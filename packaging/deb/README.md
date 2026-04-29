# CIEL SOT Agent Debian Package

This package is designed for offline installation after the `.deb` has been built.
No internet access is required to install the package itself; model download is a separate step handled by `ciel-sot-install-model`.

## Prerequisites

- Debian, Ubuntu, or Linux Mint with `dpkg` and `apt`
- systemd available for the GUI service
- enough disk space for the venv and optional models under `/var/lib/ciel/models`

## Building

Build the package from this repository with:

```bash
cd packaging/deb
bash build_deb.sh
```

## Installing on Linux Mint

```bash
sudo dpkg -i ciel-sot-agent_*.deb
sudo apt install -f
```

The `apt install -f` step resolves any missing system dependencies after the package is unpacked.
The package `postinst` script creates the runtime environment and installs the bundled wheels.

## Configuration

The main configuration file is:

```text
/etc/ciel-sot-agent/config.yaml
```

The default GUI port is `5050`.
The runtime model directory is:

```text
/var/lib/ciel/models
```

## Running the GUI

After installation, start or restart the systemd service:

```bash
sudo systemctl restart ciel-sot-gui.service
sudo systemctl status ciel-sot-gui.service
```

You can install a model later with:

```bash
ciel-sot-install-model
```

## Package structure

```text
packaging/deb/
├── DEBIAN/
│   ├── control
│   ├── postinst
│   ├── prerm
│   └── postrm
├── etc/
│   └── ciel-sot-agent/
│       └── config.yaml
├── opt/
│   └── ciel-sot-agent/
│       └── wheels/
├── usr/
│   ├── bin/
│   │   ├── ciel-sot-gui
│   │   └── ciel-sot-install-model
│   └── lib/systemd/system/
│       └── ciel-sot-gui.service
└── var/
    └── lib/ciel/models/
```

## Uninstalling

Remove the package but keep configuration data:

```bash
sudo dpkg -r ciel-sot-agent
```

Purge package and configuration files:

```bash
sudo dpkg -P ciel-sot-agent
```
