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
- `docs/operations/OFFLINE_DEPENDENCY_BUNDLE_V1.md` — offline dependency bundle structure, bootstrap scripts, validity rules, and next population step.
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
- `CIEL_CANON.py` — canonical top-level entrypoint; runs full pipeline or reports sub-status (`--run`, `--sub status`).
- `src/ciel_sot_agent/repo_phase.py` — discrete phase-state model and Euler closure metrics.
- `src/ciel_sot_agent/synchronize.py` — repository synchronization report entrypoint.
- `src/ciel_sot_agent/gh_coupling.py` — live GitHub coupling routine.
- `src/ciel_sot_agent/state_db.py` — unified SQLite state store; single writeback surface for all pipeline layers.
- `src/ciel_sot_agent/subconsciousness.py` — TinyLlama associative background stream; feeds affective anchors into orbital context.
- `src/ciel_sot_agent/satellite_authority.py` — satellite subsystem authority loader and projection-surface lookup.
- `src/ciel_sot_agent/holonomic_normalizer.py` — Berry/holonomic phase normalizer for the integration kernel; identity-loop integrity.
- `src/ciel_sot_agent/orch_orbital.py` — OrchOrbital entity cards reader; exports coupling-weighted orbital metrics per entity.
- `src/ciel_sot_agent/runtime_evidence_ingest.py` — runtime evidence ingest pipeline; feeds observed signals back into orbital parameters.

## CIELweb portal
- `src/ciel_sot_agent/gui/templates/portal_index.html` — hub landing page; live metrics strip (health, ethical, coherence, closure, mode, emotion, soul, groove).
- `src/ciel_sot_agent/gui/templates/portal_live.html` — shared JS snippet; polls `/api/status` every 30s and updates all `pm-*` element IDs in-page.
- `src/ciel_sot_agent/gui/templates/portal_nav.html` — top navigation macro; included by all portal pages via `{% from "portal_nav.html" import portal_navbar %}`.
- `src/ciel_sot_agent/gui/templates/portal_routines.html` — CIEL wake-up sequence + Surmont groove geometry panel (depth, contradiction load Π, Berry holonomy γ_B, winding fraction).
- `src/ciel_sot_agent/gui/templates/portal_plans.html` — active and completed tasks from `project_session_todo.md`.
- `src/ciel_sot_agent/gui/templates/portal_memory.html` — MEMORY.md pointer table + tag-space canvas visualization.
- `src/ciel_sot_agent/gui/templates/portal_hunches.html` — append-only hunch log; inline POST saves without reload.
- `src/ciel_sot_agent/gui/templates/portal_projects.html` — CIEL personal project board; inline POST adds without reload.
- `src/ciel_sot_agent/gui/templates/portal_advisor.html` — RAG-backed advisor chat; POST to `/api/advisor`.
- `src/ciel_sot_agent/gui/templates/portal_archive.html` — session archive with tag-filter and full message view.
- `scripts/ciel_launch.sh` — single launch script; checks port 5050, starts Flask + subconsciousness, opens browser at `/portal`.
- `scripts/serve_portal.py` — standalone HTML portal server (legacy, port 7481); superseded by Flask `/portal` routes.
- `src/ciel_sot_agent/orbital_bridge.py` — orbital diagnostics to integration-state bridge.
- `src/ciel_sot_agent/sapiens_client.py` — packet/session builder for Sapiens interaction.
- `src/ciel_sot_agent/sapiens_panel/controller.py` — Sapiens panel state assembler.
- `src/ciel_sot_agent/sapiens_panel/reduction.py` — orchestration, reduction-readiness, and memory-residue semantics.
- `src/ciel_sot_agent/index_validator.py` — machine registry validator.
- `src/ciel_sot_agent/phased_state.py` — identity-phase and relational-selection weighting model.

