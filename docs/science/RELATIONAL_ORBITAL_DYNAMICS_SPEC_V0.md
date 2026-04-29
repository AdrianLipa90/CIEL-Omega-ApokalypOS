# Relational Orbital Dynamics Specification v0

Status: formal working specification for review

This file defines the minimal effective orbital-law layer intended for the orbital runtime.
It is not yet a claim that the runtime already implements the full law.
It is the target formal contract for the next implementation step.

## Scope

This specification introduces an effective discrete orbital law for information-bearing sectors moving in a relational medium.
It is designed to sit above the current repository/orbital state representation without replacing the existing relational dynamics path.

## Status discipline

- formal working specification: yes
- executable claim already implemented: no
- analogy only: no
- unresolved parts: yes

## Minimal state variables

Each sector is assumed to carry at least the current runtime variables already present in the orbital layer, including:
- `rho`
- `phi`
- `tau`
- `spin`
- `info_mass`
- `q_target`

This law adds the following effective orbital-law variables:
- `mu_eff` — effective attractor strength seen by the sector
- `winding` — discrete count or signed measure of completed orbital wrap relative to the attractor geometry
- `tau_orbit` — orbital-period estimate for the effective orbit
- `phase_slip_ready` — boolean or thresholded indicator that the sector is close to an orbit-class transition

## Intended interpretation

- `rho` is the current orbital radius or distance-to-attractor proxy.
- `q_target` is the current preferred relational radius or attractor radius.
- `mu_eff` is not a gravitational constant imported literally from celestial mechanics.
  It is an effective local parameter encoding how strongly the relational medium holds the sector near its current orbit class.
- `winding` tracks orbital transport history at the level of completed angular circulation.
- `phase_slip_ready` marks when the current orbit is close to a threshold where a discrete jump, bifurcation, or relabeling of orbit class becomes admissible.

## Effective law

The intended v0 law is deliberately minimal.
It states that stable information-bearing orbits satisfy an effective Kepler-type scaling:

`tau_orbit^2 ~ rho^3 / mu_eff`

Operational reading:
- larger orbit radius tends to increase period,
- stronger effective attractor strength tends to shorten period,
- the relation is used as an effective ordering law, not as a claim of literal astrophysical identity.

## Derived helper quantities

The following helper quantities are expected in implementation even if the exact numerical form is refined later:

### Effective attractor strength
`mu_eff = mu_eff(state, couplings, q_target, info_mass, local coherence terms)`

Required property:
- `mu_eff > 0` for sectors considered orbitally bound in the v0 path.

### Radius mismatch
`delta_r = rho - q_target`

Required use:
- `delta_r` feeds stability and transition logic.

### Orbit-class stability score
A stability score should be computable from at least:
- `|delta_r|`
- phase alignment / drift terms
- leak or vorticity terms already present in the runtime
- local coupling pressure or equivalent relational tension

## Phase-slip rule

The v0 path requires an explicit threshold/transition rule.
A sector becomes `phase_slip_ready = true` when the local stability score crosses a critical boundary.

Minimal requirement:
- the rule must be explicit,
- the rule must be deterministic for a fixed input state,
- the rule must separate smooth in-orbit evolution from discrete orbit-class transition.

The exact threshold function is still open.
What is fixed here is the architectural requirement that the threshold be made explicit rather than remain hidden inside ad hoc heuristics.

## Winding update semantics

`winding` should update only when the angular state crosses a defined orbital wrap boundary.

Minimal requirement:
- winding must not be inferred from raw identity phase alone,
- winding must reflect orbital transport history,
- branch-local noise should not create fake completed wraps.

## Compatibility rule

The v0 orbital-law path must be optional.
The existing relational dynamics path remains valid during transition.

Required implementation property:
- a runtime switch such as `use_orbital_law_v0` or equivalent must preserve backward compatibility while allowing targeted tests and benchmarks.

## Non-claims

This file does not claim:
- that the present runtime already satisfies the full law,
- that a literal astrophysical derivation has been imported into the repository,
- that this effective law is already experimentally validated,
- that identity phase alone should drive selection or orbital ranking.

## Crossrefs

- `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`
- `docs/analogies/KEPLER_SUPERFLUID_ANALOGIES.md`
- `integration/Orbital/main/model.py`
- `integration/Orbital/main/dynamics.py`
- `integration/Orbital/main/metrics.py`
