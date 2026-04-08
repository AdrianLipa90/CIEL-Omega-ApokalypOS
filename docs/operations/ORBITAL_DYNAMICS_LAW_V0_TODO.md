# OPERATION ORBITAL DYNAMICS LAW V0 — ACTIVE TODO LEDGER

## Operational law
Before starting any phase:
- [ ] read this file in full
- [ ] confirm current repo/ref and active objective
- [ ] confirm predecessor handoff state

After finishing any phase:
- [ ] update this file as the final step
- [ ] record completed work
- [ ] record blockers / unresolved issues
- [ ] record changed files
- [ ] record next phase readiness
- [ ] record predecessor/successor links if the operation is split or handed off

Session handoff reference:
- `docs/operations/CIEL_REPO_WORKSTYLE_SESSION_HANDOFF.md`

Reporting protocol:
- unchanged
- progress, blockers, problem ⇄ solution, and state updates remain mandatory

---

## Predecessor operation
This operation is the direct successor to:
- [`DOCUMENTATION_CONSISTENCY_AND_COVERAGE_TODO.md`](./DOCUMENTATION_CONSISTENCY_AND_COVERAGE_TODO.md)

The documentation operation established the repo geometry, execution surfaces, packaging truth, and machine-readable repo maps needed before orbital runtime changes can be introduced safely.

---

## Project objective
Introduce **Orbital Dynamics Law v0** as an effective, discrete orbital law for stable information-bearing orbits in a relational medium, without mixing:
- analogy,
- hypothesis,
- formal executable claim,
- and runtime implementation.

The operation is complete only when:
- semantic boundaries are hardened,
- phased-state contracts are explicit,
- orbital selection is separated from raw identity phase,
- the formal spec for orbital dynamics v0 exists,
- runtime v0 law is wired in without semantic regression,
- and performance/test evidence exists for the new path.

---

## Branch and baseline
Historical merged branches:
- `operation/orbital-dynamics-law-v0-phase-a-20260407`
- `operation/orbital-dynamics-law-v0-phase-b-20260407`
- `operation/orbital-dynamics-law-v0-phase-c-20260407`
- `fix/post-merge-normalization-20260408`
- `operation/orbital-dynamics-law-v0-phase-e-20260408`
- `operation/orbital-dynamics-law-v0-phase-f-20260408`

Phase G direct-repair commit target:
- `main`

Current direct-repair baseline from `main`:
- `594d9cd9a613d86ea48849098dfa35a1fdbbf2a7`

## Current rationale
History on `main` shows merge commit `#219`, but the semantic evidence files were not actually present in the repository state afterwards.
That means Phase G became a repo-state inconsistency rather than a purely logical next phase.

This direct repair exists to restore the missing evidence layer on `main` itself:
- relevance fixture,
- semantic evidence tests,
- index visibility,
- and the correct ledger state.

---

# PHASE A — SEMANTIC BOUNDARY HARDENING

## Goal
Make the boundary between analogy, science, architecture, operations, and executable runtime machine-visible and review-stable.

## Deliverables
- `docs/science/RELATIONAL_ORBITAL_DYNAMICS_SPEC_V0.md`
- `docs/analogies/KEPLER_SUPERFLUID_ANALOGIES.md`
- updated documentation classification / cross-reference layer

## Checklist
- [x] confirm document status taxonomy: `analogy`, `science`, `architecture`, `operations`, `report`, `archive`
- [x] update surviving docs index / navigation layer to reflect taxonomy
- [x] add formal orbital dynamics spec stub in `docs/science/`
- [x] add Kepler/superfluid analogies note in `docs/analogies/`
- [x] ensure analogy documents are not referenced as executable claims

## Exit criteria
- [ ] analogy and formal spec are no longer confusable in repo navigation or validation

## Phase A status on `main`
- Merged.
- Remaining open point: no automated classification/validation hook yet checks that future docs preserve the boundary.

---

# PHASE B — PHASED STATE CONTRACTS

## Goal
Make the input/domain contracts of `phased_state.py` explicit.

## Decision target
Prefer a **strict contract model** unless implementation review proves permissive wrapping is required.

## Checklist
- [x] decide strict contract for `compute_phase(h)`
- [x] decide strict contract for `f_conn(r)`
- [x] implement explicit validation in `src/ciel_sot_agent/phased_state.py`
- [x] add boundary tests in `tests/test_phased_state.py`
- [x] document the chosen domain contract

## Exit criteria
- [x] there are no silent or ambiguous domain assumptions in phased-state entry functions

## Phase B status on `main`
- Merged.
- Contract state: `compute_phase(h)` accepts only a finite real hash fraction in `[0.0, 1.0)`, and `f_conn(r)` accepts only a non-negative integer connection count.

---

# PHASE C — RELATIONAL SEED SEPARATION

## Goal
Separate identity phase from selection relevance.

## Checklist
- [x] preserve deterministic identity phase for object identity
- [x] define relational selection features (layer, provenance, crossrefs, anchors, sector role, upstream/downstream)
- [x] introduce `selection_weight` / `relational_relevance`
- [x] refit phased-state gating so amplitude/energy acts over relevance, not raw identity seed
- [x] create benchmark-style fixtures comparing identity-phase drift vs relevance-stable selection

