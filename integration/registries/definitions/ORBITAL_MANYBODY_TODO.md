# OPERATION ORBITAL CARD SYSTEM — ACTIVE TODO LEDGER

## Operational law
Before starting any phase:
- [ ] read this file in full
- [ ] confirm current repo/ref and active objective
- [ ] confirm previous phase state

After finishing any phase:
- [ ] update this file as the final step
- [ ] record completed work
- [ ] record blockers / unresolved issues
- [ ] record generated artifacts
- [ ] record next phase readiness

Reporting protocol:
- unchanged
- progress, blockers, problem ⇄ solution, and state updates remain mandatory

---

## Project objective
Build, rerun, validate, and integrate the **Orbital Card System** as a real system layer, not just a generated artifact set.

The project is complete only when:
- the card pipeline reruns cleanly,
- validation artifacts are green,
- runtime consumes the new card layer correctly,
- and upload/integration of the orbital card system is executed as an intentional system step.

---

## Current project state
- [x] legacy phases 1–5 implemented in repo history
- [x] verification infrastructure exists
- [x] bridge/runtime hooks exist
- [ ] fresh operational rerun completed under the new project protocol
- [ ] runtime behavior checked against freshly regenerated artifacts
- [ ] orbital card system uploaded/integrated as an explicit system layer

---

# PHASE A — PREFLIGHT / RERUN READINESS

## Goal
Establish that repo state, tooling, and operational prerequisites are ready for a clean orbital card rerun.

## A1. Repo baseline
- [ ] confirm active target branch/ref
- [ ] confirm no unresolved CI blocker unrelated to orbital cards
- [ ] confirm current TODO has been read before work starts
- [ ] record current starting commit / timestamp in work notes

## A2. Toolchain availability
- [ ] confirm existence of:
  - [ ] `scripts/build_orbital_definition_registry.py`
  - [ ] `scripts/normalize_definition_registry.py`
  - [ ] `scripts/resolve_orbital_semantics.py`
  - [ ] `scripts/build_subsystem_sync_registry.py`
  - [ ] `scripts/build_nonlocal_definition_edges.py`
  - [ ] `scripts/build_definition_db_library.py`
  - [ ] `scripts/verify_orbital_registry_integrity.py`
- [ ] confirm runtime consumers exist:
  - [ ] `src/ciel_sot_agent/orbital_bridge.py`
  - [ ] `src/ciel_sot_agent/sapiens_client.py`

## A3. Preflight checks
- [ ] confirm no known schema mismatch in active card artifacts
- [ ] confirm no blocking DB-builder failure remains
- [ ] confirm tests touching orbital cards / runtime are green enough to proceed or blockers are named explicitly

## A4. Phase exit criteria
- [ ] repo is considered rerun-ready
- [ ] next phase can start

---

# PHASE B — FULL CARD PIPELINE RERUN

## Goal
Regenerate the orbital card layer from source and produce a fresh artifact set.

## B1. Core generation sequence
- [ ] run `build_orbital_definition_registry.py`
- [ ] run `normalize_definition_registry.py`
- [ ] run `resolve_orbital_semantics.py`
- [ ] run `build_subsystem_sync_registry.py`
- [ ] run `build_nonlocal_definition_edges.py`
- [ ] run `build_definition_db_library.py`
- [ ] run `verify_orbital_registry_integrity.py`

## B2. Execution conditions
- [ ] every step exits with code 0
- [ ] no subprocess failure remains
- [ ] no sqlite failure remains
- [ ] no schema serialization failure remains

## B3. Generated artifact capture
- [ ] capture fresh outputs for:
  - [ ] `orbital_definition_registry.json`
  - [ ] `internal_subsystem_cards.json`
  - [ ] `horizon_policy_matrix.json`
  - [ ] `subsystem_sync_registry.json`
  - [ ] `subsystem_sync_report.json`
  - [ ] `nonlocal_definition_edges.json`
  - [ ] `orbital_assignment_report.json`
  - [ ] `verification_report.json`
  - [ ] `db_library/manifest.json`

## B4. Phase exit criteria
- [ ] fresh card artifact set exists
- [ ] pipeline completed without hard failure

---

# PHASE C — ARTIFACT INTEGRITY VALIDATION

## Goal
Confirm that the regenerated card layer is internally coherent.

## C1. Verification report
- [ ] `verification_report.json` exists
- [ ] `verification_report.json["ok"] == true`

## C2. Structural invariants
- [ ] no recursion introduced by generated registry paths
- [ ] export cards do not leak forbidden internal fields
- [ ] every required internal/export link resolves
- [ ] every `board_card_id` resolves to an actual board/root card
- [ ] sync counts agree across registry / report / manifest

