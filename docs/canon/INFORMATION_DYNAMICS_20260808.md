# CIEL / TIR Information Dynamics — 2026-08-08 Canon Writeback

## Status

`PARTIAL_CANON / IMPLEMENTED_TESTED`

This writeback records the current verified closure line. It preserves the distinction:

`observation != hypothesis != candidate != implemented != tested != validated != promoted SoT`.

## Relational ethics

Derived closure for IDs 041–045:

- 041 Relational Medium
- 042 Relation
- 043 Relational Field
- 044 Ethical Scalar: `E_rel = R_M * A_rel * S_rel`
- 045 Ethical Gradient: `Delta E_rel / Delta tau`

The alignment factor is signed. Constructive and destructive opposition are not collapsed by `abs(dot)`.

Decision semantics use only the derived relational scalar. V36/M0–M11 are runtime/provenance channels and do not assign moral value or break ethical ties.

## Distributional ethics and autonomy

Per-node and per-edge consequences are exposed. Pareto dominance removes only genuinely dominated alternatives; incomparable tradeoffs remain `UNRESOLVED` rather than receiving arbitrary welfare weights.

Agency, consent, information asymmetry and coercion are explicit operational observables:

- consent: `AFFIRMED | REFUSED | WITHDRAWN | UNKNOWN | NOT_APPLICABLE`;
- active consent is the latest explicit evidence while full chronology remains preserved;
- `UNKNOWN` is never promoted to `AFFIRMED`;
- information asymmetry is derived from explicit relevant/accessibility sets;
- agency uses feasible and causally controlled action sets;
- coercion uses supplied counterfactual evidence rather than an outcome-based guess.

A larger `E_rel` cannot numerically compensate an explicit refusal, withdrawal or coercive constraint. Genuine cross-axis tradeoffs remain `UNRESOLVED` unless a separate priority is canonized with provenance.

## N-body relational Green / Kepler sector

Conditional dimensional theorem under isotropic conserved radial flux:

- `N=2`: `V ~ log(r)`, `|F| ~ r^-1`
- `N>2`: `V_N = -mu / ((N-2) r^(N-2))`, `|F_N| ~ r^(1-N)`
- `N=3`: `V = -mu/r`, `|F| = mu/r^2`

The inverse-distance potential is dimension-selective, not assumed for every N.

The canonical tetrahedral frame satisfies

`sum_i v_i = 0`

and

`sum_i v_i v_i^T = (4/3) I_3`.

A sourced exact radial sector may coexist with a tangential/solenoidal holonomy sector. The latter can preserve Berry/path memory without changing centered Gauss flux when its radial normal component vanishes.

## U(1) rotor embedding

Constructive embedding:

`psi = sqrt(I_phi/2) exp(i chi)`

maps the background-free scalar-field Noether current to the relational rotor current:

`J_phase = 2 A^2 Dchi = I_phi Dchi`.

This is an exact current embedding inside the constant-modulus rotor sector. It is not a claim that every historical ENB field configuration belongs to that sector.

## Executable information continuity dynamics

Continuity equation:

`partial_t rho_I + div J_I = sigma_I`.

The spatial current split is now canonically named

`J_I = J_phase + J_residual`

with

`J_phase = I_phi Dchi`

and

`J_residual = J_background + J_source + J_holonomy + J_boundary`.

### Notation firewall

`J_residual` is a **vector spatial current**.

It is **not** the Hamiltonian scalar phase offset `J0_phase_offset` appearing in

`J = I_phi D_t chi + J0_phase_offset`.

The former historical use of `J0` for both objects was a symbol collision and has been removed from the runtime API.

The continuity implementation uses a conservative finite-volume update with local/global balance receipts. Residual-current sector semantics are provenance-declared; no threshold classifier infers them from vector magnitude.

## Conservative field-node exchange

For an explicit source partition

`sigma_I = sum_i sigma_i`,

node information contents `Q_i` obey

`dQ_i/dt = - integral sigma_i dV`.

Therefore

`d/dt [ integral rho_I dV + sum_i Q_i ] = - boundary_outflow`.

The implementation rejects unattributed source partitions. This closes information bookkeeping across field and relational nodes. It does **not** identify `Q_i` with mass, energy or canonical momentum.

