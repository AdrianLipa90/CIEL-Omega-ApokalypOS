# CIEL / TIR Information Dynamics — 2026-08-08 Canon Writeback

## Status

`PARTIAL_CANON / IMPLEMENTED_TESTED`

Current code truth is verified from current branch contents and compare, not stale summaries.

## Core information dynamics

`partial_t rho_I + div J_I = sigma_I`

Spatial current:

`J_I = J_phase + J_residual`

`J_phase = I_phi Dchi`

`J_residual = J_background + J_source + J_holonomy + J_boundary`.

`J_residual` is a vector current and is not the Hamiltonian scalar `J0_phase_offset`.

## Canonical phase-first backreaction

`J = I_phi D_t chi + J0_phase_offset`

`p_a = g_ab qdot^b + J A_a`

`Pi_a = p_a - J A_a`

`H = (J-J0_phase_offset)^2/(2 I_phi) + 1/2 g^ab Pi_a Pi_b + V`.

For coordinate-constant metric:

`Pi_dot_k = J F_ka qdot^a - partial_k V`.

Thus backreaction is source-derived minimal coupling; no fitted force coefficient is introduced.

## Information/intention generator normalization

`I_hat_s = kappa W_hat_s + delta I_hat_0`, with `kappa=ln(2)/(24*pi)`.

Formal semiclassical charge / phase offset:

`J0_phase_offset = J_I,s = hbar rho_s(k) [kappa <W_s> + <delta I_0>]`.

This is the correct bridge. It is not `J=<I_hat_s>`.

### Structural operator W_s

The later Debt-1 derivation conditionally closes the formal generator as

`W_hat_s = -i L_{V_s}`

where `V_s` is a seed-selected Killing field on `CP1 ~= S2_Bloch`.

For an axial chart `V=partial_phi`,

`W exp(i m phi) = m exp(i m phi)`.

The runtime now includes the exact finite Fourier-mode representation and computes `<W_s>` from a supplied state rather than from a scalar proxy. This closes the **formal geometric operator**. The physical axis-selection law remains model-dependent / supplied with provenance.

### Still-open generator inputs

The current sources explicitly do **not** canonize:

- the exact project rhythm `rho_s(k)`; the logarithmic/parity forms remain reference/default rules rather than derived canon;
- the law of `delta I_hat_0(tau)`; deterministic, stochastic, semiclassical and operator-valued variants remain open choices.

The implementation therefore accepts these as explicit inputs and marks their laws OPEN instead of fabricating them.

## Source-derived standard geometry

`g_FS = 1/4 diag(1,sin^2 theta)`

`A_B = (1-cos theta)/2 dphi`

`F_B = 1/2 sin theta dtheta wedge dphi`

`g_D = 4/(1-u^2-v^2)^2 I_2`

and structurally

`G = g_FS direct_sum g_D direct_sum g_rel`.

## Source-derived ABE/Euler connection

`A_ABE = A_AB + A_B + A_E`

with

`A_AB = (q_e/hbar) A_em`

`A_B = i<u|du>`

`A_E = s_E omega_E`, and `s_E=1/2` in the spin-half sector.

Berry–Euler curvature:

`F_BE = F_B + s_E R_E`.

The intention trace in the quantum covariant momentum remains separate:

`Pi_hat_a = -i hbar nabla_a - hbar alpha_s A_ABE,a - lambda_s I_a`.

Euler–Berry closure defect:

`epsilon_EB = [Phi_AB + Phi_B + s_E integral R_E + Theta_I]/(2*pi) - D`.

Exact closure means `epsilon_EB=0`; empirical `epsilon_star` must be supplied/calibrated.

## Local relational metric from TIR action

At coherent overlap,

`S_rel = -kappa log R`

has Hessian

`g_rel_local = (2*kappa/d) [I - (1/d) 11^T]`.

Properties:

