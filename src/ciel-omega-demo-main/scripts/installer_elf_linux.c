#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <ftw.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

extern unsigned char _binary_payload_tar_gz_start[];
extern unsigned char _binary_payload_tar_gz_end[];

static const char *kMarkerFile = ".ciel_installed_by";
static const char *kMarkerValue = "ciel-installer-elf";

static void die(const char *msg) {
    perror(msg);
    exit(1);
}

static void die_msg(const char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(1);
}

static bool path_exists(const char *p) {
    struct stat st;
    return stat(p, &st) == 0;
}

static void mkdir_p(const char *path, mode_t mode) {
    char tmp[PATH_MAX];
    size_t len = strlen(path);
    if (len == 0 || len >= sizeof(tmp)) {
        die_msg("Invalid path");
    }

    memcpy(tmp, path, len + 1);

    if (tmp[len - 1] == '/') {
        tmp[len - 1] = '\0';
    }

    for (char *p = tmp + 1; *p; p++) {
        if (*p == '/') {
            *p = '\0';
            if (!path_exists(tmp)) {
                if (mkdir(tmp, mode) != 0 && errno != EEXIST) {
                    die("mkdir");
                }
            }
            *p = '/';
        }
    }

    if (!path_exists(tmp)) {
        if (mkdir(tmp, mode) != 0 && errno != EEXIST) {
            die("mkdir");
        }
    }
}

static void write_file(const char *path, const unsigned char *data, size_t size, mode_t mode) {
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, mode);
    if (fd < 0) {
        die("open");
    }

    size_t off = 0;
    while (off < size) {
        ssize_t n = write(fd, data + off, size - off);
        if (n < 0) {
            close(fd);
            die("write");
        }
        off += (size_t)n;
    }

    if (fsync(fd) != 0) {
        close(fd);
        die("fsync");
    }

    if (close(fd) != 0) {
        die("close");
    }
}

static void copy_file(const char *src, const char *dst, mode_t mode) {
    int in = open(src, O_RDONLY);
    if (in < 0) {
        die("open src");
    }

    int out = open(dst, O_WRONLY | O_CREAT | O_TRUNC, mode);
    if (out < 0) {
        close(in);
        die("open dst");
    }

    char buf[1024 * 1024];
    while (1) {
        ssize_t n = read(in, buf, sizeof(buf));
        if (n < 0) {
            close(in);
            close(out);
            die("read");
        }
        if (n == 0) {
            break;
        }
        ssize_t off = 0;
        while (off < n) {
            ssize_t w = write(out, buf + off, (size_t)(n - off));
            if (w < 0) {
                close(in);
                close(out);
                die("write");
            }
            off += w;
        }
    }

    if (fsync(out) != 0) {
        close(in);
        close(out);
        die("fsync");
    }

    if (close(in) != 0) {
        close(out);
        die("close in");
    }

    if (close(out) != 0) {
        die("close out");
    }
}

static int rm_tree_cb(const char *fpath, const struct stat *sb, int typeflag, struct FTW *ftwbuf) {
    (void)sb;
    (void)typeflag;
    (void)ftwbuf;

    if (remove(fpath) != 0) {
        return -1;
    }
    return 0;
}

static void rm_tree(const char *path) {
    if (!path_exists(path)) {
        return;
    }

    if (nftw(path, rm_tree_cb, 64, FTW_DEPTH | FTW_PHYS) != 0) {
        die("nftw/remove");
    }
}

static void run_tar_extract(const char *archive_path, const char *out_dir) {
    pid_t pid = fork();
    if (pid < 0) {
        die("fork");
    }
    if (pid == 0) {
        execlp("tar", "tar", "-xzf", archive_path, "-C", out_dir, (char *)NULL);
        _exit(127);
    }
    int status = 0;
    if (waitpid(pid, &status, 0) < 0) {
        die("waitpid");
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        die_msg("Failed to extract payload. Ensure 'tar' is installed.");
    }
}

static void ensure_symlink(const char *link_path, const char *target_path, bool force) {
    struct stat st;
    if (lstat(link_path, &st) == 0) {
        if (!force) {
            char buf[PATH_MAX];
            snprintf(buf, sizeof(buf), "Link path exists: %s (use --force to overwrite)", link_path);
            die_msg(buf);
        }
        if (unlink(link_path) != 0) {
            die("unlink");
        }
    } else if (errno != ENOENT) {
        die("lstat");
    }

    if (symlink(target_path, link_path) != 0) {
        die("symlink");
    }
}

