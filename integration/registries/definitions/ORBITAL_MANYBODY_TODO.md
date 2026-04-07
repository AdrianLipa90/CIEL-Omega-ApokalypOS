# Orbital Many-Body TODO Ledger

## Phase 1 — Card schema v0.2 ✅
- [x] Add plan and TODO docs to repo.
- [x] Extend resolver with deterministic hierarchy fields.
  - [x] derive `container_card_id`
  - [x] derive `manybody_role`
  - [x] derive `subsystem_kind`
  - [x] derive `parent_orbital_role`
  - [x] derive `horizon_id`
  - [x] derive `horizon_class`
  - [x] derive `information_regime`
  - [x] derive `visible_scopes`
  - [x] derive `leak_policy`
  - [x] derive `tau_role`
  - [x] derive `lagrange_roles`
- [x] Extend resolver report counts.
  - [x] `information_regime_counts`
  - [x] `horizon_class_counts`
  - [x] `tau_role_counts`
  - [x] `manybody_role_counts`
  - [x] `lagrange_role_counts`
- [x] Extend DB schema and persistence.
  - [x] records table columns
  - [x] indexes
  - [x] manifest schema bump
- [x] Update README for the card system sector.
- [x] Add/refresh tests for the new card semantics.

## Phase 2 — Systemic privacy and internal cards
- [ ] Define internal/private subsystem card schema.
  - [ ] `internal_card_schema`
  - [ ] `internal_card_id`
  - [ ] `internal_visibility = PRIVATE_SUBSYSTEM_ONLY`
  - [ ] `internal_candidate_states`
  - [ ] `internal_conflict_state`
  - [ ] `internal_superposition_state`
  - [ ] `internal_resolution_trace`
  - [ ] `internal_tau_local`
  - [ ] `internal_memory_mode`
- [ ] Define export/public subsystem card fields.
  - [ ] `export_state`
  - [ ] `export_result`
  - [ ] `export_confidence`
  - [ ] `residual_uncertainty`
- [ ] Define horizon projection rule.
  - [ ] `K_int -> Π_H -> K_ext`
  - [ ] exportable vs internal-only field table
  - [ ] leak-derived vs directly visible fields
- [ ] Extend DB schema / manifest for internal-vs-export distinction.
- [ ] Extend report layer with internal/export counts.

## Phase 3 — Horizon/leak policy formalization
- [ ] Define allowed visibility transition table.
- [ ] Encode first leak policy ruleset.
- [ ] Distinguish sealed vs porous vs transmissive vs observational horizon classes.
- [ ] Attach privacy constraints to each horizon class.

## Phase 4 — Synchronization scaffolding
- [ ] define board/subsystem aggregation object
- [ ] define local/orbit/system tau slots
- [ ] connect cards to synchronization metadata
- [ ] define how internal subsystem state condenses into exportable half-conclusions

## Phase 5 — Runtime integration
- [ ] feed richer cards into orbital runtime
- [ ] feed richer cards into bridge reports
- [ ] feed privacy constraints into export boundaries
- [ ] audit downstream compatibility

## Phase 6 — Verification
- [ ] rerun catalog hook
- [ ] rerun DB library build
- [ ] verify no recursion reintroduced
- [ ] verify deterministic rerun stability
- [ ] verify internal cards are not exported directly
- [ ] verify horizon projection only exports allowed fields
