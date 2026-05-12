# Memory Refactor Execution Plan

Date: 2026-05-11  
Status: execution ordering draft  
Rule: sort by lowest risk first, highest continuity risk last

## Ordering

1. projection surfaces
2. registry/catalog layer
3. nonlocal registry/projection layer
4. context assembly layer
5. telemetry/state surfaces
6. runtime continuity
7. durable memory boundaries

## Phase 0 — labeling only

Goal:
- establish explicit labels:
  - `canonical_runtime`
  - `canonical_durable`
  - `runtime_continuity`
  - `canonical_relational_injection`
  - `derived_registry`
  - `projected_surface`
  - `mirror_compat`
  - `operational_shadow`

Deliverable:
- architecture/audit docs only

Risk:
- minimal

## Phase 1 — projection surfaces

Targets:
- `integration/imports/noema_sapiens_orbital/generated/registry_export.noema`
- selected `integration/reports/*`
- other projection-only JSON/MD surfaces

Goal:
- mark projection-only outputs
- reduce false authority assigned to generated exports

Risk:
- low

## Phase 2 — registry/catalog consolidation

Targets:
- `semantic_calculator.py`
- `semantic_calculator_v2.py`
- `py_catalog.py`
- `noema_file_sense.py`
- `md_library.py`
- `file_catalog.json`
- `file_universal_catalog.json`

Goal:
- converge toward one semantic file registry model with multiple views

Risk:
- medium

## Phase 3 — nonlocal registry/projection consolidation

Targets:
- `nonlocal_cards_registry.json`
- `spreadsheet_db.nonlocal_cards`
- `orbital_definition_registry.json`
- `nonlocal_definition_edges.json`
- `registry_export.noema`

Goal:
- one explicit source for cards
- one explicit source for definition graph
- projections derived from those sources only

Risk:
- medium

## Phase 4 — context assembly consolidation

Targets:
- `memory_rag.py`
- `memory_prompt_context.py`
- selected loaders in `ciel_session_hook.py`

Goal:
- separate:
  - retrieval
  - summarization
  - prompt context assembly
  - session-start context assembly

Risk:
- medium

## Phase 5 — telemetry/state surface consolidation

Targets:
- `metrics_history`
- `json_reports`
- `timeline.json`
- bridge report surfaces
- HTRI report/state surfaces

Goal:
- make primary telemetry explicit
- demote shadow reports/views to projections or caches

Risk:
- medium to high

## Phase 6 — runtime continuity migration

Targets:
- `ciel_orch_state.pkl`
- `~/.claude/ciel_state.db`
- `save_orchestrator_state/load_orchestrator_state`
- pickle consumers

Goal:
- migrate from pickle-led continuity to DB-led continuity

Risk:
- high

Constraint:
- requires explicit migration plan

## Phase 7 — durable memory boundary cleanup

Targets:
- top-level `memory_ledger.db`
- package mirror `ciel_omega/.../memory_ledger.db`
- TSM/WPM/consolidator/session-memory boundary rules

Goal:
- make durable authority and compatibility boundaries explicit

Risk:
- very high

Constraint:
- do not perform destructive cleanup without dedicated migration proof

## Merge candidates

### Direct merge / unification candidates

- `semantic_calculator.py` + `semantic_calculator_v2.py`
- `py_catalog.py` + `noema_file_sense.py`
- `md_library.py` into the common file-registry layer
- `file_catalog.json` + `file_universal_catalog.json`
- `memory_rag.py` + `memory_prompt_context.py`
- `nonlocal_cards_registry.json` + `spreadsheet_db.nonlocal_cards`

### Contract-level unification candidates

- `htri_scheduler.py` + `htri_daemon.py`
- `metrics_history` + report/view surfaces
- `timeline.json` + telemetry views

### Migration-only candidates

- pickle continuity ↔ `state_db`
- top-level TSM ↔ package mirror TSM
