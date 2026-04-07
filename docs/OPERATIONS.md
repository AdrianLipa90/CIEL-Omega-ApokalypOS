# Operations

## Purpose

This document makes the repository's operational layer explicit.

The architecture and scientific notes already describe conceptual and semantic layers.
This file describes the execution surfaces that actually run, validate, package, and refresh the repository state.

Primary operational surfaces:
- `scripts/`
- `tools/core_only/`
- `.github/workflows/`
- `packaging/`

## Execution surfaces

### `scripts/`
Thin repo-local launcher layer.

Current wrappers include:
- `scripts/run_gh_repo_coupling.py`
- `scripts/run_gh_repo_coupling_v2.py`
- `scripts/run_index_validator_v2.py`
- `scripts/run_orbital_bridge.py`
- `scripts/run_orbital_global_pass.py`
- `scripts/run_repo_phase_sync.py`
- `scripts/run_repo_sync_v2.py`
- `scripts/run_sapiens_panel.py`

Important clarification:
there is no `scripts/run_sapiens_client.py`.
The real Sapiens client surfaces are:
- module: `src/ciel_sot_agent/sapiens_client.py`
- installed console script: `ciel-sot-sapiens-client`

Role of `scripts/`:
- provide legible local wrappers,
- keep execution paths visible to operators,
- delegate core logic into `src/ciel_sot_agent/`.

### `tools/core_only/`
Core-only maintenance and smoke-test layer.

This is the correct location for the core-only bootstrap/test helpers.
It should be documented explicitly because earlier docs incorrectly pointed some of these paths into `scripts/`.

Representative surfaces:
- `tools/core_only/bootstrap_core_only.sh`
- `tools/core_only/run_core_smoke.sh`
- `tools/core_only/run_repo_tests.sh`

### Installed console scripts
The installable package surface is defined by `pyproject.toml`.

Representative console entrypoints:
- `ciel-sot-sync`
- `ciel-sot-sync-v2`
- `ciel-sot-gh-coupling`
- `ciel-sot-gh-coupling-v2`
- `ciel-sot-index-validate`
- `ciel-sot-index-validate-v2`
- `ciel-sot-orbital-bridge`
- `ciel-sot-ciel-pipeline`
- `ciel-sot-sapiens-client`
- `ciel-sot-runtime-evidence-ingest`
- `ciel-sot-gui`
- `ciel-sot-install-model`

### `.github/workflows/`
Executable workflow layer.

Current workflow surfaces:
- `.github/workflows/ci.yml` — lint and pytest quality gate.
- `.github/workflows/runtime_pipeline.yml` — editable-install smoke path, wheel build, wheel reinstall, runtime probe path.
- `.github/workflows/package.yml` — Debian and Android packaging build path.
- `.github/workflows/gh_repo_coupling.yml` — scheduled/manual live GH coupling refresh path.

### `packaging/`
Packaging and distribution layer.

Current documented sub-surfaces:
- `packaging/deb/` — Debian packaging layout, metadata, wrappers, service files.
- `packaging/android/` — Android companion packaging surface and buildozer path.

## Operational chains

### GH coupling chain
1. `.github/workflows/gh_repo_coupling.yml`
2. `scripts/run_gh_repo_coupling.py` or `scripts/run_gh_repo_coupling_v2.py`
3. `src/ciel_sot_agent/gh_coupling.py`
4. updated files in `integration/`

### Runtime validation chain
1. `.github/workflows/runtime_pipeline.yml`
2. installed console scripts and selected repo-local wrappers
3. runtime reports under `integration/reports/`

### Packaging chain
1. `.github/workflows/package.yml`
2. `packaging/deb/` and `packaging/android/`
3. produced package artifacts

## Documentation rule

Whenever a new automation path is added, removed, or substantially repurposed, its layers should be visible in all of the following places when relevant:
- local folder documentation,
- `docs/INDEX.md`,
- this file,
- machine-readable registry or report if it writes tracked state.

## Status note

This document closes a specific class of stale operational claims:
- underdocumented workflow coverage,
- stale core-only script paths,
- stale Sapiens client wrapper references,
- and missing separation between repo-local wrappers, installed entrypoints, and workflow automation.
