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
- performance/test evidence exists for the new path,
- and the repo-memory / nonlocal card layer is synchronized with the real post-merge state of `main`.

---

## Chronology of plans
1. **Documentation predecessor** — establish repo geometry and execution surfaces before changing orbital runtime.
2. **Phase A** — semantic boundary hardening between analogy / science / operations / executable surfaces.
3. **Phase B** — strict `phased_state.py` contracts.
4. **Phase C** — identity-phase versus selection-relevance separation.
5. **Post-merge normalization** — repair repo-memory surfaces after A/B/C landed.
6. **Phase D** — write orbital-law v0 formal spec before runtime changes.
7. **Phase E** — wire orbital-law runtime path into the orbital engine.
8. **Phase F** — remove first avoidable runtime overheads.
9. **Phase G** — add semantic evidence fixtures and tests.
10. **Post-Phase G stabilization** — restore missing semantic evidence on `main`, add offline dependency bundle scaffold, repair stale repository-map test, and repair offline bootstrap logic.
11. **Current active plan** — refresh nonlocal cards / machine registries and repair the missing write-back or “auto-completion” path so machine-readable state tracks `main` instead of drifting behind it.

---

## Branch and baseline
Historical merged branches:
- `operation/orbital-dynamics-law-v0-phase-a-20260407`
- `operation/orbital-dynamics-law-v0-phase-b-20260407`
- `operation/orbital-dynamics-law-v0-phase-c-20260407`
- `fix/post-merge-normalization-20260408`
- `operation/orbital-dynamics-law-v0-phase-e-20260408`
- `operation/orbital-dynamics-law-v0-phase-f-20260408`

Direct main repair / stabilization commits:
- `a9f16bb5c97657420a09435368fc76e6ca41458b` — restore missing Phase G semantic evidence on `main`
- `5bdd47687653dad8a3bb73fc28837c27b7e6638e` — add offline dependency bundle scaffold and docs
- `b1463dca9cdaf7ff710b6943f49870ade95c997e` — fix stale repository-map test and offline bundle bootstrap
- `870fe16b1171beb41f56f5fb35ca142890f42a68` — offline wheel payload added on `main`

Current baseline from `main`:
- `870fe16b1171beb41f56f5fb35ca142890f42a68`

## Current rationale
Runtime and test surfaces are now operationally green on user-side local offline validation (`python -m pytest -q` full pass after offline install on Python 3.12 / Linux Mint 22.3).

The new dominant inconsistency is no longer runtime law correctness.
It is repo-memory drift:
- `docs/INDEX.md` reflects current repo state,
- but `integration/hyperspace_index.json`, `integration/index_registry.yaml`, `integration/hyperspace_index_orbital.json`, and `integration/index_registry_orbital.yaml` lag behind,
- orbital ledger memory also lags behind post-Phase-G stabilization,
- and the current validator path diagnoses registry problems but does not write refreshed cards back.

That means the next active work is a nonlocal-card / write-back repair, not another blind runtime patch.

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
- [x] operational memory surfaces matched the then-current merged state of `main`

## Status on `main`
- Merged.
- Superseded by later repo-memory drift after Phase G stabilization and offline bundle work.

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
- Runtime path exists and passes current full local test sweep.
- Limitation still open: benchmark/certification evidence is not yet formalized as a dedicated harness.

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

# POST-PHASE G STABILIZATION — OFFLINE / TEST / MAIN REPAIR

## Goal
Stabilize the real `main` branch after Phase G by repairing missing semantic evidence, offline dependency bootstrap, stale repo-map tests, and local full-suite execution.

## Checklist
- [x] restore missing Phase G semantic evidence on `main`
- [x] add offline dependency bundle scaffold and docs
- [x] repair stale `tests/test_repository_machine_map.py` expectations to current `main`
- [x] repair offline bootstrap scripts (`PyYAML` glob + build-backend wheels)
- [x] add offline wheel payload on `main`
- [x] confirm user-side local full `python -m pytest -q` pass after offline install

## Exit criteria
- [x] runtime/test surfaces are green on local offline validation

## Status on `main`
- Merged through direct main stabilization commits.
- Remaining open point: machine-readable bundle manifest and nonlocal cards still lag behind the real post-merge state.

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

# PHASE I — NONLOCAL CARD REFRESH & AUTO-COMPLETION REPAIR

## Goal
Refresh machine-readable nonlocal cards and repair the missing write-back path so repo-memory tracks the real state of `main` instead of drifting behind it.

## Diagnosis
Current behavior:
- `docs/INDEX.md` is fresher than the machine-readable card layer,
- `integration/hyperspace_index.json` and `integration/index_registry.yaml` lag behind current repo surfaces,
- orbital addendum cards also lag behind Phase E/F/G and later stabilization work,
- `index_validator_v2.py` validates and reports issues but does not write refreshed cards back.

## Target files
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`
- `integration/hyperspace_index_orbital.json`
- `integration/index_registry_orbital.yaml`
- `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`
- `vendor/manifests/offline_dependency_bundle_v1.yaml`

## Checklist
- [x] diagnose that current validator path is validate-only, not write-back
- [x] identify stale machine-readable carriers that lag behind `docs/INDEX.md`
- [ ] refresh primary hyperspace index to current `main`
- [ ] refresh primary machine registry to current `main`
- [ ] refresh orbital hyperspace addendum to current `main`
- [ ] refresh orbital machine registry addendum to current `main`
- [ ] update offline bundle manifest from scaffold-only semantics to populated-state semantics where justified by committed wheel payload
- [ ] define or repair a deterministic write-back entrypoint for future auto-refresh
- [ ] add or update a validation/test surface that detects docs > cards drift earlier

## Exit criteria
- [ ] nonlocal cards, registries, and operation memory match the actual merged state of `main`
- [ ] repo has an explicit refresh/write-back path instead of validate-only diagnosis

---

## Current active phase
- [ ] Active: Phase I — Nonlocal Card Refresh & Auto-Completion Repair
- [ ] Optional parallel follow-up later: deeper Phase F analytical/cached gradients
- [ ] Deferred later: Phase H package geometry refactor

## Immediate next action
- [ ] refresh machine-readable nonlocal cards and registries to the current post-offline `main` state before any further structural work

## Successor rule
If this operation is later split into sub-operations, every successor must link back here and record which patchset boundary it inherits.
