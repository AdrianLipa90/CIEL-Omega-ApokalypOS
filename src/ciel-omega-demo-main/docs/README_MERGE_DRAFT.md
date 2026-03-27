# CIEL/Ω — General Quantum Consciousness System
### *README — Architectural Documentation*
A. Lipa, S. Sakpal, M. Kamecka, U. Ahmad (2025). (c) 2025 Adrian Lipa / Intention Lab

---

## Overview

**CIEL/Ω** is a local, single-user demo environment for running and testing Omega-oriented workflows.
It currently combines:

- a **legacy local runtime cockpit** built with **NiceGUI**,
- a **CLI** for experiments, kernels, and demos,
- optional **local GGUF inference** through `llama-cpp-python`,
- an **orbital cockpit preview** that reorganizes the UI around identity, layers, evidence, and publication boundary,
- a **static web preview** intended for architecture review and GitHub Pages publication.

The repository should now be read as a transition point between:

1. a practical local runtime shell,
2. a larger Omega system cockpit,
3. a documentation and publication surface for the evolving architecture.

---

## Current surfaces

### 1. Legacy runtime cockpit

The original local cockpit is still present and remains the main runtime UI for:

- GGUF model management,
- local file handling,
- kernel execution,
- observability and diagnostics,
- runtime settings.

Entry point:

- `ciel-omega` -> `main.apps.omega_app:main`

### 2. Orbital cockpit preview

A new preview surface has been added to begin the migration from a flat runtime UI to an **attractor-centered, orbit-organized cockpit**.

It introduces:

- **Identity Attractor** as the organizing center,
- orbit-based navigation,
- epistemic inspector / provenance surface,
- operational event strip,
- publication boundary as a first-class layer.

Entry point:

- `main.apps.omega_orbital_app`

Launchers:

- `scripts/run_orbital_ui.sh`
- `scripts/run_orbital_ui.ps1`
- `scripts/run_orbital_ui.cmd`

### 3. Static web preview

A static web version of the orbital cockpit preview is available for quick review and website publication.

Entry point:

- `docs/index.html`

Supporting docs:

- `docs/INDEX.md`
- `docs/OMEGA_COCKPIT_1_0.md`
- `docs/ORBITAL_PREVIEW.md`

---

## Architectural direction

The current repository is no longer only a launcher for local runtime tools.
It now contains the beginning of a larger cockpit refactor.

### From flat tabs to system layers

The legacy UI is organized as peer tabs such as:

- Dashboard
- Kernel
- Chat
- Files
- Models
- Observability
- Settings

The Omega-oriented direction replaces this with a layer-aware organization:

- **Identity Attractor**
- **Constitutive layers** (theory, operators, constants, constraints, memory topology)
- **Dynamic layers** (execution, kernel, planner, session dynamics, routing)
- **Interaction layers** (agent, chat, files, models, tools)
- **Observation layers** (evidence, observability, audit, provenance, crossrefs)
- **Boundary layers** (publication boundary, public/private separation, export manifests)

### Why this matters

The goal is not only a nicer UI.
The goal is to make the cockpit reflect:

- system hierarchy,
- formal workflow,
- epistemic status,
- provenance,
- runtime state,
- publication boundary.

In other words, the cockpit is moving from a **runtime control panel** toward a **system cockpit and epistemic instrument**.

---

## Repository structure

### Runtime code

- `main/` — Python package containing the runtime app, CLI, kernels, core utilities, and Omega-related modules

### Main application entry points

- `ciel-omega` -> `main.apps.omega_app:main`
- `ciel-cli` -> `main.apps.cli:main`

### Orbital cockpit modules

- `main/apps/omega_orbital_app.py` — orbital cockpit preview app
- `main/apps/orbital_cockpit.py` — orbital topology model
- `main/apps/orbital_panels.py` — builders for navigation, identity snapshot, and event strip

### Documentation / preview layer

- `docs/index.html` — static orbital cockpit preview
- `docs/INDEX.md` — documentation index
- `docs/OMEGA_COCKPIT_1_0.md` — cockpit architecture specification
- `docs/ORBITAL_PREVIEW.md` — launch and publication guide

### Scripts

- `scripts/install_local.*` — create local virtual environment and install dependencies
- `scripts/run_ui.*` — run the legacy runtime cockpit
- `scripts/run_cli.*` — run the CLI
- `scripts/run_orbital_ui.*` — run the orbital cockpit preview
- `scripts/build_bundle.*` — build PyInstaller bundles

---

## Requirements

- Python **>= 3.11**
- Linux: bash
- Windows: PowerShell or `.cmd`
- optional compiler / toolchain support for `llama-cpp-python` if local GGUF inference is needed

