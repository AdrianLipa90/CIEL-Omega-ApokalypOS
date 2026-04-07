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
- planned operation branch: `operation/orbital-dynamics-law-v0-20260407`
- branch start baseline from current `main`: `b3ec634c24999545f66106b5f2eef70a639ace5a`

## Current rationale
Current `main` already contains:
- orbital runtime structures with `rho`, `phi`, `tau`, `spin`, `info_mass`, `q_target`,
- relacyjny step dynamics with potential gradients, leak and vorticity,
- documentation sectors for analogies and science,
- but still lacks a clean separation between identity phase and selection relevance,
- still lacks explicit orbital law state (`mu_eff`, winding, phase-slip readiness, period law),
- and still carries non-explicit phased-state domain contracts.

---

# PHASE A — SEMANTIC BOUNDARY HARDENING

## Goal
Make the boundary between analogy, science, architecture, operations, and executable runtime machine-visible and review-stable.

## Deliverables
- `docs/science/RELATIONAL_ORBITAL_DYNAMICS_SPEC_V0.md`
- `docs/analogies/KEPLER_SUPERFLUID_ANALOGIES.md`
- updated documentation classification / cross-reference layer

## Checklist
- [ ] confirm document status taxonomy: `analogy`, `science`, `architecture`, `operations`, `report`, `archive`
- [ ] update docs indices/matrix to reflect taxonomy
- [ ] add formal orbital dynamics spec stub in `docs/science/`
- [ ] add Kepler/superfluid analogies note in `docs/analogies/`
- [ ] ensure analogy documents are not referenced as executable claims

## Exit criteria
- [ ] analogy and formal spec are no longer confusable in repo navigation or validation

---

# PHASE B — PHASED STATE CONTRACTS

## Goal
Make the input/domain contracts of `phased_state.py` explicit.

## Decision target
Prefer a **strict contract model** unless implementation review proves permissive wrapping is required.

## Checklist
- [ ] decide strict vs permissive contract for `compute_phase(h)`
- [ ] decide strict vs permissive contract for `f_conn(r)`
- [ ] implement explicit validation in `src/ciel_sot_agent/phased_state.py`
- [ ] add boundary tests in `tests/test_phased_state.py`
- [ ] document the chosen domain contract

## Exit criteria
- [ ] there are no silent or ambiguous domain assumptions in phased-state entry functions

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
- [ ] `mu_eff`
- [ ] `winding`
- [ ] `tau_orbit`
- [ ] `phase_slip_ready`
- [ ] `rho <-> q_target` relation
- [ ] effective Kepler-type law `T^2 ~ rho^3 / mu_eff`
- [ ] threshold/phase-slip transition rule

## Exit criteria
- [ ] a short, reviewable orbital dynamics law v0 exists as formal spec

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
- [ ] Phase A — Semantic Boundary Hardening

## Immediate next action
- [ ] open Patchset A on the branch and land the semantic boundary hardening/doc-classification layer first

## Successor rule
If this operation is later split into sub-operations, every successor must link back here and record which patchset boundary it inherits.
