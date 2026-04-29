# Derivation Notes

These notes bridge the user's relational-phase analogies to the first executable integration metric used in this repository.

## D1. Discrete repository state
Assume each repository `R_i` carries a discrete state:
- phase `phi_i`
- mass `m_i >= 0`
- spin marker `s_i in {+1/2, -1/2}`
- identity label `I_i`

This is a finite approximation for integration work. It is not yet a full derivation from the canonical field structure.

## D2. Pairwise coupling
For a weighted semantic relation between repositories `i` and `j`, assign coupling `K_ij >= 0`.
A minimal bounded pairwise tension functional is:

`tension(i,j) = K_ij * (1 - cos(phi_j - phi_i))`

Properties:
- zero when phases are equal modulo `2*pi`
- nonnegative
- bounded above by `2*K_ij`

## D3. Global Euler-style closure
Treat each repository as a weighted unit phasor `m_i * exp(i*phi_i)`.
Define the weighted Euler vector:

`E = sum_i m_i * exp(i * phi_i)`

and normalized closure defect:

`D = 1 - |E| / sum_i m_i`

For nonnegative masses:
- `0 <= D <= 1`
- `D = 0` if all repositories are perfectly phase-aligned

## D4. Why this is the first implementation target
This metric has three useful features for integration work:
1. it is finite and easy to compute,
2. it is machine-readable and testable,
3. it gives a shared scalar for comparing repository coordination over time.

## D5. Relation to broader claims
The user proposed that synchronization through a shared substrate may reflect a deeper geometry of information flow.
This repository does **not** claim that the present derivation proves that universal thesis.
It implements only the first narrow bridge:

> if repositories are modeled as coupled discrete phase carriers, a weighted Euler closure defect can serve as a practical coherence observable.

## Imported upstream constraint
Uploaded materials include a relational contract parameter file and a derivation note where `tau_i` is explicitly coupled to `A_ij` in the relational setting.
This repository records that as a protected upstream concept and does not override it here.
Crossref:
- `agentcrossinfo.md`
- `docs/science/HYPOTHESES.md`