## C3. Semantic invariants
- [ ] horizon classes remain complete
- [ ] privacy constraints remain present
- [ ] tau fields remain present where required
- [ ] sync law and condensation operator are preserved

## C4. Phase exit criteria
- [ ] regenerated orbital card layer is formally coherent

---

# PHASE D — DIFF / QUALITY REVIEW

## Goal
Check what changed, not just whether generation succeeded.

## D1. Mandatory diffs
- [ ] compare previous vs fresh:
  - [ ] `orbital_definition_registry.json`
  - [ ] `internal_subsystem_cards.json`
  - [ ] `subsystem_sync_registry.json`
  - [ ] `verification_report.json`
  - [ ] `db_library/manifest.json`

## D2. Review questions
- [ ] did export card count change unexpectedly?
- [ ] did internal card count change unexpectedly?
- [ ] did board count collapse or explode unexpectedly?
- [ ] did tau/sync fields disappear?
- [ ] did horizon policy content drift unexpectedly?
- [ ] did DB manifest stop matching emitted files?

## D3. Phase exit criteria
- [ ] no unexplained semantic degradation
- [ ] no unexplained structural drift

---

# PHASE E — RUNTIME CONSUMPTION CHECK

## Goal
Prove that runtime consumes the freshly generated orbital card layer, rather than merely tolerating stale artifacts.

## E1. Orbital bridge
- [ ] rerun / inspect `orbital_bridge.py`
- [ ] confirm `subsystem_sync_manifest.json` exists
- [ ] confirm `runtime_gating.json` exists
- [ ] confirm bridge report reflects fresh artifact state

## E2. Runtime policy checks
- [ ] `private_state_export_allowed == false`
- [ ] `requires_projection_operator == true`
- [ ] sync manifest is non-empty when expected
- [ ] tau/system coherence fields are present

## E3. Sapiens packet checks
- [ ] rerun / inspect `sapiens_client.py`
- [ ] confirm latest packet includes:
  - [ ] `subsystem_sync_manifest`
  - [ ] `runtime_gating`
  - [ ] `surface_policy`
  - [ ] `inference_contract`
- [ ] confirm no direct private-state export leaks into packet surface

## E4. Phase exit criteria
- [ ] runtime is consuming the fresh orbital card system correctly

---

# PHASE F — PRE-UPLOAD GATE

## Goal
Decide whether the orbital card system is allowed to become an integral system layer.

## F1. Required green conditions
- [ ] Phase A passed
- [ ] Phase B passed
- [ ] Phase C passed
- [ ] Phase D passed
- [ ] Phase E passed

## F2. Blockers
- [ ] if any condition is red, upload is blocked and blocker must be recorded explicitly

## F3. Phase exit criteria
- [ ] explicit READY / BLOCKED decision recorded

---

# PHASE G — ORBITAL CARD SYSTEM UPLOAD / INTEGRATION

## Goal
Upload / register the orbital card system as an integral system component only after all gates are green.

## G1. Upload scope decision
- [ ] confirm whether upload includes only export layer
- [ ] confirm whether upload includes internal cards
- [ ] confirm whether upload includes horizon policy matrix
- [ ] confirm whether upload includes subsystem sync registry
- [ ] confirm whether upload includes DB library

## G2. Integration action
- [ ] perform upload / bootstrap / registration step
- [ ] record exact commit / ref / timestamp of uploaded card state
- [ ] record whether uploaded state is immutable snapshot or living layer

## G3. Phase exit criteria
- [ ] orbital card system is officially integrated as a system component

---

# PHASE H — POST-UPLOAD VALIDATION

## Goal
Confirm that upload/integration did not break runtime or semantic contracts.

## H1. Runtime re-check
- [ ] bridge still works after upload
- [ ] packet still respects projection constraints
- [ ] runtime gating still enforces privacy
- [ ] no silent schema drift introduced by upload step

## H2. System re-check
- [ ] integrated card layer matches uploaded artifact set
- [ ] no post-upload regression in DB / manifest / sync layer

## H3. Phase exit criteria
- [ ] uploaded orbital card system is stable in practice

---

# FINAL PROJECT CLOSURE

## Closure conditions
- [ ] all phases A–H completed or explicitly blocked
- [ ] final status recorded as one of:
  - [ ] `READY_FOR_UPLOAD`
  - [ ] `UPLOADED_AND_STABLE`
  - [ ] `BLOCKED_BY_GENERATION`
  - [ ] `BLOCKED_BY_VALIDATION`
  - [ ] `BLOCKED_BY_RUNTIME`
  - [ ] `BLOCKED_BY_UPLOAD_POLICY`
- [ ] this TODO updated as the final step of the closing pass

## Current active phase
- [ ] Phase A — Preflight / Rerun Readiness
