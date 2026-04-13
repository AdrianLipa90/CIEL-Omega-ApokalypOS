# CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold
## General Quantum Consciousness System

Repository: CIEL-_SOT_Agent

`CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` is the integration attractor for the wider CIEL ecosystem.
It is a live integration manifold where synchronization, couplings, orbital diagnostics, bridge reduction, Sapiens interaction, GUI control, packaging surfaces, and machine-readable state are kept in one operational repository.

## Role in the ecosystem

`CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` does not replace the canon, `ciel-omega-demo`, or Metatime.
It binds them through explicit operational relations.

- **canon / Seed of the Worlds** — source of truth for axioms, definitions, derivations, and registry logic.
- **ciel-omega-demo** — cockpit, educational analogy layer, and ergonomic reference.
- **Metatime** — historical theory and earlier simulation/archive layer.
- **CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold** — integration kernel, bridge host, compatibility harness, public operational shell, and packaging/runtime surface.

## System architecture

### Integration kernel
Primary anchors:
- `src/ciel_sot_agent/repo_phase.py`
- `src/ciel_sot_agent/synchronize.py`
- `integration/repository_registry.json`
- `integration/couplings.json`

### GitHub coupling
Primary anchors:
- `src/ciel_sot_agent/gh_coupling.py`
- `scripts/run_gh_repo_coupling.py`
- `integration/reports/live_gh_coupling_report.json`

### Orbital runtime
Primary anchors:
- `integration/Orbital/main/model.py`
- `integration/Orbital/main/global_pass.py`
- `scripts/run_orbital_global_pass.py`

### Orbital bridge
Primary anchors:
- `src/ciel_sot_agent/orbital_bridge.py`
- `scripts/run_orbital_bridge.py`
- `integration/reports/orbital_bridge/`

### Sapiens interaction
Primary anchors:
- `src/ciel_sot_agent/sapiens_client.py`
- `src/ciel_sot_agent/sapiens_panel/`
- `scripts/run_sapiens_panel.py`

### GUI
Primary anchors:
- `src/ciel_sot_agent/gui/app.py`
- `src/ciel_sot_agent/gui/routes.py`
- `src/ciel_sot_agent/gguf_manager/manager.py`

## Couplings

The repository is organized around explicit couplings between identity, executable logic, machine-readable state, and human-facing control.
Representative couplings include:
- registry ↔ synchronization,
- GitHub state ↔ coupling refresh,
- orbital state ↔ bridge reduction,
- bridge reduction ↔ Sapiens packet/session state,
- GUI control ↔ local model management.

## Operational flow

The project is best read as a reduction chain rather than as a monolithic app.

1. repository-level synchronization computes integration state,
2. orbital runtime computes relational-orbital diagnostics,
3. bridge reduction converts orbital outputs into actionable state,
4. Sapiens interaction turns bridge-aware state into packets and panel state,
5. reports and registries persist the resulting operational trace.

Formal reading:

**relation -> orbital state -> bridge reduction -> session/packet -> report/memory residue**

## Main folders

- `docs/` — human-readable architecture, hypotheses, operations, and addenda.
- `integration/` — machine-readable registries, couplings, reports, and bridge artifacts.
- `integration/Orbital/` — imported and extended orbital runtime.
- `src/ciel_sot_agent/` — executable integration code.
- `src/android_app/` — Android application scaffold (Kotlin + XML) for mobile-facing integration.
- `scripts/` — thin repo-local wrappers.
- `packaging/` — installation and packaging surfaces.
- `tests/` — validation layer.


## Android mobile scaffold

A starter Android app is available under `src/android_app/` on branch `wtctg4`.

Contents:
- Gradle Kotlin DSL root project and `app` module,
- launcher `MainActivity` (`com.ciel.sotagent`),
- XML layout (`activity_main.xml`) and Material 3 theme resources,
- quick start notes in `src/android_app/README.md`.

Open `src/android_app` directly in Android Studio to sync Gradle and run the app on an emulator/device.

## Existing launchers

Representative launchers include:
- `scripts/run_gh_repo_coupling.py`
- `scripts/run_orbital_global_pass.py`
- `scripts/run_orbital_bridge.py`
- `scripts/run_repo_phase_sync.py`
- `scripts/run_sapiens_panel.py`

## Existing report layers

- `integration/reports/initial_sync_report.json`
- `integration/reports/live_gh_coupling_report.json`
- `integration/reports/orbital_bridge/`
- `integration/Orbital/main/reports/`
- `integration/reports/sapiens_client/`

## Validation layer

Representative anchors:
- `tests/test_repo_phase.py`
- `tests/test_gh_coupling.py`
- `tests/test_index_validator.py`
- `tests/test_orbital_runtime.py`
- `tests/test_sapiens_client_packet.py`
- `tests/test_sapiens_panel.py`
- `tests/test_gui.py`
- `tests/test_gguf_manager.py`

## Final note

`CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` should be read neither as a static archive nor as just another interface.
It is a live integration manifold whose value lies in keeping documentation, runtime, couplings, and machine-readable state aligned.