- one null direction = global U(1) phase;
- rank `d-1`;
- positive definite on the horizontal quotient `sum delta_j=0`;
- Moore–Penrose inverse is the exact inverse on that quotient;
- for `d=36`, the single-coordinate quadratic coefficient is `kappa*35/36^2 = 0.00024827179801127847`.

This closes local coherent-point `g_rel`. A unique global/nonlinear extension remains OPEN.

## N-body / Kepler epistemic correction

The preregistered direct TIR test remains visible:

- direct local `TIR action -> 1/r`: **FAIL**;
- local TIR action quadratic/harmonic: **PASS**;
- simple reciprocal overlap `1/z -> 1/r`: **FAIL**.

The separate B3 Green theorem remains valid under its premise.

### Constructive rotor field lift

The source-supported constant-modulus embedding

`psi = sqrt(I_phi/2) exp(i chi)`

makes the scalar-field Noether current exactly

`J^mu = 2 A^2 D^mu chi = I_phi D^mu chi`.

This is now classified as

`CONSTRUCTIVE_EMBEDDED_SECTOR_EXACT`.

For a static centered radial configuration on Euclidean `B3`, conservation gives

`r^2 I_phi chi'(r)=C`,

hence

`chi'(r)=C/(I_phi r^2)`

and

`chi(r)=chi_0-C/(I_phi r)`.

Therefore the inverse-square gradient / inverse-distance phase profile is exact **inside this constructed constant-modulus radial sector**.

The stronger statement that every finite-dimensional relational state uniquely induces this local physical B3 field remains

`OPEN_NOT_UNIQUE_NOT_VALIDATED`.

No direct `S_rel -> 1/r` map is canonized.

## Conservative field-node exchange

For `sigma_I=sum_i sigma_i` and node information `Q_i`:

`dQ_i/dt = - integral sigma_i dV`

so

`d/dt[integral rho_I dV + sum_i Q_i] = -boundary_outflow`.

## Relational/ethical closure

041–045 relational medium/field/scalar/gradient are implemented with signed `E_rel=R_M*A_rel*S_rel` and no arbitrary moral threshold. Local/Pareto ethics and autonomy v7 preserve explicit refusal/withdrawal/unknown consent and surface coercion/information asymmetry without a weighted moral sum.

## CI status note

The `ci` workflow on head `ec44f849...` failed during pytest **collection**, before the newly added information-dynamics tests executed. The observed blockers were legacy repository/import environment issues: missing `psutil`, missing `ciel_secret_loader`, unavailable `HolonomicMemoryOrchestrator`, and missing `integration.information_flow`. Ruff passed. These failures are not silently reclassified as failures of the new mathematical modules; they remain repository CI blockers until separately repaired.

## PhaseNav/NOEMA

Earlier canonical nodes were routed through native PhaseNav provenance envelopes: 36D, M0–M11/12 lanes, append-only verified chain. Binding was ACTIVE at the relevant test moments. `V36 != proof`.

New v3 nodes are `PENDING_RUNTIME_REPROBE` because the active execution container no longer has the previously assembled native runtime mounted after reset. No pseudo-vectorization is substituted.

## Current OPEN set

1. Derive or select with provenance the physical axis law for `V_s`; the Killing operator itself is conditionally closed.
2. Define a project-canonical `rho_s(k)` tied to geometry rather than a reference placeholder.
3. Define the fluctuation law for `delta I_hat_0(tau)`.
4. Derive a global/nonlinear extension of local Hessian `g_rel`, or prove local quotient scope is sufficient.
5. Bind runtime `A_em`, `omega_E`, intention trace `I_a`, `alpha_s`, and `lambda_s` from provenance-bearing observables.
6. Bind continuous field/node observables to the remaining generator inputs without circular inference.
7. Repair legacy CI collection blockers and re-run the full suite.
8. Re-probe native PhaseNav runtime and vectorize the new canon nodes.
9. Only then evaluate frozen preregistration: `delta~0.1%`, `~6.3 sigma`.

## Invariant

`observation != hypothesis != candidate != implemented != tested != validated != promoted SoT`.

`V36 != proof`.
