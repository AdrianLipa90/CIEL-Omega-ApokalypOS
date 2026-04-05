# CIEL SOT Agent — Linux Mint / Debian package

This directory contains the Debian package structure for installing
**CIEL SOT Agent** on Linux Mint 21+ and Ubuntu 22.04+.

The package installs the application into an isolated Python virtual
environment at `/opt/ciel-sot-agent/venv` using pre-bundled wheels.
**No internet access is required during installation.**

---

## Prerequisites

| Tool | Install |
|------|---------|
| `dpkg-deb` | pre-installed on all Debian/Ubuntu/Mint systems |
| `python3` ≥ 3.11 | `sudo apt install python3` |
| `python3-venv` | `sudo apt install python3-venv` *(runtime dep, needed on target)* |
| `pip` | `python3 -m ensurepip --upgrade` *(build-time only, needed on build machine)* |

---

## Building the `.deb` package

Run the helper script from the repository root (or from this directory):

```bash
# from the repository root
bash packaging/deb/build_deb.sh
```

The script:
1. Builds the `ciel-sot-agent` wheel from source.
2. Downloads all runtime + GUI dependency wheels into the staging area
   so the resulting package is fully self-contained.
3. Produces `dist/ciel-sot-agent_<version>_all.deb`.

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
# Remove the package (keeps /var/lib/ciel/models/ intact)
sudo dpkg -r ciel-sot-agent

# Purge: also remove the virtual environment
sudo dpkg -P ciel-sot-agent
```

The `prerm` script stops and disables the systemd service before removal.
The `postrm` script removes the virtual environment (`/opt/ciel-sot-agent/venv`)
when the package is purged.

---

## Package structure

```
packaging/deb/
├── build_deb.sh                              build helper script
├── DEBIAN/
│   ├── control                               package metadata
│   ├── postinst                              post-install: create venv, install wheels
│   ├── prerm                                 pre-remove: stop + disable service
│   └── postrm                                post-remove: clean up venv on purge
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
| `/opt/ciel-sot-agent/wheels/` | Pre-bundled Python wheels (read-only) |
| `/opt/ciel-sot-agent/venv/` | Isolated venv created by `postinst` |
| `/usr/bin/ciel-sot-gui` | Shell wrapper → venv binary |
| `/usr/bin/ciel-sot-install-model` | Shell wrapper → venv binary |
| `/usr/lib/systemd/system/ciel-sot-gui.service` | systemd unit |
| `/var/lib/ciel/models/` | GGUF model storage (preserved on remove) |

---

## Changing the default port or host

Edit `/usr/lib/systemd/system/ciel-sot-gui.service`, update the `ExecStart` line:

```ini
ExecStart=/usr/bin/ciel-sot-gui --host 0.0.0.0 --port 8080
```

Then reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ciel-sot-gui
```

