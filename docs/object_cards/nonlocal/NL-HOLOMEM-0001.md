# NL-HOLOMEM-0001 — HolonomicMemoryOrchestrator

## Identity
- **card_id:** `NL-HOLOMEM-0001`
- **name:** `HolonomicMemoryOrchestrator`
- **class:** `nonlocal_memory_orchestrator`
- **active_status:** `ACTIVE_CANONICAL_NONLOCAL_RUNTIME`

## Anchors
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/orchestrator.py`
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/orchestrator_types.py`
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/holonomy.py`

## Role
Canonical nonlocal memory orchestrator that computes Euler-Berry-Aharonov-Bohm loop evaluations and carries continuity across memory channels.

## Flow
- **input_from:** `cleaned text + phase metadata + memory channels`
- **output_to:** `OrchestratorCycleResult + eba_results + energy/defect aggregates`

## Authority
### May
- compute EBA loop evaluations from canonical memory channels
- emit nonlocal coherence, Berry phase, AB phase, and defect metrics
- serve as canonical source of nonlocal runtime state for engine/orchestrator/bridge integration

### Must not
- be replaced by demo EBA scripts as runtime source of truth
- be treated as optional decorative telemetry when nonlocal runtime is active
- silently fork parallel nonlocal memory logic outside the canonical memory sector

## Horizon relation
Internal nonlocal runtime beneath bridge projection.

## Authority rule
Canonical source of nonlocal memory runtime; downstream layers consume its outputs but do not override them.
