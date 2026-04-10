# CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold — Human Repository Guide

## What this repository actually is

`CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` is not one single app and it is not only one Python package.

It is a mixed repository that contains:
1. native integration code under `src/ciel_sot_agent/`,
2. machine-readable integration state under `integration/`,
3. execution surfaces under `scripts/`, `tools/core_only/`, `.github/workflows/`, and `packaging/`,
4. embedded/imported source snapshots that support integration, audit, bridge work, and documentation.

The most important navigation rule is:

> first decide whether you are looking at native integration code, integration state, operations, or an embedded snapshot.

If that distinction is missed, the repo looks larger and more inconsistent than it actually is.

## Layer 1 — Native package you can install

Path: `src/ciel_sot_agent/`

This is the real installable core of the repository. It contains the code exposed by `pyproject.toml`, including synchronization, GH coupling, index validation, orbital bridge, CIEL pipeline adapter, Sapiens client and panel state assembly, runtime evidence ingest, Flask GUI, and GGUF model manager.

## Layer 2 — Integration state and machine-readable artifacts

Path: `integration/`

This sector stores the files that native code reads or writes: registries, coupling maps, hyperspace indices, reports, imported upstream maps, and migration-era duplicates plus target-geometry copies.

Important detail: the repo is in a transitional geometry. Some files coexist in:
- legacy flat paths such as `integration/index_registry.yaml`, and
- target paths such as `integration/registries/index_registry_v2.yaml`.

This is deliberate and must be documented clearly to avoid false bug reports.

## Layer 3 — Operational surfaces

Relevant paths:
- `scripts/`
- `tools/core_only/`
- `.github/workflows/`
- `packaging/`

These paths tell you how the repo is actually run, validated, and shipped.

Three distinct execution modes exist:
1. repo-local thin wrappers,
2. installed console scripts from `pyproject.toml`,
3. GitHub Actions and packaging automation.

## Layer 4 — Embedded or imported subprojects

Relevant paths include:
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/`
- `src/CIEL_RELATIONAL_MECHANISM_REPO/`
- `src/ciel-omega-demo-main/`
- `src/CIEL_Orbital_Foundation_Packk/`
- `src/ciel_rh_control_mini_repo/`
- `integration/Orbital/main/`

These are not all part of the installable package surface. They are present because the repo also acts as an integration attractor, an import review workspace, a bridge layer, and a documentation/audit host.

## Executable surface

Installed console scripts include:
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

Repo-local wrappers include:
- `run_gh_repo_coupling.py`
- `run_gh_repo_coupling_v2.py`
- `run_index_validator_v2.py`
- `run_orbital_bridge.py`
- `run_orbital_global_pass.py`
- `run_repo_phase_sync.py`
- `run_repo_sync_v2.py`
- `run_sapiens_panel.py`

Important clarification:
there is no local `scripts/run_sapiens_client.py`.
The packet client exists as module `src/ciel_sot_agent/sapiens_client.py` and console script `ciel-sot-sapiens-client`.

## Packaging and workflows

Current workflows:
- `.github/workflows/ci.yml`
- `.github/workflows/runtime_pipeline.yml`
- `.github/workflows/package.yml`
- `.github/workflows/gh_repo_coupling.yml`

Debian packaging lives under `packaging/deb/`.
Android companion packaging lives under `packaging/android/`.

Android device/runtime validation remains out of scope for this documentation operation unless explicitly brought back into scope.