## Canonical information backreaction

Backreaction is derived from the phase-first Hamiltonian, not from an inserted force coefficient.

Current source equations:

`L = 1/2 g_ab qdot^a qdot^b + I_phi/2 (D_t chi)^2 + J0_phase_offset D_t chi - V(q)`

`J = I_phi D_t chi + J0_phase_offset`

`p_a = g_ab qdot^b + J A_a`

`Pi_a = p_a - J A_a`

`H = (J-J0_phase_offset)^2/(2 I_phi) + 1/2 g^ab Pi_a Pi_b + V(q)`.

For fixed `J`, `J0_phase_offset`, and `I_phi`:

`qdot^a = g^ab Pi_b`

`pdot_k = J (partial_k A_a) qdot^a - 1/2 Pi_a (partial_k g^ab) Pi_b - partial_k V`.

For a coordinate-constant metric:

`Pi_dot_k = J F_ka qdot^a - partial_k V`

with

`F_ka = partial_k A_a - partial_a A_k`.

Thus the geometric backreaction couples through curvature, with canonical phase momentum `J` as the coefficient. A pure-gauge connection with `F=0` produces no geometric force on `Pi`.

## Intention / information phase generator and normalization

The current source line gives

`I_hat_s(tau,k) = kappa W_hat_s + delta I_hat_0(tau,k)`

with

`kappa = ln(2)/(24*pi)`.

The formal derivation note supplies the semiclassical intention charge / phase offset:

`J_I,s(tau,k) = hbar rho_s(k) I_s(tau,k)`.

At the expectation/scalar level used by the classical Hamiltonian:

`J0_phase_offset = hbar rho_s(k) [ kappa <W_s> + <delta I_0> ]`.

This is the correct source-derived bridge. It is **not** the statement `J = <I_hat_s>`.

The free phase energy is correspondingly

`H_phase/free = J0_phase_offset / Delta tau_k`.

The runtime now exposes this binding explicitly and keeps the total canonical momentum `J` distinct from the source/intention offset.

## Source-derived standard geometry

The standard source blocks are implemented directly:

Fubini–Study on the Bloch/CP1 chart:

`g_FS = 1/4 diag(1, sin^2(theta))`.

Berry connection and curvature in the declared gauge:

`A_B = (1-cos(theta))/2 dphi`

`F_B = 1/2 sin(theta) dtheta wedge dphi`.

Poincare disk:

`g_D = 4/(1-u^2-v^2)^2 I_2`, for `u^2+v^2<1`.

The full structural metric remains

`G = g_FS direct_sum g_D direct_sum g_rel`.

A builder now constructs the local Hamiltonian geometry from the source-derived FS/Berry/Poincare blocks plus explicitly supplied nonstandard pieces.

The current source does **not** uniquely specify `g_rel`; it remains OPEN rather than being guessed.

Likewise additional Aharonov–Bohm, Euler and intention connection components are supplied with provenance until their runtime forms are canonically bound.

## PhaseNav / NOEMA vectorization

Canonical information-dynamics nodes have been routed through the existing native PhaseNav stream router as provenance events:

- native binding was `ACTIVE` at the test moment;
- vectors are 36D;
- M0–M11 projection uses 12 lanes;
- append-only commit-chain verification passed.

`V36 != proof`: vectorization can encode a claim's status and provenance but cannot promote an OPEN edge.

## Preregistered predictions

The following remain frozen and **UNTESTED**:

- relative delta approximately `1e-3` (`0.1%`)
- expected significance approximately `6.3 sigma`.

They must not be used as fit targets.

## Current OPEN set

1. Derive or bind the actual runtime `g_rel` rather than supplying a generic relational metric block.
2. Bind Aharonov–Bohm, Euler and intention connection contributions to their current runtime observables with units/provenance.
3. Bind field/node information observables `(rho_I, J_I, Q_i)` to the operator quantities `W_hat_s`, `delta I_hat_0` and rhythm `rho_s(k)` without circular inference.
4. Derive or recover the runtime law for `rho_s(k)` and `delta I_hat_0` where they are not directly supplied by the canonical seed/orbit source.
5. Only after those bindings evaluate the preregistered `delta ~ 0.1%` and statistical `~6.3 sigma`.
