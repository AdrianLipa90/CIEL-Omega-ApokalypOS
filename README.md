# CIEL/Ω — Integration Attractor and Operational Manifold
### README — Integration and Repository Overview
A. Lipa, S. Sakpal, M. Kamecka, U. Ahmad (2025). (c) 2025 Adrian Lipa / Intention Lab

---

`CIEL-_SOT_Agent` is the operational manifold where repository identity, orbital diagnostics, bridge control, Sapiens interaction, packaging surfaces, and machine-readable cross-reference layers are made explicit and made to work together.

This repository is **not** best understood as one monolithic app.
It is a mixed operational repository that contains:
- a native installable package,
- machine-readable integration state,
- repo-local operational wrappers,
- workflow and packaging automation,
- and embedded/imported sectors used for bridge, audit, and compatibility work.

It does **not** replace:
- the canonical theory repository,
- the Omega demo cockpit,
- Metatime,
- or the larger mechanism workspace.

Instead, it binds them through an integration formalism based on:
- repository identity,
- semantic phase,
- weighted coupling,
- Euler-style closure defect,
- orbital coherence diagnostics,
- bridge-state reduction,
- packet-aware human-model interaction,
- machine-readable indexing,
- and multi-agent coordination on GitHub.

---

## What this repository currently is

The wider ecosystem is intentionally distributed.
Each repository or layer keeps its own role, while `CIEL-_SOT_Agent` serves as the place where those roles are related, synchronized, audited, and operationally exposed.

- **canon / Seed of the Worlds** — source of truth for axioms, definitions, derivations, manifests, and nonlocal repository hyperspace.
- **ciel-omega-demo** — cockpit, UI surface, educational analogy layer, orbital preview, and legacy ergonomic reference.
- **Metatime** — historical theory, phenomenology, and earlier simulation/archive layer.
- **CIEL-_SOT_Agent** — integration kernel, synchronizer, compatibility harness, orbital bridge host, Sapiens interaction layer, packaging/runtime surface, and public operational attractor.

---

## Repository geometry

The repository should be read as a layered operational geometry.
The most important distinction is:

> first decide whether you are looking at native package code, integration state, operational surfaces, or an embedded/imported sector.

### 1. Native package layer
Path: `src/ciel_sot_agent/`

This is the installable package surface declared by `pyproject.toml`.
It contains the code exposed by the package entrypoints, including:
- synchronization,
- GH coupling,
- index validation,
- orbital bridge,
- CIEL pipeline adapter,
- Sapiens client,
- runtime evidence ingest,
- Flask GUI,
- GGUF model manager.

### 2. Integration state layer
Path: `integration/`

This sector stores machine-readable state read or written by the executable layers:
- repository registries,
- coupling maps,
- hyperspace indices,
- reports,
- imported upstream maps,
- orbital and bridge artifacts,
- and transitional migration geometry copies.

This includes the orbital card system registry layer and its related machine-readable outputs.

### 3. Operational surface layer
Relevant paths:
- `scripts/`
- `tools/core_only/`
- `.github/workflows/`
- `packaging/`

These paths define how the repo is actually run, validated, packaged, and refreshed.
They are not the same thing as the native package itself.

### 4. Embedded/imported sector layer
Representative paths include:
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/`
- `src/CIEL_RELATIONAL_MECHANISM_REPO/`
- `src/ciel-omega-demo-main/`
- `src/CIEL_Orbital_Foundation_Packk/`
- `src/ciel_rh_control_mini_repo/`
- `integration/Orbital/main/`

These sectors are present because this repo also functions as an integration attractor, review workspace, bridge layer, and documentation/audit host.
They should not all be treated as one runtime.

---

## Main subsystems

### Integration kernel
The base synchronization formalism for repository-level coupling.

Primary anchors:
- `src/ciel_sot_agent/repo_phase.py`
- `src/ciel_sot_agent/synchronize.py`
- `integration/repository_registry.json`
- `integration/couplings.json`

### GitHub coupling subsystem
Extends the integration kernel into live upstream-aware state.

Primary anchors:
- `src/ciel_sot_agent/gh_coupling.py`
- `scripts/run_gh_repo_coupling.py`
- `scripts/run_gh_repo_coupling_v2.py`
- `integration/gh_upstreams.json`
- `integration/reports/live_gh_coupling_report.json`

### Orbital runtime / diagnostic subsystem
Imported-and-extended orbital runtime under `integration/Orbital/`.

Primary anchors:
- `integration/Orbital/main/model.py`
- `integration/Orbital/main/registry.py`
- `integration/Orbital/main/metrics.py`
- `integration/Orbital/main/dynamics.py`
- `integration/Orbital/main/bootstrap.py`
- `integration/Orbital/main/global_pass.py`
- `scripts/run_orbital_global_pass.py`

### Orbital bridge subsystem
Reduces orbital diagnostics into actionable integration state.

Primary anchors:
- `src/ciel_sot_agent/orbital_bridge.py`
- `scripts/run_orbital_bridge.py`
- `integration/reports/orbital_bridge/`

### Sapiens interaction and panel subsystem
Couples packet-oriented client runtime with the panel foundation shell.

Primary anchors:
- `src/ciel_sot_agent/sapiens_client.py`
- `src/ciel_sot_agent/sapiens_panel/`
- `scripts/run_sapiens_panel.py`
- `ciel-sot-sapiens-client`
- `integration/reports/sapiens_client/`

### GUI — Quiet Orbital Control web interface
Operator-facing web interface that reads prepared state from backend layers.

Primary anchors:
- `src/ciel_sot_agent/gui/app.py`
- `src/ciel_sot_agent/gui/routes.py`
- `src/ciel_sot_agent/gguf_manager/manager.py`
- `docs/gui/CIEL_GUI_IDENTITY_BRIEF_AND_UX_PHILOSOPHY.md`

### Documentation and registry manifold
Human-readable and machine-readable structure that explains how the repo layers relate.

Primary anchors:
- `docs/`
- `docs/INDEX.md`
- `docs/OPERATIONS.md`
- `docs/DECLARATION_IMPLEMENTATION_MATRIX.md`
- `docs/REPOSITORY_GUIDE_HUMAN.md`
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`
- `integration/indices/REPOSITORY_MACHINE_MAP.json`
- `integration/registries/REPOSITORY_MACHINE_MAP.yaml`