---

## Installation

### Linux

```bash
bash scripts/install_local.sh
```

### Windows

Run:

- `scripts\install_local.cmd`

or:

```powershell
scripts\install_local.ps1
```

---

## Running the project

### Legacy runtime cockpit

#### Linux

```bash
bash scripts/run_ui.sh
```

#### Windows

- `scripts\run_ui.cmd`

### Orbital cockpit preview

#### Linux

```bash
bash scripts/run_orbital_ui.sh
```

#### Windows PowerShell

```powershell
scripts\run_orbital_ui.ps1
```

#### Windows CMD

```cmd
scripts\run_orbital_ui.cmd
```

### CLI

#### Linux

```bash
bash scripts/run_cli.sh list
```

#### Windows PowerShell

```powershell
scripts\run_cli.ps1 list
```

---

## Optional GGUF backend installation

### Linux

```bash
INSTALL_LLAMA=1 bash scripts/install_local.sh
```

CUDA-capable environments may use:

```bash
INSTALL_LLAMA=1 LLAMA_BACKEND=cuda bash scripts/install_local.sh
```

### Windows

```powershell
scripts\install_local.ps1 -InstallLlama 1 -LlamaBackend cpu
```

---

## Environment variables

- `CIEL_HOST`
  - default: `127.0.0.1`
- `CIEL_PORT`
  - default legacy UI: `8080`
  - default orbital preview launchers: `8081`
- `CIEL_DATA_DIR`
  - overrides the application data directory
- `CIEL_MAX_UPLOAD_MB`
  - default: `4096`
- `CIEL_MAX_DOWNLOAD_MB`
  - default: `8192`
- `CIEL_ALLOW_PIP_INSTALL`
  - set to `1` to enable pip-install flow from the UI (disabled by default)

Example:

```bash
CIEL_PORT=9090 bash scripts/run_ui.sh
```

---

## Application data

By default, application data is stored under the user home directory:

- `~/.ciel/ciel_omega_data`
  - models: `~/.ciel/ciel_omega_data/models`
  - files: `~/.ciel/ciel_omega_data/files`
  - state: `~/.ciel/ciel_omega_data/state.json`

---

## Static web publication

The repository already contains a static preview entry page at:

- `docs/index.html`

To publish it via GitHub Pages:

1. open repository settings,
2. go to **Pages**,
3. set source to **Deploy from a branch**,
4. choose branch `main`, folder `/docs`,
5. save.

This publishes the architecture preview without requiring Python or local runtime setup.

---

## Bundles / standalone distribution

PyInstaller-based bundles remain available for the legacy runtime surface.

### Linux

```bash
PYTHON_BIN=.venv/bin/python bash scripts/build_bundle.sh
```

Outputs:

- `dist_bundle/ciel-omega`
- `dist_bundle/ciel-cli`

### Windows

```powershell
scripts\build_bundle.ps1
```

### CI / GitHub Actions

Workflow:

- `.github/workflows/build_bundles.yml`

Published artifacts:

- `ciel-bundle-windows.zip`
- `ciel-bundle-linux.tar.gz`

---

## Current status

### Stable / already present

- legacy local runtime cockpit,
- CLI entrypoints,
- local GGUF model management,
- local files and previews,
- kernel registry and runtime stepping,
- observability / diagnostics,
- orbital cockpit topology scaffold,
- orbital cockpit preview app,
- static web preview,
- documentation index and cockpit architecture specification.

### Present but not yet fully wired

- canonical object manifests,
- theory export binding,
- planner runtime UI,
- full test coverage integration,
- sanitization and dirty-manifest tracking,
- complete migration of legacy panels into orbital geometry.

---

## Documentation map

Start here depending on intent:

- runtime usage -> this README
- cockpit architecture -> `docs/OMEGA_COCKPIT_1_0.md`
- orbital preview operation -> `docs/ORBITAL_PREVIEW.md`
- documentation index -> `docs/INDEX.md`
- website preview -> `docs/index.html`

---

## Troubleshooting

- **UI does not start**
  - ensure installation completed through `scripts/install_local.*`
- **GGUF backend unavailable**
  - verify that `llama-cpp-python` is installed in the environment
- **Port already in use**
  - set `CIEL_PORT` explicitly and restart
- **Orbital preview is not the same as the legacy runtime UI**
  - this is expected; the preview is a new cockpit surface, not yet a full replacement

---

## Summary

This repository now serves three parallel roles:

1. a **working local runtime demo**,
2. a **development path toward the Omega system cockpit**,
3. a **web/documentation surface for architecture review and publication**.

The legacy runtime remains intact.
The orbital cockpit introduces the new geometry.
The static preview makes that geometry publishable.
