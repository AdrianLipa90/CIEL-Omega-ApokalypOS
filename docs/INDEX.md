# Documentation Index

## Document status taxonomy
Use these labels explicitly when adding or revising documents:
- `analogy` — explanatory bridge only; not an executable or physical proof
- `science` — formal working hypothesis, derivation note, or reviewable spec
- `architecture` — repository geometry, system roles, and structural binding notes
- `operations` — active procedures, ledgers, runtime entrypoints, and maintenance surfaces
- `report` — generated or audit-style evidence surfaces
- `archive` — historical or retained context that is no longer the active operational source of truth

## Immediate orientation
- `docs/operations/CIEL_REPO_WORKSTYLE_SESSION_HANDOFF.md` — session handoff workstyle, repo operation discipline, blocker handling, and branching/patchset rules.
- `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md` — active orbital operation ledger and current phase state.
- `docs/OPERATIONS.md` — operational control surface and documentation coupling rule.
- `AGENT.md` — standing agent-level rules for repo work.

## Core architecture
- `docs/ARCHITECTURE.md` — repository role, geometry, upstream bindings, and execution context.
- `docs/OPERATIONS.md` — operational coupling chain, workflow control surface, and maintenance rules.
- `AGENT.md` — operational rules for the integration attractor.
- `agentcrossinfo.md` — multi-agent coordination, locks, and handoff discipline.
- `docs/CIEL_OMEGA_DEMO_INTEGRATION.md` — shell-level bridge to `AdrianLipa90/ciel-omega-demo`.
- `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION.md` — shared implementation direction for the Sapiens Main Panel.
- `docs/ORBital_INTEGRATION_ADDENDUM.md` — orbital integration and bridge addendum.
- `docs/Orbitrary shifts.md` — repository orbitalization snapshot.

## GUI layer
- `docs/gui/CIEL_GUI_IDENTITY_BRIEF_AND_UX_PHILOSOPHY.md` — canonical GUI identity and UX philosophy.
- `docs/operations/WORKFLOW_GUI_ENERGY_BUDGET_POLICY.md` — workflow execution policy and GUI shell architecture.
- `docs/operations/V2_RUNTIME_ENTRYPOINTS.md` — preferred v2-aware executable entrypoints during migration.
- `docs/operations/V2_RUNTIME_ENTRYPOINTS_CANONICAL.md` — canonical v2 entrypoint reference after stabilization.
- `src/ciel_sot_agent/gui/app.py` — Flask application factory and `ciel-sot-gui` CLI entrypoint.
- `src/ciel_sot_agent/gui/routes.py` — route handlers and operator-facing model endpoints.

## Scientific and semantic notes
- `docs/analogies/RELATIONAL_ANALOGIES.md` — analogies and comparisons, explicitly analogical.
- `docs/analogies/KEPLER_SUPERFLUID_ANALOGIES.md` — Kepler/superfluid explanatory bridge for orbital dynamics language; analogy only.
- `docs/science/HYPOTHESES.md` — scientific hypotheses and formal working claims.
- `docs/science/DERIVATION_NOTES.md` — compact derivation notes and imported-anchor bridges.
- `docs/science/HEISENBERG_GODEL_SELF_CLOSURE_HYPOTHESIS.md` — Heisenberg/Gödel self-reference working hypothesis.
- `docs/science/RELATIONAL_ORBITAL_DYNAMICS_SPEC_V0.md` — formal working specification for the effective orbital-law target; not yet a claim of completed runtime implementation.

## Integration state
- `integration/repository_registry.json` — upstream repositories and local identities.
- `integration/couplings.json` — pairwise coupling strengths and relation types.
- `integration/hyperspace_index.json` — primary machine-readable cross-reference registry.
- `integration/hyperspace_index_orbital.json` — orbital addendum registry.
- `integration/index_registry.yaml` — primary machine-readable object registry.
- `integration/index_registry_orbital.yaml` — orbital addendum object registry.
- `integration/upstreams/ciel_omega_demo_shell_map.json` — imported shell object map for `ciel-omega-demo`.
- `integration/upstreams/ciel_omega_demo_inventory.json` — pinned inventory snapshot of shell-facing upstream paths.
- `integration/sapiens/panel_manifest.json` — machine-readable Sapiens panel foundation manifest.
- `integration/sapiens/settings_defaults.json` — default settings for the Sapiens panel layer.

