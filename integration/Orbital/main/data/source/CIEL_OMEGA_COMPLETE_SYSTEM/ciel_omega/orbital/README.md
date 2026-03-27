# orbital

Status: **active orbital coherence layer with runtime bridge**.

This subsystem is not just a passive chart renderer. In the current audited build it does four concrete jobs:

1. **derive real repository geometry** from imports, README mesh, AGENT mesh, and structural manifests,
2. **construct the orbital system** with sector states, Berry phases, Poincare distances, closure residuals, and zeta support,
3. **evolve the system** under the relational Lagrangian / Euler-leak dynamics,
4. **bridge the final state into runtime policy and memory metadata** through `ciel/orbital_memory_loop.py`.

So the right description is:

> orbital is the coherence-and-control layer that reads real structure, computes global state, and feeds runtime restraint / depth policy.

It is still true that this layer is **read-only with respect to repository content** during the global pass itself. It writes reports/manifests, but it does not mutate source files or perform autonomous repo edits.

## What the subsystem already computes

- sector geometry `(theta, phi, rho)`
- pair couplings `A_ij(tau_i, tau_j, Omega_ij, d_ij)`
- global coherence `R_H`
- chord tension `T_glob`
- global chirality `Lambda_glob`
- closure penalty / residuals
- zeta tetra defect and effective zeta coupling
- spectral observables of the orbital adjacency / Laplacian
- runtime control recommendation (`safe` / `standard` / `deep`)
- RH policy overlay (`normal_operation` / `slow_execution_local_correction` / `freeze_and_rebuild_closure`)

## Current role in the full system

`input -> orbital pass -> control recommendation -> runtime policy -> memory metadata / wave attrs`

That means the orbital subsystem is already participating in the live execution loop, even though it is not yet the sole global governor of every subsystem.

## Canonical workflow

1. derive real geometry from imports + README/AGENT mesh + manifests,
2. build global `A_ij(tau_i, tau_j, Omega_ij, d_ij)`,
3. evolve the six-sector system under the relational Lagrangian,
4. expose:
   - `R_H`
   - `T_glob`
   - `Lambda_glob`
   - `closure_penalty`
   - spectral observables
   - zeta observables
5. translate final state into runtime restraint / depth guidance.

## Open boundary

What is **not** yet closed here:

- orbital does not directly rewrite source sectors,
- orbital does not yet own the whole orchestrator,
- orbital policy is bridged into runtime and memory, but not yet propagated through every subsystem as a universal control law.

So the honest status is neither “mere diagnostic toy” nor “finished total governor”. It is an active coherence layer with a real runtime bridge and an unfinished global closure boundary.
