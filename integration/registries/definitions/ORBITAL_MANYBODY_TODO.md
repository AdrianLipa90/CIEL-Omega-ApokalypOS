# Orbital Many-Body TODO Ledger

## Phase 1 — Card schema v0.2
- [ ] Add plan and TODO docs to repo.
- [ ] Extend resolver with deterministic hierarchy fields.
  - [ ] derive `container_card_id`
  - [ ] derive `manybody_role`
  - [ ] derive `subsystem_kind`
  - [ ] derive `parent_orbital_role`
  - [ ] derive `horizon_id`
  - [ ] derive `horizon_class`
  - [ ] derive `information_regime`
  - [ ] derive `visible_scopes`
  - [ ] derive `leak_policy`
  - [ ] derive `tau_role`
  - [ ] derive `lagrange_roles`
- [ ] Extend resolver report counts.
  - [ ] `information_regime_counts`
  - [ ] `horizon_class_counts`
  - [ ] `tau_role_counts`
  - [ ] `manybody_role_counts`
  - [ ] `lagrange_role_counts`
- [ ] Extend DB schema and persistence.
  - [ ] records table columns
  - [ ] indexes
  - [ ] manifest schema bump
- [ ] Update README for the card system sector.
- [ ] Add/refresh tests for the new card semantics.

## Phase 2 — Horizon/leak policy formalization
- [ ] Define allowed visibility transition table.
- [ ] Encode first leak policy ruleset.
- [ ] Distinguish sealed vs porous vs transmissive horizon classes.

## Phase 3 — Synchronization scaffolding
- [ ] define board/subsystem aggregation object
- [ ] define local/orbit/system tau slots
- [ ] connect cards to synchronization metadata

## Phase 4 — Runtime integration
- [ ] feed richer cards into orbital runtime
- [ ] feed richer cards into bridge reports
- [ ] audit downstream compatibility

## Phase 5 — Verification
- [ ] rerun catalog hook
- [ ] rerun DB library build
- [ ] verify no recursion reintroduced
- [ ] verify deterministic rerun stability
