# CIEL / TIR Information Dynamics — 2026-08-08 Canon Writeback

## Status

`PARTIAL_CANON / IMPLEMENTED_TESTED`

This writeback records only the scope implemented and locally tested on 2026-08-08. It does not promote unresolved physical bindings.

## Relational ethics

New derived closure for historical IDs 041–045:

- 041 Relational Medium
- 042 Relation
- 043 Relational Field
- 044 Ethical Scalar: `E_rel = R_M * A_rel * S_rel`
- 045 Ethical Gradient: `Delta E_rel / Delta tau`

The alignment factor is signed. Constructive and destructive opposition are not collapsed by `abs(dot)`.

Decision semantics use only the derived relational scalar. V36/M0–M11 are runtime/provenance channels and do not assign moral value or break ethical ties.

## Distributional ethics

Per-node and per-edge consequences are exposed. Pareto dominance removes only genuinely dominated alternatives; incomparable tradeoffs remain `UNRESOLVED` rather than receiving arbitrary welfare weights.

## N-body relational Green / Kepler sector

Conditional dimensional theorem under isotropic conserved radial flux:

- `N=2`: `V ~ log(r)`, `|F| ~ r^-1`
- `N>2`: `V_N = -mu / ((N-2) r^(N-2))`, `|F_N| ~ r^(1-N)`
- `N=3`: `V = -mu/r`, `|F| = mu/r^2`

The inverse-distance potential is therefore dimension-selective, not assumed for every N.

The canonical regular tetrahedral frame satisfies:

`sum_i v_i = 0`

`sum_i v_i v_i^T = (4/3) I_3`

A sourced exact radial sector may coexist with a tangential/solenoidal holonomy sector. The latter can preserve Berry/path memory without changing the centered Gauss flux when its radial normal component vanishes.

## U(1) rotor embedding

Constructive embedding:

`psi = sqrt(I_phi/2) exp(i chi)`

maps the background-free scalar-field Noether current to the relational rotor current:

`J = 2 A^2 Dchi = I_phi Dchi`.

This is an exact current embedding inside the constant-modulus rotor sector. It is not a claim that every historical ENB field configuration belongs to that sector.

## Executable information dynamics

Continuity equation:

`partial_t rho_I + div J_I = sigma_I`

Current split:

`J_I = J_phase + J0`

`J_phase = I_phi Dchi`

`J0 = J_background + J_source + J_holonomy + J_boundary`

The implementation includes a conservative finite-volume update with local/global balance receipts. J0 sector semantics are provenance-declared; no threshold classifier infers them from vector magnitude.

## Epistemic firewall

The following are not equivalent:

`observation != hypothesis != candidate != implemented != tested != validated != promoted SoT`

V36 representation is not proof.

## Preregistered predictions

The following remain frozen and **UNTESTED**:

- relative delta approximately `1e-3` (`0.1%`)
- expected significance approximately `6.3 sigma`

They must not be used as fit targets.

## Remaining open work

1. Bind each runtime J0 contribution to a derived/measured TIR source.
2. Couple information-current dynamics back to relational-body state without inserting an arbitrary force coefficient.
3. Derive source/coupling normalization from TIR rather than fitting it.
4. Only after that evaluate the preregistered delta and statistical significance.