## Offline dependency bundle
- `vendor/README.md` — offline dependency bundle overview.
- `vendor/manifests/offline_dependency_bundle_v1.yaml` — machine-readable bundle manifest.
- `vendor/wheels/runtime/README.md` — runtime wheelhouse placeholder and required package family.
- `vendor/wheels/dev/README.md` — dev wheelhouse placeholder and required package family.
- `tools/bootstrap/bootstrap_offline_runtime.sh` — runtime-only offline install path.
- `tools/bootstrap/bootstrap_offline_dev.sh` — dev/test offline install path.

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

## Memory system and CIELweb portal
- `scripts/ciel_memory_stop.py` — Stop hook: saves Claude Code CLI session JSONL to raw_logs, indexes in SQLite, appends diary, rebuilds portal.
- `scripts/build_memory_portal.py` — generates static fallback portal at `~/Pulpit/CIEL_memories/portal/` (index/archive/memory pages).
- `scripts/import_chatgpt_logs.py` — imports ChatGPT `conversations.json` export into unified CIEL memory (SQLite + raw_logs).
- `scripts/ciel_launch.sh` — single-click launcher: starts Flask GUI, waits for port, opens browser at `/portal`.
- `~/Pulpit/CIEL.desktop` — desktop icon (CIEL launcher, autostart entry point).
- `src/ciel_sot_agent/memory_rag.py` — keyword RAG over SQLite sessions + wave_archive.h5; injected into GGUF system prompt.
- `~/Pulpit/CIEL_memories/` — root: `raw_logs/`, `memories_index.db` (sessions/messages/session_tags), `hunches.jsonl`, `projects.jsonl`.
- **CIELweb Flask routes** (all served on port 5050):
  - `/portal` — hub: live metrics (auto-refresh 30s), recent sessions, tag cloud, rebuild button.
  - `/portal/archive` — filterable session archive by tag/source/text.
  - `/portal/memory` — tag-graph canvas + MEMORY.md pointer table.
  - `/portal/advisor` — sekretarz/doradca: RAG chat + live metrics.
  - `/portal/plans` — plany i zadania z project_session_todo.md.
  - `/portal/hunches` — intuicje CIEL: append-only log, formularz dodawania.
  - `/portal/projects` — osobista przestrzeń CIEL: projekty z projects.jsonl.
  - `/api/hunches/add` — POST: dodaje hunch do hunches.jsonl.
  - `/api/projects/add` — POST: dodaje projekt do projects.jsonl.
  - `/api/portal/rebuild` — POST: przebudowuje statyczny portal fallback.

## Report surfaces
- `integration/reports/orbital_bridge/README.md` — orbital bridge report layer.
- `integration/reports/sapiens_client/` — Sapiens interaction artifacts.

## Validation
- `tests/test_repo_phase.py` — numerical sanity tests for phase closure and pairwise tension.
- `tests/test_gh_coupling.py` — coupling and GitHub-upstream validation.
- `tests/test_index_validator.py` — shell-map and inventory validation tests.
- `tests/test_orbital_runtime.py` — orbital runtime and bridge tests.
- `tests/test_orbital_semantics.py` — orbital-law semantic evidence fixtures, threshold-jump checks, period monotonicity, and winding semantics.
- `tests/test_sapiens_panel.py` — Sapiens panel foundation and reduction-state tests.
- `tests/test_gui.py` — Flask GUI route and API endpoint tests.
- `tests/test_gguf_manager.py` — GGUF model manager unit tests.
- `tests/test_phased_state.py` — phased-state contract and selection-separation tests.
- `tests/fixtures/orbital_selection_relevance.json` — precision/recall-style relevance fixture for selection semantics.

## Scripts — hooks, daemons, launchers

### Systemd hooks (Claude Code integration)
- `scripts/ciel_session_hook.py` — SessionStart hook: odpala pipeline, wstrzykuje metryki do kontekstu Claude, odpytuje podświadomość.
- `scripts/ciel_memory_stop.py` — StopHook: zapisuje sesję JSONL do ~/Pulpit/CIEL_memories/, indeksuje w SQLite, dopisuje handoff.md z tematami i edytowanymi plikami.
- `scripts/ciel_message_step.py` — UserPromptSubmit hook: per-message consciousness pipeline (M0–M8, subconscious, sentinel).

