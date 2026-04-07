# Hierarchical Orbital Many-Body Implementation Plan v0.3

## Objective
Refactor the orbital card system so each object card and each subsystem card carries enough structure to represent limited information regimes, event-horizon style subsystem boundaries, holonomic leakage policy, many-body synchronization roles, local/orbit/system tau, systemic privacy, and deterministic horizon-policy semantics for visibility, privacy, and leak budgets.

## New architectural laws
### Systemic Privacy Law
`K_i^ext = Π_H(K_i^int)`

### Horizon Policy Law
Every horizon class must carry explicit deterministic policy data for privacy, leak mode, leak budget, allowed visibility transitions, exportable fields, and sealed fields.

## Current implementation status
- Phase 0 ✅
- Phase 1 ✅
- Phase 2 ✅
- Phase 3 ✅
- Phase 4 ⏳ next
- Phase 5 ⏳
- Phase 6 ⏳

## Current implementation target
This branch has completed **Phase 1**, **Phase 2**, and **Phase 3**.
The next target is **Phase 4**: local synchronization scaffolding (`tau_local`, `tau_orbit`, `tau_system`) and subsystem-board aggregation.
