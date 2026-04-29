# NL-EBA-0002 — EBA Loop Evaluation Set

## Identity
- **card_id:** `NL-EBA-0002`
- **name:** `EBA Loop Evaluation Set`
- **class:** `nonlocal_phase_memory_card_set`
- **active_status:** `ACTIVE_CANONICAL_NONLOCAL_CARD_SET`

## Anchors
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/orchestrator_types.py`
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/holonomy.py`

## Role
Canonical card set for Euler-Berry-Aharonov-Bohm loop evaluations carried by nonlocal memory runtime.

## Flow
- **input_from:** `Holonomic loop geometry + trajectory state + identity phase`
- **output_to:** `loop cards with phi_ab, phi_berry, defect magnitude, coherence state, and energy/defect summaries`

## Authority
### May
- represent loop-level nonlocal cards for short/medium/long memory loops
- feed bridge-visible nonlocal card manifests
- act as machine-readable substrate for nonlocal registry export

### Must not
- replace underlying holonomy calculations
- be synthesized from stale exports when live orchestrator results are available
- drift away from canonical loop IDs and coherence thresholds

## Horizon relation
Internal card layer that becomes projected summary through bridge horizon.

## Authority rule
Loop cards are derived from canonical orchestrator outputs and remain subordinate to the live memory runtime.
