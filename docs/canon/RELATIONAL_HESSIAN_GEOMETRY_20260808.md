# TIR Relational Hessian Geometry — 2026-08-08

## Status

`DERIVED_GLOBAL_ACTION_HESSIAN / REGIONAL_RIEMANNIAN_METRIC`

## Source action

For phase coordinates `phi_j`:

`z(phi) = (1/d) sum_j exp(i phi_j)`

`R(phi) = |z(phi)|^2`

`S_rel(phi) = -kappa log R(phi)`

with

`kappa = ln(2)/(24*pi)`.

The tensor below is derived from this action. No metric profile is fitted.

## Exact R derivatives

Let `u_a = exp(i phi_a)` and `z=(1/d)sum u_j`.

The exact gradient is

`partial_a R = -(2/d) Im(conj(z) u_a)`.

The exact Hessian of `R` is

for `a != b`:

`partial_a partial_b R = (2/d^2) cos(phi_a-phi_b)`,

and for `a=b`:

`partial_a^2 R = 2[1/d^2 - Re(conj(z)u_a)/d]`.

Therefore, wherever `R>0`,

`H_S = Hess(S_rel) = kappa[(grad R)(grad R)^T/R^2 - Hess(R)/R]`.

## Global U(1) mode

A common phase shift `phi_j -> phi_j + c` leaves `R` and `S_rel` invariant.
Consequently the all-ones vector is a null mode:

`H_S 1 = 0`.

This is implemented and regression-tested.

## Coherent-point metric

At `phi_1=...=phi_d`, the exact Hessian reduces to

`g_rel_local = (2*kappa/d)[I-(1/d)11^T]`.

It has rank `d-1` and is positive definite on the horizontal quotient
`sum_j delta_j=0`.

For `d=36`, the single-coordinate quadratic coefficient remains

`kappa*35/36^2 = 0.00024827179801127847`.

## Why this is not a global Riemannian metric

Away from coherent overlap, the exact action Hessian can acquire negative
horizontal eigenvalues while preserving the global U(1) zero mode.

Therefore the canon distinction is:

- exact global action Hessian on `R>0`: `DERIVED`;
- Riemannian metric interpretation: `REGIONAL`;
- indefinite region: `ACTION_TENSOR_ONLY`, not admitted into the Hamiltonian
  kinetic metric block.

The runtime now computes the Hessian signature and hard-fails if an indefinite
or additionally degenerate region is requested as a Hamiltonian relational
metric.

## Regional inverse

Where the signature is

`RIEMANNIAN_ON_HORIZONTAL_QUOTIENT`,

the Moore–Penrose inverse of the exact Hessian is used as the inverse metric on
the horizontal quotient. The global U(1) zero mode remains zero.

No finite-difference derivative or arbitrary regularization is introduced.

## Remaining geometry debt

A fully nonlinear Hamiltonian trajectory through changing relational phase
coordinates also needs derivatives of the regional inverse metric. Those are
not approximated with an arbitrary finite-difference step. Until an analytic or
otherwise provenance-bearing derivative is implemented, the exact coherent
local builder remains the canonical Hamiltonian implementation and the global
Hessian is used for regional admissibility/signature analysis.

## Epistemic firewall

`GLOBAL_HESSIAN_DERIVED != GLOBAL_RIEMANNIAN_METRIC`

`REGIONAL_METRIC_ADMITTED != UNIVERSAL_METRIC`

This derivation does not alter the earlier falsification:

`DIRECT_LOCAL_TIR_TO_1_OVER_R = FAIL`.
