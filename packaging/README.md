# CIEL SOT Agent — Installers

Production-ready installers for **CIEL SOT Agent**.  Each installer:

1. Installs the Python package (`ciel-sot-agent[gui]`)
2. Installs `llama-cpp-python` (bundles the llama.cpp binary for on-device LLM inference)
3. Downloads a GGUF language model (default: TinyLlama 1.1B Chat Q4_K_M ~670 MB)

---

## Quick install

### Linux / macOS

```bash
# Default model: TinyLlama
bash <(curl -fsSL https://raw.githubusercontent.com/AdrianLipa90/CIEL-_SOT_Agent/main/packaging/install.sh)

# Qwen 2.5 0.5B (smallest, ~397 MB)
CIEL_MODEL=qwen2.5-0.5b-q4 bash <(curl -fsSL https://raw.githubusercontent.com/AdrianLipa90/CIEL-_SOT_Agent/main/packaging/install.sh)

# Qwen 2.5 1.5B (~986 MB)
CIEL_MODEL=qwen2.5-1.5b-q4 bash <(curl -fsSL https://raw.githubusercontent.com/AdrianLipa90/CIEL-_SOT_Agent/main/packaging/install.sh)
```

Or clone the repo and run locally:

```bash
bash packaging/install.sh
```

### Windows

Double-click `packaging/install.bat` — or run from PowerShell:

```powershell
# Default model
.\packaging\install.ps1

# Qwen 2.5 0.5B
.\packaging\install.ps1 -Model qwen2.5-0.5b-q4

# Skip model download
.\packaging\install.ps1 -Model none
```

### Linux Mint / Debian — `.deb` package

```bash
# Build
bash packaging/deb/build_deb.sh

# Install (default model: TinyLlama, downloaded in background)
sudo dpkg -i dist/ciel-sot-agent_*.deb

# Install with Qwen2.5-0.5B
sudo CIEL_MODEL=qwen2.5-0.5b-q4 dpkg -i dist/ciel-sot-agent_*.deb

# Follow model download progress
tail -f /var/log/ciel-model-install.log
```

---

## Available models

| Key | Model | Size | Notes |
|-----|-------|------|-------|
| `tinyllama-1.1b-chat-q4` | TinyLlama 1.1B Chat Q4_K_M | ~670 MB | **Default** |
| `qwen2.5-0.5b-q4` | Qwen 2.5 0.5B Instruct Q4_K_M | ~397 MB | Smallest Qwen |
| `qwen2.5-1.5b-q4` | Qwen 2.5 1.5B Instruct Q4_K_M | ~986 MB | Balanced Qwen |
| `phi-2-q4` | Microsoft Phi-2 Q4_K_M | ~1.6 GB | |
| `none` | — | — | Skip download |

---

## Manual model management

After install, use the `ciel-sot-install-model` CLI tool:

```bash
# List all available models
ciel-sot-install-model --list

# Download a specific model
ciel-sot-install-model --model qwen2.5-0.5b-q4

# Download to a custom directory
ciel-sot-install-model --model tinyllama-1.1b-chat-q4 --models-dir /data/models
```

Models are stored in `~/.local/share/ciel/models/` by default (Linux/macOS)
or `%LOCALAPPDATA%\ciel\models` (Windows), or in the path pointed to by the
`CIEL_MODELS_DIR` environment variable.

---

## Contents

```
packaging/
├── install.sh        Linux / macOS one-liner installer
├── install.ps1       Windows PowerShell installer
├── install.bat       Windows batch launcher for install.ps1
├── README.md         This file
└── deb/
    ├── build_deb.sh  Build the .deb package
    ├── README.md     Debian/Ubuntu/Mint packaging guide
    └── ...
```
