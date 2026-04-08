# Installers

This folder contains the installation surfaces for `ciel-sot-agent`.
Every supported installer follows the same three-step model:

1. install `ciel-sot-agent`,
2. install `llama-cpp-python`,
3. optionally download a GGUF model.

## Quick install

### Linux / macOS
```bash
bash packaging/install.sh --model tinyllama-1.1b-chat-v1.0-q4
```

### Windows
```powershell
.\packaging\install.ps1 -Model none
```

### Debian package (`.deb`)
Build or obtain the package, install it, then use `ciel-sot-install-model` when you want a local model.
See `packaging/deb/README.md` for the Debian and Linux Mint path.

## Available models

| Key | Notes |
|---|---|
| `tinyllama-1.1b-chat-v1.0-q4` | Default TinyLlama option |
| `qwen2.5-0.5b-q4` | Small Qwen model |
| `qwen2.5-1.5b-q4` | Larger Qwen model |
| `phi-2-q4` | Phi-2 quantized option |
| `none` | Skip model download during install |

## Model storage

By default models are stored under `~/.local/share/ciel/models`.
Override the location with the `CIEL_MODELS_DIR` environment variable.

## Manual model management

Use `ciel-sot-install-model` after installation to download or switch models without reinstalling the application.
This is useful when you initially chose `none` or when you want to redirect downloads to `CIEL_MODELS_DIR`.

## Contents

- `install.sh` — Bash installer for Linux and macOS.
- `install.ps1` — PowerShell installer for Windows.
- `install.bat` — cmd wrapper for Windows.
- `deb/` — Debian and Linux Mint packaging path.
- `android/` — Android build surface.