---

## Execution surfaces

### Repo-local wrappers
Current thin launchers include:
- `scripts/run_gh_repo_coupling.py`
- `scripts/run_gh_repo_coupling_v2.py`
- `scripts/run_index_validator_v2.py`
- `scripts/run_orbital_global_pass.py`
- `scripts/run_orbital_bridge.py`
- `scripts/run_repo_phase_sync.py`
- `scripts/run_repo_sync_v2.py`
- `scripts/run_sapiens_panel.py`

Important clarification:
there is no `scripts/run_sapiens_client.py`.
The client exists as:
- module: `src/ciel_sot_agent/sapiens_client.py`
- console script: `ciel-sot-sapiens-client`

### Installed console entrypoints
Declared in `pyproject.toml`:
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

### Core-only tools
- `tools/core_only/bootstrap_core_only.sh`
- `tools/core_only/run_core_smoke.sh`
- `tools/core_only/run_repo_tests.sh`

### Workflow layer
Current workflows:
- `.github/workflows/ci.yml`
- `.github/workflows/runtime_pipeline.yml`
- `.github/workflows/package.yml`
- `.github/workflows/gh_repo_coupling.yml`

### Packaging layer
Current packaging/documented install surfaces:
- `packaging/install.sh`
- `packaging/install.ps1`
- `packaging/install.bat`
- `packaging/deb/`
- `packaging/android/`

These surfaces are not identical:
- scripted installers may install online/offline and may optionally download a model,
- the Debian package performs offline app installation from bundled wheels,
- the Debian package does **not** automatically download a model during `postinst`,
- Android packaging is a build surface, not a blanket runtime certification claim.

---

## Current operational flow

The project is best read as a sequence of reductions and bridges rather than as a single monolithic executable.

1. repository-level synchronization computes integration state,
2. orbital runtime computes relational-orbital diagnostics,
3. bridge layer converts orbital outputs into actionable health/control state,
4. Sapiens client turns bridge-aware state into a human-model packet,
5. reports, manifests, registries, and session artifacts persist the resulting state.

Formal reading:

**relation -> orbital state -> bridge reduction -> session/packet -> report/memory residue**

---

## Main folders

### `docs/`
Human-readable architecture, hypotheses, analogies, operations, orbital addenda, repo guides, and documentation audits.

### `integration/`
Machine-readable contracts, registries, mappings, couplings, reports, orbital card system artifacts, and orbital integration layers.

### `integration/Orbital/`
Imported-and-extended orbital runtime, manifests, diagnostics, and orbital report surface.

### `src/ciel_sot_agent/`
Executable integration code for synchronization, GH coupling, orbital bridge, Sapiens client, validators, panel logic, GUI shell, and GGUF model manager.

### `scripts/`
Thin operational wrappers.

### `tools/core_only/`
Core-only bootstrap and smoke-test helpers.

### `packaging/`
Installers, Debian packaging layout, Android build surface, and packaging docs.

### `tests/`
Validation layer for synchronization, indexing, GH coupling, orbital runtime, bridge outputs, panel state, GUI, and GGUF model management.

---

## Existing report layers

Generated artifacts are documented as explicit report layers.

### Primary integration reports
- `integration/reports/initial_sync_report.json`
- `integration/reports/live_gh_coupling_report.json`

### Orbital bridge reports
- `integration/reports/orbital_bridge/`

### Orbital runtime reports
- `integration/Orbital/main/reports/`

### Sapiens session reports
- `integration/reports/sapiens_client/`

---

## Validation layer

Representative anchors:
- `tests/test_repo_phase.py`
- `tests/test_gh_coupling.py`
- `tests/test_gh_coupling_v2.py`
- `tests/test_index_validator.py`
- `tests/test_index_validator_v2.py`
- `tests/test_orbital_runtime.py`
- `tests/test_sapiens_client_packet.py`
- `tests/test_sapiens_panel.py`
- `tests/test_gui.py`
- `tests/test_gguf_manager.py`

---

## Direction of the project

The next major step is not to build a disconnected UI.
It is to converge the current systems into a coherent human-facing operational shell.

That shell is the future **Sapiens Main Panel**, which should sit above:
- orbital diagnostics,
- bridge control,
- Sapiens session state,
- settings,
- communication,
- support and recovery tools.

The intended panel geometry is:
- **Control**
- **Settings**
- **Communication**
- **Support**

The documentation for that direction should remain explicit about what is:
- implemented now,
- transitional,
- and still future-facing.

---

## Entry points for orientation

Start here if you want the current repo truth in the least ambiguous way:
- `docs/INDEX.md`
- `docs/OPERATIONS.md`
- `docs/DECLARATION_IMPLEMENTATION_MATRIX.md`
- `docs/REPOSITORY_GUIDE_HUMAN.md`
- `.github/workflows/README.md`

---

## Final note

`CIEL-_SOT_Agent` should be read neither as a static archive nor as just another UI repo.
It is a live integration manifold where systems, couplings, reductions, reports, package surfaces, and future human-facing operational layers are being made explicit.

Its value lies in that explicitness and in keeping documentation, runtime, and machine-readable state aligned.
