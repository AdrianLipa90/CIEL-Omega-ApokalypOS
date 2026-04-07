# CIEL SOT Agent — Packaging Surfaces

This folder contains multiple packaging and installation surfaces.

They should not be treated as one identical installer path, because they differ in:
- where dependencies come from,
- whether installation is online or offline,
- whether GGUF model download is automatic or explicit,
- and whether the result is a local dev install, a system package, or a CI-built artifact.

## Packaging surfaces

### 1. Scripted installers (`install.sh`, `install.ps1`, `install.bat`)
These are convenience installers for Linux/macOS and Windows.

They:
1. install `ciel-sot-agent[gui]`,
2. try to install `llama-cpp-python` unless explicitly skipped,
3. optionally download a GGUF model unless the selected model is `none`.

Important detail:
- these installers may run in **online mode** (PyPI) or **offline mode** if a local `packaging/vendor/` wheel cache exists,
- model download is part of the script flow unless explicitly skipped,
- `llama-cpp-python` installation is optional and may fail without aborting the whole install.

### 2. Debian package (`packaging/deb/`)
This is a distinct installation surface.

The Debian package:
- bundles wheels at build time,
- installs the application into `/opt/ciel-sot-agent/venv`,
- installs from pre-bundled wheels during `postinst`,
- does **not** automatically download a GGUF model during package installation.

So the `.deb` is best described as:
- **offline application/package install**,
- with **explicit post-install model management** via `ciel-sot-install-model`.

### 3. Android packaging (`packaging/android/`)
This is the Android build surface used by CI and local Buildozer flows.

It should be treated as:
- a build artifact path,
- not as proof of validated end-user runtime behavior on arbitrary devices.

## Quick install

### Linux / macOS scripted installer
```bash
# Default model: TinyLlama
bash <(curl -fsSL https://raw.githubusercontent.com/AdrianLipa90/CIEL-_SOT_Agent/main/packaging/install.sh)

# Qwen 2.5 0.5B
CIEL_MODEL=qwen2.5-0.5b-q4 bash <(curl -fsSL https://raw.githubusercontent.com/AdrianLipa90/CIEL-_SOT_Agent/main/packaging/install.sh)

# Skip model download
CIEL_MODEL=none bash <(curl -fsSL https://raw.githubusercontent.com/AdrianLipa90/CIEL-_SOT_Agent/main/packaging/install.sh)
```

Or run locally from the repository root:
```bash
bash packaging/install.sh
```

### Windows scripted installer
```powershell
# Default model
.\packaging\install.ps1

# Qwen 2.5 0.5B
.\packaging\install.ps1 -Model qwen2.5-0.5b-q4

# Skip model download
.\packaging\install.ps1 -Model none
```

### Debian / Ubuntu / Mint `.deb`
```bash
# Build
bash packaging/deb/build_deb.sh

# Install the package
sudo dpkg -i dist/ciel-sot-agent_*.deb

# Fix missing system dependencies if needed
sudo apt install -f

# Download a model explicitly after install
ciel-sot-install-model --model tinyllama-1.1b-chat-q4
```

## Available models for scripted installers / explicit post-install model management

| Key | Model | Size | Notes |
|-----|-------|------|-------|
| `tinyllama-1.1b-chat-q4` | TinyLlama 1.1B Chat Q4_K_M | ~670 MB | Default scripted-installer model |
| `qwen2.5-0.5b-q4` | Qwen 2.5 0.5B Instruct Q4_K_M | ~397 MB | Smallest Qwen |
| `qwen2.5-1.5b-q4` | Qwen 2.5 1.5B Instruct Q4_K_M | ~986 MB | Balanced Qwen |
| `phi-2-q4` | Microsoft Phi-2 Q4_K_M | ~1.6 GB | |
| `none` | — | — | Skip scripted-installer download |

## Manual model management

After installation, use the `ciel-sot-install-model` CLI tool:

```bash
ciel-sot-install-model --list
ciel-sot-install-model --model qwen2.5-0.5b-q4
ciel-sot-install-model --model tinyllama-1.1b-chat-q4 --models-dir /data/models
```

Default model locations:
- Linux/macOS: `~/.local/share/ciel/models/`
- Windows: `%LOCALAPPDATA%\ciel\models`
- Debian package default runtime path: `/var/lib/ciel/models/`
- override path: `CIEL_MODELS_DIR`

## CI packaging path

The packaging workflow surface is:
- `.github/workflows/package.yml`

It currently builds:
- Debian package artifacts,
- Android APK artifacts.

This should be read as build coverage, not as universal runtime certification.

## Contents

```text
packaging/
├── install.sh        Linux/macOS scripted installer
├── install.ps1       Windows PowerShell scripted installer
├── install.bat       Windows batch launcher for install.ps1
├── README.md         This file
└── deb/
    ├── build_deb.sh  Build the .deb package
    ├── README.md     Debian/Ubuntu/Mint packaging guide
    └── ...
```
