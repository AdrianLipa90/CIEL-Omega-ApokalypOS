# Documentation Index

## Core architecture
- `docs/ARCHITECTURE.md` — repository role, geometry, upstream bindings, and initial execution plan.
- `docs/CIEL_OMEGA_DEMO_INTEGRATION.md` — explicit shell-level integration bridge to `AdrianLipa90/ciel-omega-demo`.
- `docs/OPERATIONS.md` — operational bridge for scripts, workflows, and report layers.
- `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION.md` — shared implementation direction for the Sapiens Main Panel.
- `docs/ORBital_INTEGRATION_ADDENDUM.md` — orbital integration and bridge addendum.
- `docs/Orbitrary shifts.md` — current orbitalization state of the repository: already orbitalized, partially orbitalized, and still outside stable orbit.
- `AGENT.md` — operational rules for the integration attractor.

## GUI and operator-facing layer
- `docs/gui/CIEL_GUI_IDENTITY_BRIEF_AND_UX_PHILOSOPHY.md` — canonical GUI identity, UX philosophy, visual language, and functional layering for the CIEL Quiet Orbital Control interface.
- `docs/operations/WORKFLOW_GUI_ENERGY_BUDGET_POLICY.md` — workflow execution policy, GUI shell architecture, and energy budget stratification for the human-facing phase.
- `docs/operations/V2_RUNTIME_ENTRYPOINTS.md` — preferred v2-aware executable entrypoints during repository-geometry migration.
- `docs/operations/V2_RUNTIME_ENTRYPOINTS_CANONICAL.md` — canonical v2 entrypoint reference after migration stabilization.

## Scientific and semantic notes
- `docs/analogies/RELATIONAL_ANALOGIES.md` — analogies and comparisons, explicitly marked as analogical and non-probative.
- `docs/science/HYPOTHESES.md` — scientific hypotheses and formal working claims.
- `docs/science/HEISENBERG_GODEL_SELF_CLOSURE_HYPOTHESIS.md` — composite working hypothesis on self-measurement, self-reference, and nonzero self-closure cost in truth-facing semantic systems.
- `docs/science/DERIVATION_NOTES.md` — compact derivation notes and bridges to imported anchors.

## Integration state
- `integration/repository_registry.json` — upstream repositories and local identities.
- `integration/couplings.json` — pairwise coupling strengths and relation types.
- `integration/hyperspace_index.json` — primary machine-readable cross-reference registry.
- `integration/hyperspace_index_orbital.json` — orbital addendum registry.
- `integration/index_registry.yaml` — primary machine-readable object registry.
- `integration/index_registry_orbital.yaml` — orbital addendum object registry.
- `integration/upstreams/ciel_omega_demo_shell_map.json` — imported shell object map for `ciel-omega-demo`.
- `integration/upstreams/ciel_omega_demo_inventory.json` — pinned inventory snapshot of known shell-facing upstream paths.
- `integration/sapiens/panel_manifest.json` — machine-readable Sapiens panel foundation manifest.
- `integration/sapiens/settings_defaults.json` — default settings for the Sapiens panel layer.

## Executable layer
- `src/ciel_sot_agent/repo_phase.py` — discrete phase-state model and Euler closure metrics.
- `src/ciel_sot_agent/synchronize.py` — CLI entrypoint for repository synchronization report.
- `src/ciel_sot_agent/gh_coupling.py` — live GitHub coupling routine.
- `src/ciel_sot_agent/orbital_bridge.py` — orbital diagnostics to integration-state bridge.
- `src/ciel_sot_agent/sapiens_client.py` — packet-aware human-model interaction seed.
- `src/ciel_sot_agent/sapiens_panel/controller.py` — Sapiens panel state assembler.
- `src/ciel_sot_agent/sapiens_panel/reduction.py` — orchestration, reduction-readiness, and memory-residue semantics.
- `src/ciel_sot_agent/index_validator.py` — machine registry validator for path, reference, placeholder, shell-map, and inventory coherence.

## GUI layer
- `src/ciel_sot_agent/gui/app.py` — Flask application factory and CLI entry-point (`ciel-sot-gui`) for the CIEL Quiet Orbital Control web interface.
- `src/ciel_sot_agent/gui/routes.py` — Flask route handlers: main dashboard (`GET /`), status API (`GET /api/status`), panel state (`GET /api/panel`), and GGUF model endpoints (`GET /api/models`, `POST /api/models/ensure`).