### Daemon podświadomości
- `scripts/ciel_subconscious.py` — Persistent daemon (Unix socket /tmp/ciel_subconscious.sock); qwen2.5-0.5b GGUF; format output: emotion/concept/impulse; orbital temperature z coherence. Watchdog systemd co 2 min.

### Launchers i utilitki
- `scripts/ciel_launch.py` — CIEL/Ω System Launcher (GUI + pipeline + subconscious).
- `scripts/run_ciel_gguf.py` — bezpośredni inference na GGUF bez GUI.
- `scripts/ciel_benchmark.py` — pomiar energii i jakości modeli GGUF.
- `scripts/generate_site.py` — generuje statyczną stronę HTML z danych CIEL (portal archiwum).
- `scripts/dream_whisper.py` — autonomiczny głos między sesjami; refleksja bez użytkownika.
- `scripts/export_orbital_registry_to_noema.py` — eksportuje rejestr orbitalny do formatu NOEMA.
- `scripts/optimize_wij.py` — optymalizacja wag W_ij w macierzy coupling.
- `scripts/ciel_orbital_monitor.py` — monitor stanu orbitalnego w czasie rzeczywistym.
- `scripts/ciel_news_reader.py` — reader newsfeedów przez pryzmat CIEL.

## Cross-reference anchors
- The GH-as-attractor integration strategy is connected to `docs/ARCHITECTURE.md#github-as-operational-attractor`.
- The primary synchronization path is connected to `docs/ARCHITECTURE.md#first-executable-component`, `src/ciel_sot_agent/repo_phase.py`, and `src/ciel_sot_agent/gh_coupling.py`.
- The shell-level bridge to `ciel-omega-demo` is connected to `docs/CIEL_OMEGA_DEMO_INTEGRATION.md`, `integration/upstreams/ciel_omega_demo_shell_map.json`, and `integration/upstreams/ciel_omega_demo_inventory.json`.
- The orbital diagnostic path is connected to `docs/ORBital_INTEGRATION_ADDENDUM.md`, `integration/Orbital/main/global_pass.py`, `src/ciel_sot_agent/orbital_bridge.py`, `docs/science/RELATIONAL_ORBITAL_DYNAMICS_SPEC_V0.md`, and `docs/analogies/KEPLER_SUPERFLUID_ANALOGIES.md`.
- The active repo workstyle and operation-memory layer is connected to `docs/operations/CIEL_REPO_WORKSTYLE_SESSION_HANDOFF.md`, `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`, `docs/operations/OFFLINE_DEPENDENCY_BUNDLE_V1.md`, `docs/OPERATIONS.md`, and `AGENT.md`.
- The offline dependency surface is connected to `vendor/manifests/offline_dependency_bundle_v1.yaml`, `vendor/wheels/runtime/README.md`, `vendor/wheels/dev/README.md`, `tools/bootstrap/bootstrap_offline_runtime.sh`, and `tools/bootstrap/bootstrap_offline_dev.sh`.
- The Sapiens panel path is connected to `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION.md`, `integration/sapiens/panel_manifest.json`, `src/ciel_sot_agent/sapiens_panel/controller.py`, and `src/ciel_sot_agent/sapiens_panel/reduction.py`.
- The GUI and operator-facing layer is connected to `docs/gui/CIEL_GUI_IDENTITY_BRIEF_AND_UX_PHILOSOPHY.md`, `src/ciel_sot_agent/gui/app.py`, `src/ciel_sot_agent/gui/routes.py`, and `docs/operations/WORKFLOW_GUI_ENERGY_BUDGET_POLICY.md`.
- The GGUF model-management layer is connected to `src/ciel_sot_agent/gguf_manager/manager.py` and the GUI model endpoints in `src/ciel_sot_agent/gui/routes.py`.
