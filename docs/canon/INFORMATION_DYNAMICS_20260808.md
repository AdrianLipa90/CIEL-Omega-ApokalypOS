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

## Source-derived standard geometry

`g_FS = 1/4 diag(1,sin^2 theta)`

`A_B = (1-cos theta)/2 dphi`

`F_B = 1/2 sin theta dtheta wedge dphi`

`g_D = 4/(1-u^2-v^2)^2 I_2`

and structurally

`G = g_FS direct_sum g_D direct_sum g_rel`.

## Source-derived ABE/Euler connection

The formal Phase-Intention note defines

`A_ABE = A_AB + A_B + A_E`

with

`A_AB = (q_e/hbar) A_em`

`A_B = i<u|du>`

`A_E = s_E omega_E`, and `s_E=1/2` in the spin-half sector.

Berry–Euler curvature is

`F_BE = F_B + s_E R_E`.

The intention trace in the quantum covariant momentum is kept separate:

`Pi_hat_a = -i hbar nabla_a - hbar alpha_s A_ABE,a - lambda_s I_a`.

Therefore `I_a` must not be silently folded into `A_ABE`.

Euler–Berry closure defect is

`epsilon_EB = [Phi_AB + Phi_B + s_E integral R_E + Theta_I]/(2*pi) - D`.

Exact closure means `epsilon_EB=0`. Any empirical tolerance `epsilon_star` remains caller-supplied/calibrated; no default threshold is canonized.

## Local relational metric from TIR action

The preregistered direct derivation test found

`S_rel = -kappa log R`

and, for phase displacements around coherent overlap,

`S_rel = kappa[(1/d) sum delta_j^2 - (1/d^2)(sum delta_j)^2] + higher order`.

Therefore the coherent-point Hessian supplies a non-arbitrary local relational metric:

`g_rel_local = (2*kappa/d) [I - (1/d) 11^T]`.

Properties:

- one null direction = global U(1) phase;
- rank `d-1`;
- positive definite on the horizontal quotient `sum delta_j=0`;
- Moore–Penrose inverse is the exact inverse on that quotient;
- for `d=36`, the single-coordinate quadratic coefficient is exactly `kappa*35/36^2 = 0.00024827179801127847`.

This closes **local coherent-point `g_rel`**. A unique global/nonlinear extension away from the coherent chart remains OPEN.

## Relational/ethical closure

041–045 relational medium/field/scalar/gradient are implemented with signed `E_rel=R_M*A_rel*S_rel` and no arbitrary moral threshold. Local/Pareto ethics and autonomy v7 preserve explicit refusal/withdrawal/unknown consent and surface coercion/information asymmetry without a weighted moral sum.

## N-body / Kepler epistemic correction

The preregistered direct TIR test must remain visible:

- direct local `TIR action -> 1/r`: **FAIL**;
- local TIR action is quadratic/harmonic type: **PASS**;
- simple reciprocal overlap `1/z -> 1/r`: **FAIL**.

This does not invalidate the separate B3 Green theorem.

For a centered isotropic conserved radial flux on Euclidean `B3`:

- `V = A + B/r`;
- `|grad V| ~ 1/r^2`;
- Gauss flux is radius-independent.

The current factorized bridge is therefore:

1. project geometry -> `B3`, `rho_TIR=||r||`: source-supported;
2. centered isotropic conserved B3 flux -> `1/r^2`: exact conditional theorem;
3. cyclic chi -> conserved finite-dimensional phase charge `J`: source-supported;
4. `J -> local conserved J^mu on B3`: **OPEN field-lift lemma**;
5. identification with a physical gravitational source/coupling: **OPEN**.

No direct `S_rel -> 1/r` map is canonized.

## Conservative field-node exchange

For `sigma_I=sum_i sigma_i` and node information `Q_i`:

`dQ_i/dt = - integral sigma_i dV`

so

`d/dt[integral rho_I dV + sum_i Q_i] = -boundary_outflow`.

## PhaseNav/NOEMA

Earlier canonical nodes were routed through native PhaseNav provenance envelopes: 36D, M0–M11/12 lanes, append-only verified chain. Binding was ACTIVE at the relevant test moments. `V36 != proof`.

New v3 nodes (`ABE/Euler`, local Hessian `g_rel`, direct-TIR-Kepler FAIL receipt) are currently `PENDING_RUNTIME_REPROBE` because the active execution container no longer has the previously assembled native runtime mounted after reset. No pseudo-vectorization is substituted.

## Current OPEN set

1. Derive/validate the finite-dimensional `J -> local J^mu` B3 field lift rather than assuming it.
2. Derive a global/nonlinear extension of the local Hessian `g_rel`, or prove the local quotient metric is the intended runtime scope.
3. Bind runtime electromagnetic `A_em`, Euler/spin `omega_E`, intention trace `I_a`, `alpha_s`, and `lambda_s` from provenance-bearing runtime observables.
4. Bind `(rho_I,J_I,Q_i)` to `W_hat_s`, `delta I_hat_0`, and `rho_s(k)` without circular inference.
5. Re-probe native PhaseNav runtime and vectorize the new v3 canon nodes.
6. Only then evaluate the frozen preregistration: `delta~0.1%`, `~6.3 sigma`.

## Invariant

`observation != hypothesis != candidate != implemented != tested != validated != promoted SoT`.

`V36 != proof`.
