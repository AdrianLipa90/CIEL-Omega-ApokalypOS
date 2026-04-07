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
- original planned operation branch recorded in the first draft: `operation/orbital-dynamics-law-v0-20260407`
- active Phase A branch after post-merge rebase on current main: `operation/orbital-dynamics-law-v0-phase-a-20260407`
- active Phase B branch from current `main`: `operation/orbital-dynamics-law-v0-phase-b-20260407`
- current Phase B baseline from `main`: `4e8b8629df7aa6a62bfe3acbb7cfd0a2a517cbb2`

## Current rationale
Current `main` already contains:
- orbital runtime structures with `rho`, `phi`, `tau`, `spin`, `info_mass`, `q_target`,
- relacyjny step dynamics with potential gradients, leak and vorticity,
- documentation sectors for analogies and science,
- Phase A semantic boundary docs,
- but still lacked explicit phased-state domain contracts,
- and still lacked dedicated boundary tests for the phased-state entry functions.

Phase B patchset resolves those phased-state entry-contract gaps on a dedicated branch.
It also adds an explicit session-handoff workstyle document and links it into the repo's primary orientation surfaces.

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

## Phase A progress entry — 2026-04-07
Completed on branch:
- `docs/science/RELATIONAL_ORBITAL_DYNAMICS_SPEC_V0.md`
- `docs/analogies/KEPLER_SUPERFLUID_ANALOGIES.md`
- `docs/INDEX.md`

Resolved in this patchset:
- the formal orbital-law target now exists as a separate science document,
- the Kepler/superfluid explanatory layer now exists as an explicit analogy document,
- docs navigation now carries an explicit taxonomy instead of leaving status implicit.

Remaining blocker before closing Phase A:
- no validation or automated classification hook yet checks that future docs preserve this boundary.

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

## Phase B progress entry — 2026-04-07
Chosen contract:
- `compute_phase(h)` accepts only a finite real hash fraction in `[0.0, 1.0)`.
- `f_conn(r)` accepts only a non-negative integer connection count.
- permissive wrapping and silent coercion were explicitly rejected.

Changed files:
- `src/ciel_sot_agent/phased_state.py`
- `tests/test_phased_state.py`
- `docs/operations/CIEL_REPO_WORKSTYLE_SESSION_HANDOFF.md`
- `docs/INDEX.md`
- `docs/OPERATIONS.md`
- `AGENT.md`
- `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`

Resolved in this patchset:
- phased-state entry functions now fail explicitly on invalid domain values,
- the contract is documented in the module docstring and this ledger,
- a dedicated boundary-test layer now exists for the module,
- immediate session-orientation and handoff logic now exists as an explicit operations document linked from the main repo orientation surfaces.

Known limitation:
- full repo test execution was not performed inside this GitHub patchset flow; only the contract logic itself was checked during patch construction.

---

# PHASE C — RELATIONAL SEED SEPARATION

## Goal
Separate identity phase from selection relevance.

## Checklist
- [ ] preserve deterministic identity phase for object identity
- [ ] define relational selection features (layer, provenance, crossrefs, anchors, sector role, upstream/downstream)
- [ ] introduce `selection_weight` / `relational_relevance`
- [ ] refit orbital gating so it acts over relevance, not raw identity seed
- [ ] create benchmark fixtures comparing orbital selection vs baseline selection

## Exit criteria
- [ ] orbital selection correlates with relevance instead of merely with deterministic object identity

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

## Checklist
- [ ] extend `Sector` with orbital-law fields
- [ ] add effective attractor strength and period helpers
- [ ] add phase-slip readiness computation
- [ ] add optional `use_orbital_law_v0` path
- [ ] keep compatibility with current relational dynamics path

## Exit criteria
- [ ] runtime contains an effective discrete orbital law path v0

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
- [x] Phase B — Phased State Contracts advanced on branch
- [ ] Phase C — Relational Seed Separation is the next implementation phase

## Immediate next action
- [ ] audit where raw identity phase leaks into selection logic, then define `selection_weight` / `relational_relevance`

## Successor rule
If this operation is later split into sub-operations, every successor must link back here and record which patchset boundary it inherits.
