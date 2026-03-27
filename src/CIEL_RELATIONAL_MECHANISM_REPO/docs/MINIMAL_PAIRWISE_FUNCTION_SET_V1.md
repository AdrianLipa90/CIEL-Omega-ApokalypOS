# MINIMAL PAIRWISE FUNCTION SET V1

This document isolates the smallest confirmed-mechanism function set needed to realize pairwise coupling mechanically in the current runtime.

## Strict pairwise core
1. `berry_pair_phase`
2. `_complex_coupling`
3. `A_ij`
4. `A_matrix`

Chain:
pair phase -> complex pair kernel -> A_ij -> global A_matrix

## Runtime context
- `run_global_pass`
- `step`

## Notes
The runtime does not expose literal `W_ij` or `F_ij` function names in the orbital layer.
In the current canonical runtime, the nearest confirmed-mechanism carriers are the pairwise phase and A_ij/A_matrix functions in `ciel_omega/orbital/metrics.py`.
