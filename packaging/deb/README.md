# CIEL SOT Agent — Linux Mint / Debian package

This directory contains the Debian package structure for installing
**CIEL SOT Agent** on Linux Mint 21+ and Ubuntu 22.04+.

The package installs the application into an isolated Python virtual
environment at `/opt/ciel-sot-agent/venv` using pre-bundled wheels.
**No internet access is required during installation.**

The `.deb` is architecture-specific (`amd64`, `arm64`, etc.) because
it bundles binary wheels (e.g. numpy). Build the package on the same
architecture as the target machine.

---

## Prerequisites

### Build machine (where you run `build_deb.sh`)

| Tool | Install |
|------|---------|
| `dpkg-deb` | pre-installed on all Debian/Ubuntu/Mint systems |
| `python3` ≥ 3.11 | `sudo apt install python3` |
| `pip` | `python3 -m ensurepip --upgrade` |

### Target machine (where you install the `.deb`)

| Tool | Install |
|------|---------|
| `python3` ≥ 3.11 | `sudo apt install python3` |
| `python3-venv` | `sudo apt install python3-venv` |

---

## Building the `.deb` package

```bash
# from the repository root
bash packaging/deb/build_deb.sh
```

The script:
1. Detects the host architecture via `dpkg --print-architecture`.
2. Builds the `ciel-sot-agent` wheel from source.
3. Downloads all runtime + GUI dependency wheels (binary-only, pinned via
   `constraints.txt`) into the staging area.
4. Produces `dist/ciel-sot-agent_<version>_<arch>.deb`.

### Reproducible builds

Dependency versions are pinned in `constraints.txt`. To update the pins:

```bash
# Create a fresh venv and install
python3 -m venv /tmp/ciel-pin && /tmp/ciel-pin/bin/pip install 'ciel-sot-agent[gui]'
/tmp/ciel-pin/bin/pip freeze > packaging/deb/constraints.txt
rm -rf /tmp/ciel-pin
```

The build enforces `--only-binary :all:` so no source packages are
compiled during the build — every wheel must be pre-built.

---

## Installing on Linux Mint

```bash
# 1. Build the package
bash packaging/deb/build_deb.sh

# 2. Install
sudo dpkg -i dist/ciel-sot-agent_*.deb

# 3. Fix any missing system dependencies (if needed)
sudo apt install -f
```

The `postinst` script will:
- create `/opt/ciel-sot-agent/venv` (isolated Python virtual environment),
- install the application from the pre-bundled wheels (offline, no pip download),
- create `/var/lib/ciel/models/` for GGUF model storage,
- reload the systemd daemon.

---

## Configuration

The default configuration lives at `/etc/ciel-sot-agent/config.yaml` and is
registered as a Debian **conffile** — `dpkg` will preserve your edits across
upgrades and prompt if the upstream default changes.

```yaml
gui:
  host: "127.0.0.1"
  port: 5050

models:
  dir: "/var/lib/ciel/models"

logging:
  level: "INFO"
```

The systemd unit exports `CIEL_SOT_CONFIG=/etc/ciel-sot-agent/config.yaml`
so the application can locate it at runtime.

---

## Running the GUI

```bash
# Launch the Flask Quiet Orbital Control web interface directly:
ciel-sot-gui

# Or enable and start the systemd service (auto-start on boot):
sudo systemctl enable --now ciel-sot-gui

# Check service status:
systemctl status ciel-sot-gui

# View logs:
journalctl -u ciel-sot-gui -f
```

The GUI is served on `http://127.0.0.1:5050` by default.

---

## Managing GGUF models

```bash
# List available models
ciel-sot-install-model --list

# Download a model
ciel-sot-install-model --model tinyllama-1.1b-chat-q4
```

GGUF model files are stored in `/var/lib/ciel/models/`.

---

## Uninstalling

```bash
# Remove the package (keeps /var/lib/ciel/models/ and config intact)
sudo dpkg -r ciel-sot-agent

# Purge: also remove the virtual environment and config
sudo dpkg -P ciel-sot-agent
```

The `prerm` script stops and disables the systemd service before removal.
The `postrm` script removes the virtual environment (`/opt/ciel-sot-agent/venv`)
and reloads systemd when the package is removed or purged.

---

## Package structure

```
packaging/deb/
├── build_deb.sh                              build helper script
├── constraints.txt                           pinned dependency versions
├── DEBIAN/
│   ├── conffiles                             dpkg conffile registry
│   ├── control                               package metadata (arch template)
│   ├── postinst                              post-install: create venv, install wheels
│   ├── prerm                                 pre-remove: stop + disable service
│   └── postrm                                post-remove: clean venv, daemon-reload
├── etc/
│   └── ciel-sot-agent/
│       └── config.yaml                       default configuration (conffile)
├── opt/
│   └── ciel-sot-agent/
│       └── wheels/                           bundled wheels (populated by build_deb.sh)
├── usr/
│   ├── bin/
│   │   ├── ciel-sot-gui                      GUI launcher (wraps venv binary)
│   │   └── ciel-sot-install-model            model installer CLI (wraps venv binary)
│   └── lib/systemd/system/
│       └── ciel-sot-gui.service              systemd unit file
└── var/
    └── lib/
        └── ciel/
            └── models/                       runtime GGUF model storage directory
```

### Installation layout on the target system

| Path | Contents |
|------|----------|
| `/etc/ciel-sot-agent/config.yaml` | Configuration (conffile, survives upgrades) |
| `/opt/ciel-sot-agent/wheels/` | Pre-bundled Python wheels (read-only) |
| `/opt/ciel-sot-agent/venv/` | Isolated venv created by `postinst` |
| `/usr/bin/ciel-sot-gui` | Shell wrapper → venv binary |
| `/usr/bin/ciel-sot-install-model` | Shell wrapper → venv binary |
| `/usr/lib/systemd/system/ciel-sot-gui.service` | systemd unit |
| `/var/lib/ciel/models/` | GGUF model storage (preserved on remove) |

---

## Changing the default port or host

Edit `/etc/ciel-sot-agent/config.yaml`:

```yaml
gui:
  host: "0.0.0.0"
  port: 8080
```

Then restart the service:

```bash
sudo systemctl restart ciel-sot-gui
```