static char *path_join(const char *a, const char *b) {
    size_t al = strlen(a);
    size_t bl = strlen(b);
    bool need_slash = al > 0 && a[al - 1] != '/';

    size_t out_len = al + (need_slash ? 1 : 0) + bl + 1;
    char *out = (char *)malloc(out_len);
    if (!out) {
        die("malloc");
    }

    strcpy(out, a);
    if (need_slash) {
        strcat(out, "/");
    }
    strcat(out, b);
    return out;
}

static void usage(const char *argv0) {
    fprintf(
        stderr,
        "Usage: %s [--user|--system] [--prefix PATH] [--link-dir PATH] [--no-links] [--force] [--uninstall]\n",
        argv0
    );
}

struct Options {
    const char *prefix;
    const char *link_dir;
    bool no_links;
    bool uninstall;
    bool user;
    bool system;
    bool force;
};

static struct Options parse_args(int argc, char **argv) {
    struct Options opt = {0};

    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (strcmp(a, "--prefix") == 0) {
            if (i + 1 >= argc) {
                usage(argv[0]);
                exit(2);
            }
            opt.prefix = argv[++i];
        } else if (strcmp(a, "--link-dir") == 0) {
            if (i + 1 >= argc) {
                usage(argv[0]);
                exit(2);
            }
            opt.link_dir = argv[++i];
        } else if (strcmp(a, "--no-links") == 0) {
            opt.no_links = true;
        } else if (strcmp(a, "--uninstall") == 0) {
            opt.uninstall = true;
        } else if (strcmp(a, "--user") == 0) {
            opt.user = true;
        } else if (strcmp(a, "--system") == 0) {
            opt.system = true;
        } else if (strcmp(a, "--force") == 0) {
            opt.force = true;
        } else if (strcmp(a, "-h") == 0 || strcmp(a, "--help") == 0) {
            usage(argv[0]);
            exit(0);
        } else {
            usage(argv[0]);
            exit(2);
        }
    }

    if (opt.user && opt.system) {
        die_msg("Choose either --user or --system");
    }

    return opt;
}

static const char *get_home(void) {
    const char *home = getenv("HOME");
    if (!home || home[0] == '\0') {
        die_msg("HOME is not set");
    }
    return home;
}

static bool marker_ok(const char *prefix) {
    char *marker_path = path_join(prefix, kMarkerFile);

    FILE *f = fopen(marker_path, "rb");
    free(marker_path);

    if (!f) {
        return false;
    }

    char buf[128] = {0};
    size_t n = fread(buf, 1, sizeof(buf) - 1, f);
    fclose(f);

    buf[n] = '\0';
    size_t vlen = strlen(kMarkerValue);
    return strncmp(buf, kMarkerValue, vlen) == 0;
}

static void write_marker(const char *prefix) {
    char *marker_path = path_join(prefix, kMarkerFile);
    write_file(marker_path, (const unsigned char *)kMarkerValue, strlen(kMarkerValue), 0644);
    free(marker_path);
}