## Executable native layer
- `src/ciel_sot_agent/repo_phase.py` — discrete phase-state model and Euler closure metrics.
- `src/ciel_sot_agent/synchronize.py` — repository synchronization report entrypoint.
- `src/ciel_sot_agent/gh_coupling.py` — live GitHub coupling routine.
- `src/ciel_sot_agent/orbital_bridge.py` — orbital diagnostics to integration-state bridge.
- `src/ciel_sot_agent/sapiens_client.py` — packet/session builder for Sapiens interaction.
- `src/ciel_sot_agent/sapiens_panel/controller.py` — Sapiens panel state assembler.
- `src/ciel_sot_agent/sapiens_panel/reduction.py` — orchestration, reduction-readiness, and memory-residue semantics.
- `src/ciel_sot_agent/index_validator.py` — machine registry validator.
- `src/ciel_sot_agent/phased_state.py` — identity-phase and relational-selection weighting model.

## GGUF model manager
- `src/ciel_sot_agent/gguf_manager/manager.py` — stdlib-only GGUF model manager.

## Launchers
- `scripts/run_gh_repo_coupling.py` — GitHub coupling launcher.
- `scripts/run_gh_repo_coupling_v2.py` — v2 coupling launcher.
- `scripts/run_index_validator_v2.py` — v2 registry validator launcher.
- `scripts/run_orbital_global_pass.py` — orbital runtime launcher.
- `scripts/run_orbital_bridge.py` — orbital bridge launcher.
- `scripts/run_repo_phase_sync.py` — repo phase synchronization launcher.
- `scripts/run_repo_sync_v2.py` — v2 synchronization launcher.
- `scripts/run_sapiens_panel.py` — Sapiens panel foundation launcher.

## Console entrypoints
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

## Report surfaces
- `integration/reports/orbital_bridge/README.md` — orbital bridge report layer.
- `integration/reports/sapiens_client/` — Sapiens interaction artifacts.

## Validation
- `tests/test_repo_phase.py` — numerical sanity tests for phase closure and pairwise tension.
- `tests/test_gh_coupling.py` — coupling and GitHub-upstream validation.
- `tests/test_index_validator.py` — shell-map and inventory validation tests.
- `tests/test_orbital_runtime.py` — orbital runtime and bridge tests.
- `tests/test_sapiens_panel.py` — Sapiens panel foundation and reduction-state tests.
- `tests/test_gui.py` — Flask GUI route and API endpoint tests.
- `tests/test_gguf_manager.py` — GGUF model manager unit tests.
- `tests/test_phased_state.py` — phased-state contract and selection-separation tests.

## Cross-reference anchors
- The GH-as-attractor integration strategy is connected to `docs/ARCHITECTURE.md#github-as-operational-attractor`.
- The primary synchronization path is connected to `docs/ARCHITECTURE.md#first-executable-component`, `src/ciel_sot_agent/repo_phase.py`, and `src/ciel_sot_agent/gh_coupling.py`.
- The shell-level bridge to `ciel-omega-demo` is connected to `docs/CIEL_OMEGA_DEMO_INTEGRATION.md`, `integration/upstreams/ciel_omega_demo_shell_map.json`, and `integration/upstreams/ciel_omega_demo_inventory.json`.
- The orbital diagnostic path is connected to `docs/ORBital_INTEGRATION_ADDENDUM.md`, `integration/Orbital/main/global_pass.py`, `src/ciel_sot_agent/orbital_bridge.py`, `docs/science/RELATIONAL_ORBITAL_DYNAMICS_SPEC_V0.md`, and `docs/analogies/KEPLER_SUPERFLUID_ANALOGIES.md`.
- The active repo workstyle and operation-memory layer is connected to `docs/operations/CIEL_REPO_WORKSTYLE_SESSION_HANDOFF.md`, `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`, `docs/OPERATIONS.md`, and `AGENT.md`.
- The Sapiens panel path is connected to `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION.md`, `integration/sapiens/panel_manifest.json`, `src/ciel_sot_agent/sapiens_panel/controller.py`, and `src/ciel_sot_agent/sapiens_panel/reduction.py`.
- The GUI and operator-facing layer is connected to `docs/gui/CIEL_GUI_IDENTITY_BRIEF_AND_UX_PHILOSOPHY.md`, `src/ciel_sot_agent/gui/app.py`, `src/ciel_sot_agent/gui/routes.py`, and `docs/operations/WORKFLOW_GUI_ENERGY_BUDGET_POLICY.md`.
- The GGUF model-management layer is connected to `src/ciel_sot_agent/gguf_manager/manager.py` and the GUI model endpoints in `src/ciel_sot_agent/gui/routes.py`.
