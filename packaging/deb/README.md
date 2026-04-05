# CIEL SOT Agent — Linux Mint / Debian package

This directory contains the Debian package structure for installing
**CIEL SOT Agent** on Linux Mint 21+ and Ubuntu 22.04+.

---

## Prerequisites

| Tool | Install |
|------|---------|
| `dpkg-deb` | pre-installed on all Debian/Ubuntu/Mint systems |
| `python3` ≥ 3.11 | `sudo apt install python3` |
| `pip3` | `sudo apt install python3-pip` |

---

## Building the `.deb` package

Run the helper script from the repository root (or from this directory):

```bash
# from the repository root
bash packaging/deb/build_deb.sh
```

The script produces `dist/ciel-sot-agent_<version>_all.deb`.

---

## Installing on Linux Mint

```bash
# 1. Build the package
bash packaging/deb/build_deb.sh

# 2. Install
sudo dpkg -i dist/ciel-sot-agent_*.deb

# 3. Fix any missing dependencies (if needed)
sudo apt install -f
```

The `postinst` script will:
- install the Python package via `pip3`,
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

## Uninstalling

```bash
sudo dpkg -r ciel-sot-agent
```

The `prerm` script stops and disables the systemd service before removal.

---

## Package structure

```
packaging/deb/
├── build_deb.sh                         build helper script
├── DEBIAN/
│   ├── control                          package metadata
│   ├── postinst                         post-install hook (pip install + systemd reload)
│   └── prerm                            pre-removal hook (stop + disable service)
└── usr/
    ├── bin/
    │   └── ciel-sot-gui                 launcher wrapper
    └── lib/systemd/system/
        └── ciel-sot-gui.service         systemd unit file
```

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