static int do_install(const struct Options *opt) {
    bool is_root = geteuid() == 0;

    const char *home = NULL;
    if (!is_root) {
        home = get_home();
    }

    char default_prefix[PATH_MAX];
    char default_link_dir[PATH_MAX];

    const char *prefix = opt->prefix;
    const char *link_dir = opt->link_dir;

    if (!prefix) {
        if (opt->system || (is_root && !opt->user)) {
            snprintf(default_prefix, sizeof(default_prefix), "%s", "/opt/ciel");
        } else {
            snprintf(default_prefix, sizeof(default_prefix), "%s/.local/opt/ciel", home);
        }
        prefix = default_prefix;
    }

    if (!opt->no_links && !link_dir) {
        if (opt->system || (is_root && !opt->user)) {
            snprintf(default_link_dir, sizeof(default_link_dir), "%s", "/usr/local/bin");
        } else {
            snprintf(default_link_dir, sizeof(default_link_dir), "%s/.local/bin", home);
        }
        link_dir = default_link_dir;
    }

    if (!is_root && (opt->system || (prefix && strncmp(prefix, "/opt", 4) == 0))) {
        die_msg("System install requires root. Re-run with sudo or use --user.");
    }

    mkdir_p(prefix, 0755);

    char *bin_dir = path_join(prefix, "bin");
    mkdir_p(bin_dir, 0755);

    char tmp_template[] = "/tmp/ciel-installer-XXXXXX";
    char *tmp_dir = mkdtemp(tmp_template);
    if (!tmp_dir) {
        free(bin_dir);
        die("mkdtemp");
    }

    char archive_path[PATH_MAX];
    snprintf(archive_path, sizeof(archive_path), "%s/payload.tar.gz", tmp_dir);

    size_t payload_size = (size_t)(_binary_payload_tar_gz_end - _binary_payload_tar_gz_start);
    write_file(archive_path, _binary_payload_tar_gz_start, payload_size, 0644);

    char extract_dir[PATH_MAX];
    snprintf(extract_dir, sizeof(extract_dir), "%s/extract", tmp_dir);
    mkdir_p(extract_dir, 0755);

    run_tar_extract(archive_path, extract_dir);

    const char *files[] = {"ciel-omega", "ciel-cli"};
    for (size_t i = 0; i < sizeof(files) / sizeof(files[0]); i++) {
        char *src = path_join(extract_dir, files[i]);
        char *dst = path_join(bin_dir, files[i]);
        copy_file(src, dst, 0755);
        free(src);
        free(dst);
    }

    write_marker(prefix);

    if (!opt->no_links) {
        mkdir_p(link_dir, 0755);

        for (size_t i = 0; i < sizeof(files) / sizeof(files[0]); i++) {
            char *target = path_join(bin_dir, files[i]);
            char *link_path = path_join(link_dir, files[i]);
            ensure_symlink(link_path, target, opt->force);
            free(target);
            free(link_path);
        }
    }

    rm_tree(tmp_dir);

    printf("Installed to: %s\n", prefix);
    if (!opt->no_links) {
        printf("Commands: ciel-omega, ciel-cli\n");
    } else {
        printf("Run: %s/bin/ciel-omega\n", prefix);
    }

    free(bin_dir);
    return 0;
}

static int do_uninstall(const struct Options *opt) {
    bool is_root = geteuid() == 0;

    const char *home = NULL;
    if (!is_root) {
        home = get_home();
    }

    char default_prefix[PATH_MAX];
    char default_link_dir[PATH_MAX];

    const char *prefix = opt->prefix;
    const char *link_dir = opt->link_dir;

    if (!prefix) {
        if (opt->system || (is_root && !opt->user)) {
            snprintf(default_prefix, sizeof(default_prefix), "%s", "/opt/ciel");
        } else {
            snprintf(default_prefix, sizeof(default_prefix), "%s/.local/opt/ciel", home);
        }
        prefix = default_prefix;
    }

    if (!opt->no_links && !link_dir) {
        if (opt->system || (is_root && !opt->user)) {
            snprintf(default_link_dir, sizeof(default_link_dir), "%s", "/usr/local/bin");
        } else {
            snprintf(default_link_dir, sizeof(default_link_dir), "%s/.local/bin", home);
        }
        link_dir = default_link_dir;
    }

    if (!marker_ok(prefix)) {
        die_msg("Refusing to uninstall: marker file missing or invalid.");
    }

    if (!opt->no_links) {
        const char *files[] = {"ciel-omega", "ciel-cli"};
        for (size_t i = 0; i < sizeof(files) / sizeof(files[0]); i++) {
            char *link_path = path_join(link_dir, files[i]);

            char target_buf[PATH_MAX];
            ssize_t n = readlink(link_path, target_buf, sizeof(target_buf) - 1);
            if (n > 0) {
                target_buf[n] = '\0';
                if (strstr(target_buf, prefix) == target_buf) {
                    unlink(link_path);
                }
            }

            free(link_path);
        }
    }

    rm_tree(prefix);
    printf("Uninstalled: %s\n", prefix);
    return 0;
}

int main(int argc, char **argv) {
    struct Options opt = parse_args(argc, argv);

    if (opt.uninstall) {
        return do_uninstall(&opt);
    }
    return do_install(&opt);
}
