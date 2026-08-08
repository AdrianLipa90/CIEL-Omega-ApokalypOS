# CIEL / TIR Information Dynamics — 2026-08-08 Canon Writeback

## Status

`PARTIAL_CANON / IMPLEMENTED_TESTED`

Current code truth is verified from the branch contents and compare, not from possibly lagging PR metadata.

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

## Source-derived geometry

`g_FS = 1/4 diag(1,sin^2 theta)`

`A_B = (1-cos theta)/2 dphi`

`F_B = 1/2 sin theta dtheta wedge dphi`

`g_D = 4/(1-u^2-v^2)^2 I_2`

and structurally

`G = g_FS direct_sum g_D direct_sum g_rel`.

FS/Berry/Poincare blocks are implemented. `g_rel` remains OPEN because the current source does not give a unique form.

## Relational/ethical closure

041–045 relational medium/field/scalar/gradient are implemented with signed `E_rel=R_M*A_rel*S_rel` and no arbitrary moral threshold. Local/Pareto ethics and autonomy v7 preserve explicit refusal/withdrawal/unknown consent and surface coercion/information asymmetry without a weighted moral sum.

## N-body Kepler sector

Under isotropic conserved radial flux:

- N=2: `V~log r`
- N>2: `V~-1/((N-2)r^(N-2))`
- N=3: `V=-mu/r`, `|F|=mu/r^2`.

The sourced exact radial sector may coexist with flux-free tangential holonomy.

## Conservative field-node exchange

For `sigma_I=sum_i sigma_i` and node information `Q_i`:

`dQ_i/dt = - integral sigma_i dV`

so

`d/dt[integral rho_I dV + sum_i Q_i] = -boundary_outflow`.

## PhaseNav/NOEMA

Canonical nodes have been routed through native PhaseNav provenance envelopes: 36D, M0–M11/12 lanes, append-only verified chain. Binding was ACTIVE at the test moment. `V36 != proof`.

## Current OPEN set

1. Derive/bind runtime `g_rel`.
2. Bind AB/Euler/intention connection components beyond the explicit Berry block.
3. Bind `(rho_I,J_I,Q_i)` to `W_hat_s`, `delta I_hat_0`, and `rho_s(k)` without circular inference.
4. Recover/derive any generator input not directly supplied by canonical seed/orbit provenance.
5. Then test the frozen preregistration: `delta~0.1%`, `~6.3 sigma`.

## Invariant

`observation != hypothesis != candidate != implemented != tested != validated != promoted SoT`.