## GGUF model manager
- `src/ciel_sot_agent/gguf_manager/manager.py` — lightweight stdlib-only GGUF model manager; downloads and locates small quantised models on first startup without requiring heavy ML dependencies at install time.

## Validation
- `tests/test_repo_phase.py` — numerical sanity tests for phase closure and pairwise tension.
- `tests/test_gh_coupling.py` — coupling and GitHub-upstream related validation.
- `tests/test_index_validator.py` — shell-map and inventory validation tests.
- `tests/test_orbital_runtime.py` — orbital runtime and bridge tests.
- `tests/test_sapiens_panel.py` — Sapiens panel foundation and reduction-state tests.
- `tests/test_gui.py` — Flask GUI route and API endpoint tests.
- `tests/test_gguf_manager.py` — GGUF model manager unit tests.

## Launchers and report surfaces
- `scripts/run_gh_repo_coupling.py` — GitHub coupling launcher.
- `scripts/run_orbital_global_pass.py` — orbital runtime launcher.
- `scripts/run_orbital_bridge.py` — orbital bridge launcher.
- `scripts/run_sapiens_client.py` — Sapiens client packet launcher.
- `scripts/run_sapiens_panel.py` — Sapiens panel foundation launcher.
- `integration/reports/orbital_bridge/README.md` — orbital bridge report layer.
- `integration/reports/sapiens_client/` — Sapiens interaction artifacts.

## Console entrypoints
- `ciel-sot-gui` — launch the Flask-based Quiet Orbital Control web interface (`ciel_sot_agent.gui.app:main`).
- `ciel-sot-sync` — repository synchronization report (`ciel_sot_agent.synchronize:main`).
- `ciel-sot-gh-coupling` — live GitHub coupling routine (`ciel_sot_agent.gh_coupling:main`).
- `ciel-sot-orbital-bridge` — orbital diagnostics to bridge reduction (`ciel_sot_agent.orbital_bridge:main`).
- `ciel-sot-sapiens-client` — Sapiens packet/session builder (`ciel_sot_agent.sapiens_client:main`).
- `ciel-sot-runtime-evidence-ingest` — runtime evidence validator and ingest (`ciel_sot_agent.runtime_evidence_ingest:main`).

## Cross-reference anchors
- The GH-as-attractor integration strategy is connected to `docs/ARCHITECTURE.md#github-as-operational-attractor`.
- The primary synchronization path is connected to `docs/ARCHITECTURE.md#first-executable-component`, `src/ciel_sot_agent/repo_phase.py`, and `src/ciel_sot_agent/gh_coupling.py`.
- The shell-level bridge to `ciel-omega-demo` is connected to `docs/CIEL_OMEGA_DEMO_INTEGRATION.md`, `integration/upstreams/ciel_omega_demo_shell_map.json`, and `integration/upstreams/ciel_omega_demo_inventory.json`.
- The orbital diagnostic path is connected to `docs/ORBital_INTEGRATION_ADDENDUM.md`, `integration/Orbital/main/global_pass.py`, and `src/ciel_sot_agent/orbital_bridge.py`.
- The Sapiens panel path is connected to `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION.md`, `integration/sapiens/panel_manifest.json`, `src/ciel_sot_agent/sapiens_panel/controller.py`, and `src/ciel_sot_agent/sapiens_panel/reduction.py`.
- The repository orbitalization snapshot is connected to `docs/Orbitrary shifts.md`, `docs/ORBital_INTEGRATION_ADDENDUM.md`, and the main orbital/panel bridge layers.
- The Heisenberg-Godel self-closure hypothesis is connected to `docs/science/HYPOTHESES.md`, `AGENT.md`, and `integration/hyperspace_index.json`.
- The GUI and operator-facing layer is connected to `docs/gui/CIEL_GUI_IDENTITY_BRIEF_AND_UX_PHILOSOPHY.md`, `src/ciel_sot_agent/gui/app.py`, `src/ciel_sot_agent/gui/routes.py`, and `docs/operations/WORKFLOW_GUI_ENERGY_BUDGET_POLICY.md`.
- The GGUF model management layer is connected to `src/ciel_sot_agent/gguf_manager/manager.py` and the GUI model endpoints in `src/ciel_sot_agent/gui/routes.py`.
