# Relational Mechanism Formalism v0

This repo tracks the mechanism layer only. The metric is left emergent.

## Core objects
- Base state manifold: local spherical / projective chart
- Cycles: C_i
- Phase of a cycle: gamma_i = ∮_Ci A
- Local fingerprint: Sigma_i = (tau_i, gamma_i, F_i)
- Holonomic pair relation: W_ij
- Pair correction / coupling result: F_ij
- Euler-Berry closure defect: Delta_H = Σ_k exp(i gamma_k)
- Holonomic defect norm: R_H = |Delta_H|^2
- Relational potential: V_rel = kappa_H R_H + V_I + V_D

## Minimal pipeline
relation -> orbital -> orchestration -> reduction -> memory

## Confirmed couplings in this repo
- tau_i couples to pair structure through (tau_i, tau_j, gamma_i, gamma_j, W_ij) -> F_ij
- epsilon couples to D
- gamma_i couples to A
- W_ij is induced by a connection along a path between cycles
- Delta_H is constructed from the phase family {gamma_k}
- R_H is induced by Delta_H
- V_rel is induced by R_H

## Not frozen here
- final D_f
- final J(epsilon)
- final metric
- final Kepler layer
- final tetrahedral horizon dynamics

## Tetrahedral toy extension
A regular tetrahedral frame T_4 may be embedded into the spherical base as a minimal nontrivial spatial scaffold.
This is tracked here as a toy extension and not yet a frozen runtime law.