## Exit criteria
- [ ] orbital selection correlates with relevance instead of merely with deterministic object identity

## Phase C status on `main`
- Merged.
- Resolved in code: hash-derived `h` now drives only `phi`, while selection/amplitude flows through explicit relational metadata.
- Remaining open point: the broader repo-wide audit of all possible selector surfaces is still not complete.

---

# POST-MERGE NORMALIZATION — AUDIT FOLLOW-UP

## Goal
Normalize repo-memory surfaces after Phase A/B/C landed on `main`.

## Checklist
- [x] remove stale branch-era status from `agentcrossinfo.md`
- [x] normalize orbital ledger wording from branch-local to main-canonical state
- [x] add `tests/test_phased_state.py` to `docs/INDEX.md`
- [x] remove phased-state legacy residue and stale module wording

## Exit criteria
- [x] operational memory surfaces match the actual merged state of `main`

## Status on `main`
- Merged.

---

# PHASE D — ORBITAL DYNAMICS SPEC V0

## Goal
Write the formal orbital law before changing runtime behavior.

## Minimal formal state targets
- [x] `mu_eff`
- [x] `winding`
- [x] `tau_orbit`
- [x] `phase_slip_ready`
- [x] `rho <-> q_target` relation
- [x] effective Kepler-type law `T^2 ~ rho^3 / mu_eff`
- [x] threshold/phase-slip transition rule

## Exit criteria
- [x] a short, reviewable orbital dynamics law v0 exists as formal spec

---

# PHASE E — ORBITAL LAW RUNTIME V0

## Goal
Introduce the effective orbital law into the existing orbital runtime without destroying current relacyjny dynamics.

## Target files
- `integration/Orbital/main/model.py`
- `integration/Orbital/main/metrics.py`
- `integration/Orbital/main/dynamics.py`
- `integration/Orbital/main/global_pass.py`
- `tests/test_orbital_runtime.py`

## Checklist
- [x] extend `Sector` with orbital-law fields
- [x] add effective attractor strength and period helpers
- [x] add phase-slip readiness computation
- [x] add optional `use_orbital_law_v0` path
- [x] keep compatibility with current relational dynamics path

## Exit criteria
- [x] runtime contains an effective discrete orbital law path v0

## Status on `main`
- Merged.
- Limitation still open: runtime path exists, but benchmark/certification evidence is not yet complete.

---

# PHASE F — DYNAMICS PERFORMANCE REPAIR

## Goal
Repair the real bottleneck in `step_dynamics` after semantics are fixed.

## Checklist
- [x] profile `_relational_step()` and `_perturbed_potential()` by code-path audit
- [x] remove unnecessary `deepcopy`/full recomputation patterns from gradient estimation
- [ ] replace numerical perturbation where possible with cached or analytical gradients
- [ ] repeat benchmark after changes

## Exit criteria
- [ ] performance gains come from mathematical/runtime cleanup, not from hiding the cost behind concurrency

## Status on `main`
- Merged.
- Limitation still open: analytical/cached gradient rewrite and benchmark pass are not yet done.

---

# PHASE G — SEMANTIC TEST & BENCH SUITE

## Goal
Produce evidence that orbital law v0 improves runtime semantics or at least does not regress them.

## Checklist
- [x] add orbital selection benchmarks
- [x] add precision/recall style relevance fixtures
- [x] add stability tests for orbit/period/threshold-jump behavior
- [x] add tests for winding update semantics

## Exit criteria
- [x] semantic/runtime evidence exists for the new law

## Phase G direct-repair entry — 2026-04-08
Resolved in this repair:
- added `tests/fixtures/orbital_selection_relevance.json` as a precision/recall-style relevance fixture,
- added `tests/test_orbital_semantics.py` covering relevance ranking, orbital period monotonicity, explicit phase-slip threshold behavior, and winding updates across a `2π` boundary,
- updated `docs/INDEX.md` so the new semantic evidence surfaces are visible in repo navigation,
- corrected this ledger so Phase G is represented as actually present on `main`, not only in merge history.

Changed files:
- `tests/fixtures/orbital_selection_relevance.json`
- `tests/test_orbital_semantics.py`
- `docs/INDEX.md`
- `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`

Known limitation:
- this is still test/fixture evidence, not a performance benchmark harness or empirical certification suite.

---

# PHASE H — PACKAGE GEOMETRY REFACTOR (LATE)

## Goal
Refactor package geometry only after semantics and runtime law stabilize.

## Checklist
- [ ] decide target subpackage layout (`core`, `orbital`, `github`, `sapiens`, `validation`, `gui`)
- [ ] preserve compatibility imports
- [ ] migrate docs and entrypoints only after law/test layers are stable

## Exit criteria
- [ ] package geometry reflects stable semantics rather than forcing them prematurely

---

## Current active phase
- [ ] No mandatory orbital-law phase is blocked on semantics now.
- [ ] Optional next engineering phase: deeper Phase F follow-up (analytical/cached gradients).
- [ ] Optional next structural phase: Phase H package geometry refactor later.

## Immediate next action
- [ ] decide whether the next patch should target analytical/cached gradients or shift to package-geometry cleanup after the semantic evidence layer is restored on `main`.

## Successor rule
If this operation is later split into sub-operations, every successor must link back here and record which patchset boundary it inherits.
