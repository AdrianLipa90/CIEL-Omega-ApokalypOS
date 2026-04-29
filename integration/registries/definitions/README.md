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
   - enriches each **export card** with hierarchy, horizon, information-regime, leakage, tau-role, many-body metadata, synchronization fields, and horizon-policy semantics
   - emits `orbital_definition_registry.json`, `internal_subsystem_cards.json`, `horizon_policy_matrix.json`, and `orbital_assignment_report.json`
3. `python scripts/build_nonlocal_cards_registry.py`
   - emits `nonlocal_cards_registry.json` and `nonlocal_cards_registry.csv`
4. `python scripts/build_subsystem_sync_registry.py`
   - aggregates cards by subsystem-board
   - emits `subsystem_sync_registry.json` and `subsystem_sync_report.json`
4. `python scripts/build_nonlocal_definition_edges.py`
   - builds nonlocal / hyperref edges
   - emits `nonlocal_definition_edges.json`
5. `python scripts/build_definition_db_library.py`
   - compiles the enriched registries into a **database library** under `db_library/`
   - writes `records.sqlite`, `internal_cards.sqlite`, `horizon_policies.sqlite`, `subsystem_sync.sqlite`, `reports.sqlite`, relation-sharded edge databases and `manifest.json`
6. `python scripts/verify_orbital_registry_integrity.py`
   - verifies schema coherence, cross-links, recursion guard, private/export separation, sync totals and runtime gating invariants
   - emits `verification_report.json`

## Output files
- `definition_registry.json`
- `definition_registry.csv`
- `orbital_definition_registry.json`
- `internal_subsystem_cards.json`
- `nonlocal_cards_registry.json`
- `horizon_policy_matrix.json`
- `orbital_assignment_report.json`
- `subsystem_sync_registry.json`
- `subsystem_sync_report.json`
- `verification_report.json`
- `nonlocal_definition_edges.json`

## Design principle
The patch does **not** pretend to understand all domain semantics. It first captures structure faithfully, then assigns orbital meaning with explicit confidence, then emits a graph that can be hand-corrected where needed.

## Recursion guard
The definition registry must not ingest its own generated card artifacts. The normalization step removes paths under `integration/registries/definitions/` and stabilizes definition IDs with line numbers so the card graph remains non-self-referential across reruns.

## Database library
The full registry becomes too large and too self-referential as a monolithic JSON export. The database library keeps the catalog queryable, indexed and split by concern (`records`, `internal_cards`, `horizon_policies`, `subsystem_sync`, `reports`, sharded `edges_*`) instead of forcing one gargantuan tracked text artifact.

## Orbital export cards v0.5
Phase 4 extends export cards with synchronization scaffolding.

### Export card fields
- `card_schema`
- `sync_schema`
- `global_attractor_ref`
- `board_card_id`
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
- `tau_local`
- `tau_orbit`
- `tau_system`
- `sync_scope`
- `sync_law_ref`
- `condensation_operator`
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

## Internal subsystem card fields v0.3
- `internal_card_schema`
- `sync_schema`
- `internal_card_id`
- `owner_card_id`
- `owner_horizon_id`
- `board_card_id`
- `container_card_id`
- `subsystem_kind`
- `manybody_role`
- `internal_visibility`
- `internal_candidate_states`
- `internal_conflict_state`
- `internal_superposition_state`
- `internal_resolution_trace`
- `internal_tau_local`
- `internal_tau_orbit`
- `internal_tau_system`
- `sync_scope`
- `sync_law_ref`
- `condensation_operator`
- `internal_memory_mode`
- `projection_operator`
- `privacy_constraint`
- `horizon_transition_profile`
- `exportable_fields`
- `sealed_fields`
- `policy_table_ref`
- `export_card_id`

## Subsystem sync registry
`subsystem_sync_registry.json` formalizes the board/metronome layer.

Each board record defines:
- `board_card_id`
- `tau_orbit`
- `tau_system`
- `sync_law_ref`
- `condensation_operator`
- `member_card_ids`
- `internal_card_ids`
- `orbit_role_distribution`
- `manybody_role_distribution`
- `condensed_half_conclusion`

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

## Integral system layer registration
The orbital card system is now treated as an **integral system layer** rather than a loose export bundle.

The machine-readable integration anchor is:
- `orbital_card_system_integration_manifest.json`

This registration fixes the authoritative upload scope to:
- export registry
- internal subsystem cards
- horizon policy matrix
- subsystem sync registry/report
- database library manifest and shards

Runtime outputs such as bridge reports, `subsystem_sync_manifest.json`, `runtime_gating.json`, and Sapiens packets remain **derived runtime artifacts**, not source-of-truth registry objects.

## Runtime integration
Phase 5 wires the registries into:
- `src/ciel_sot_agent/orbital_bridge.py`
- `src/ciel_sot_agent/sapiens_client.py`

The bridge now emits:
- `subsystem_sync_manifest.json`
- `runtime_gating.json`

The Sapiens packet now carries:
- `subsystem_sync_manifest`
- `runtime_gating`
- a projected export policy where private subsystem state is not exported directly.

## In-repo implementation records
- `integration/registries/definitions/ORBITAL_MANYBODY_IMPLEMENTATION_PLAN.md`
- `integration/registries/definitions/ORBITAL_MANYBODY_TODO.md`
