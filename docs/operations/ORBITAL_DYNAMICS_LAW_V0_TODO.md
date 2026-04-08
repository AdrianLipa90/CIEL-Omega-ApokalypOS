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
Historical branch provenance:
- `operation/orbital-dynamics-law-v0-phase-a-20260407`
- `operation/orbital-dynamics-law-v0-phase-b-20260407`
- `operation/orbital-dynamics-law-v0-phase-c-20260407`

Normalization branch still open during this work:
- `fix/post-merge-normalization-20260408`

Active Phase E branch stacked on normalization head:
- `operation/orbital-dynamics-law-v0-phase-e-20260408`

Current Phase E baseline from normalization branch head:
- `b92bba8b65664107ac24d073d08474edc0d559dd`

## Current rationale
Current runtime already had:
- relational/orbital dynamics with `rho`, `phi`, `tau`, `spin`, `info_mass`, `q_target`,
- Phase A/B/C semantic groundwork,
- but still lacked an explicit Orbital Law v0 runtime path.

The concrete gap before this patchset was:
- `Sector` had no orbital-law state fields,
- metrics had no `mu_eff` / `tau_orbit` / `phase_slip_ready` helper layer,
- `step()` had no optional `use_orbital_law_v0` path,
- global-pass summaries could not expose orbital-law v0 state even when enabled.

Phase E patchset addresses that runtime gap directly.

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

## Status
- Implemented on `fix/post-merge-normalization-20260408`.
- Not yet merged at the moment this stacked Phase E branch was created.

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

## Phase E progress entry — 2026-04-08
Resolved in this patchset:
- `Sector` now carries `mu_eff`, `winding`, `tau_orbit`, `phase_slip_ready`, and `orbit_stability`,
- `metrics.py` now computes target orbit radius, effective attractor strength, orbital period estimate, stability score, and phase-slip readiness,
- `step()` now supports an explicit optional `use_orbital_law_v0` path layered on top of the existing relational or legacy step,
- global-pass snapshots now expose aggregate orbital-law metrics when the path is enabled,
- runtime tests now verify that enabling the path updates sector fields and reports orbital-law metrics.

Changed files:
- `integration/Orbital/main/model.py`
- `integration/Orbital/main/metrics.py`
- `integration/Orbital/main/dynamics.py`
- `integration/Orbital/main/global_pass.py`
- `tests/test_orbital_runtime.py`
- `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`

Known limitation:
- this patchset implements the optional runtime path and minimal evidence surface, but it is not yet a full benchmark/certification pass.
- post-merge normalization is still stacked underneath this branch until PR #213 lands.

---

# PHASE F — DYNAMICS PERFORMANCE REPAIR

## Goal
Repair the real bottleneck in `step_dynamics` after semantics are fixed.

## Checklist
- [ ] profile `_relational_step()` and `_perturbed_potential()`
- [ ] remove unnecessary `deepcopy`/full recomputation patterns from gradient estimation
- [ ] replace numerical perturbation where possible with cached or analytical gradients
- [ ] repeat benchmark after changes

## Exit criteria
- [ ] performance gains come from mathematical/runtime cleanup, not from hiding the cost behind concurrency

---

# PHASE G — SEMANTIC TEST & BENCH SUITE

## Goal
Produce evidence that orbital law v0 improves runtime semantics or at least does not regress them.

## Checklist
- [ ] add orbital selection benchmarks
- [ ] add precision/recall style relevance fixtures
- [ ] add stability tests for orbit/period/threshold-jump behavior
- [ ] add tests for winding update semantics

## Exit criteria
- [ ] semantic/runtime evidence exists for the new law

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
- [ ] Phase F — Dynamics Performance Repair is the next implementation phase
- [ ] Phase G — Semantic Test & Bench Suite remains the next evidence phase

## Immediate next action
- [ ] profile `_perturbed_potential()` / `_relational_step()` under both baseline and orbital-law-v0 mode before attempting optimization

## Successor rule
If this operation is later split into sub-operations, every successor must link back here and record which patchset boundary it inherits.
