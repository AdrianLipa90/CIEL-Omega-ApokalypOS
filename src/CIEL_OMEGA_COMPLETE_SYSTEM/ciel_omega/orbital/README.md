# orbital

Global read-only orbital coherence engine for the repository.

Purpose:
- derive six-sector orbital geometry from real repo structure,
- compute global coherence metrics,
- expose spectral observables,
- provide a read-only diagnostic pass before any write-back automation.

Canonical workflow:
1. derive real geometry from imports + README/AGENT mesh + manifests,
2. build global \(A_{ij}(\tau_i,\tau_j,\Omega_{ij},d_{ij})\),
3. evolve the six-sector system,
4. report:
   - \(R_H\)
   - \(T_{glob}\)
   - \(\Lambda_{glob}\)
   - `closure_penalty`
   - spectral observables
