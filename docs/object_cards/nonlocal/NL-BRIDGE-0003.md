# NL-BRIDGE-0003 — MemoryCorePhaseBridge

## Identity
- **card_id:** `NL-BRIDGE-0003`
- **name:** `MemoryCorePhaseBridge`
- **class:** `nonlocal_reduction_bridge`
- **active_status:** `ACTIVE_CANONICAL_NONLOCAL_BRIDGE`

## Anchors
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/bridge/memory_core_phase_bridge.py`

## Role
Canonical reduction bridge from nonlocal memory and phase state into Euler metrics and projected bridge state.

## Flow
- **input_from:** `memory runtime + phase state + core state`
- **output_to:** `euler_metrics + bridge_closure_score + target_phase + projected bridge bundle`

## Authority
### May
- reduce nonlocal state into bridge-visible Euler metrics
- carry closure and phase-target information into runtime and pipeline outputs
- operate in both package and local script modes as the same bridge object

### Must not
- shadow the canonical memory orchestrator with synthetic nonlocal state
- emit bridge metrics detached from canonical memory/core state
- be bypassed by ad hoc wrappers claiming to project nonlocal state directly

## Horizon relation
Bridge horizon between internal nonlocal state and projected runtime/action state.

## Authority rule
Canonical reduction path for nonlocal -> Euler bridge metrics; wrappers may read but not redefine its outputs.
