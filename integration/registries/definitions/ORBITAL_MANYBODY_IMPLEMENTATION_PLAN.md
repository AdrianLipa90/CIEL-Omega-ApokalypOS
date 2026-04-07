# Hierarchical Orbital Many-Body Implementation Plan v0.4

## Objective
Refactor the orbital card system so each object card and each subsystem card carries enough structure to represent limited information regimes, event-horizon style subsystem boundaries, holonomic leakage policy, many-body synchronization roles, local/orbit/system tau, systemic privacy, deterministic horizon-policy semantics, and runtime export gating.

## New architectural laws
### Systemic Privacy Law
`K_i^ext = Π_H(K_i^int)`

### Horizon Policy Law
Every horizon class must carry explicit deterministic policy data for privacy, leak mode, leak budget, allowed visibility transitions, exportable fields, and sealed fields.

### Board Synchronization Law
Subsystem members synchronize through a board-level orbital frame:
- `tau_local` for the local node
- `tau_orbit` for the subsystem-board
- `tau_system` for the global attractor frame

### Runtime Projection Law
Runtime reports and user-facing packets may expose only projected/export-compatible state, never direct subsystem-private state.

## Current implementation status
- Phase 0 ✅
- Phase 1 ✅
- Phase 2 ✅
- Phase 3 ✅
- Phase 4 ✅
- Phase 5 ✅
- Phase 6 ⏳ current

## Completed phases
### Phase 4 — Local synchronization scaffolding ✅
- attach `tau_local`, `tau_orbit`, `tau_system`
- define board/subsystem aggregation via `subsystem_sync_registry.json`
- define condensation of internal subsystem state into `condensed_half_conclusion`
- persist board synchronization into `subsystem_sync.sqlite`

### Phase 5 — Runtime integration ✅
- feed subsystem sync and policy artifacts into `orbital_bridge.py`
- emit `subsystem_sync_manifest.json` and `runtime_gating.json`
- project runtime gating and sync manifest into `sapiens_client.py`
- enforce projected export mode for user-facing packets

## Current implementation target
The current target is **Phase 6**:
1. rerun hook chain and DB build,
2. verify deterministic artifact coherence,
3. verify recursion guard still holds,
4. verify private/export separation remains enforced,
5. finalize documentation and audit readiness.
