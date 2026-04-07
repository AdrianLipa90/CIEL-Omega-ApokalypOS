# Orbital / Nonlocal Definition Registry

This sector is the output target for the automatic definition-catalog patch.

## Goal
Extract formal definitions from active code, assign them to orbital roles, and emit a nonlocal edge map that can be hyperlinked into the wider hyperspace / nonlocal registry.

## Pipeline
1. `python scripts/build_orbital_definition_registry.py`
   - scans configured roots
   - extracts file nodes and formal definitions
   - emits `definition_registry.json` and `definition_registry.csv`
2. `python scripts/resolve_orbital_semantics.py`
   - assigns orbital roles and semantic roles heuristically
   - enriches each **export card** with hierarchy, horizon, information-regime, leakage, tau-role, many-body metadata, and horizon-policy semantics
   - emits `orbital_definition_registry.json`, `internal_subsystem_cards.json`, `horizon_policy_matrix.json`, and `orbital_assignment_report.json`
3. `python scripts/build_nonlocal_definition_edges.py`
   - builds nonlocal / hyperref edges
   - emits `nonlocal_definition_edges.json`

## Output files
- `definition_registry.json`
- `definition_registry.csv`
- `orbital_definition_registry.json`
- `internal_subsystem_cards.json`
- `horizon_policy_matrix.json`
- `orbital_assignment_report.json`
- `nonlocal_definition_edges.json`

## Design principle
The patch does **not** pretend to understand all domain semantics. It first captures structure faithfully, then assigns orbital meaning with explicit confidence, then emits a graph that can be hand-corrected where needed.

## Recursion guard
The definition registry must not ingest its own generated card artifacts. The normalization step removes paths under `integration/registries/definitions/` and stabilizes definition IDs with line numbers so the card graph remains non-self-referential across reruns.

## Database library
4. `python scripts/build_definition_db_library.py`
   - compiles the enriched registries into a **database library** under `db_library/`
   - writes `records.sqlite`, `internal_cards.sqlite`, `horizon_policies.sqlite`, `reports.sqlite`, relation-sharded edge databases and `manifest.json`

### Why a database library
The full registry becomes too large and too self-referential as a monolithic JSON export. The database library keeps the catalog queryable, indexed and split by concern (`records`, `internal_cards`, `horizon_policies`, `reports`, sharded `edges_*`) instead of forcing one gargantuan tracked text artifact.

## Orbital export cards v0.4
Phase 3 formalizes horizon semantics and leakage by attaching deterministic policy fields to every export card.

### Export card fields
- `card_schema`
- `global_attractor_ref`
- `container_card_id`
- `subsystem_kind`
- `manybody_role`
- `parent_orbital_role`
- `horizon_id`
- `horizon_class`
- `information_regime`
- `visible_scopes`
- `leak_policy`
- `tau_role`
- `lagrange_roles`
- `internal_card_id`
- `projection_operator`
- `privacy_constraint`
- `leak_channel_mode`
- `leak_budget_class`
- `allowed_visibility_transitions`
- `policy_table_ref`
- `export_state`
- `export_result`
- `export_confidence`
- `residual_uncertainty`

## Internal subsystem card fields v0.2
- `internal_card_schema`
- `internal_card_id`
- `owner_card_id`
- `owner_horizon_id`
- `container_card_id`
- `subsystem_kind`
- `manybody_role`
- `internal_visibility`
- `internal_candidate_states`
- `internal_conflict_state`
- `internal_superposition_state`
- `internal_resolution_trace`
- `internal_tau_local`
- `internal_memory_mode`
- `projection_operator`
- `privacy_constraint`
- `horizon_transition_profile`
- `exportable_fields`
- `sealed_fields`
- `policy_table_ref`
- `export_card_id`

## Horizon policy matrix
`horizon_policy_matrix.json` is the deterministic ruleset for:
- `SEALED`
- `POROUS`
- `TRANSMISSIVE`
- `OBSERVATIONAL`

Each class defines:
- `privacy_constraint`
- `leak_channel_mode`
- `leak_budget_class`
- `allowed_visibility_transitions`
- `exportable_fields`
- `sealed_fields`

## Systemic Privacy Law
Every subsystem preserves a private internal knowledge layer `K_int` and exposes only a horizon-projected export layer `K_ext`.

`K_ext = Π_H(K_int)`

This means:
- internal cards remain private to the subsystem,
- export cards must not contain internal-only fields,
- horizon policy determines which fields may be exported and how they may leak,
- export cards carry only results, summaries, uncertainty, and leak-compatible projections.

## In-repo implementation records
- `integration/registries/definitions/ORBITAL_MANYBODY_IMPLEMENTATION_PLAN.md`
- `integration/registries/definitions/ORBITAL_MANYBODY_TODO.md`
