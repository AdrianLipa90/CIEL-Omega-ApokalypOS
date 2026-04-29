# NL-PHASE-0004 — PhaseInfoSystem

## Identity
- **card_id:** `NL-PHASE-0004`
- **name:** `PhaseInfoSystem`
- **class:** `phase_dynamics_runtime`
- **active_status:** `ACTIVE_CANONICAL_PHASE_RUNTIME`

## Anchors
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/phase_equation_of_motion.py`

## Role
Canonical phase dynamics runtime carrying Collatz-forced phase evolution and fermion lock diagnostics.

## Flow
- **input_from:** `collatz seed + truth target + phase parameters`
- **output_to:** `R_H + fermion_lock + phase sector + collatz-forced phase evolution`

## Authority
### May
- drive canonical phase evolution in runtime processing
- expose phase diagnostics to engine/orchestrator/pipeline
- couple Collatz forcing to phase organization

### Must not
- be replaced by demo phase sweeps as runtime source of truth
- run detached from canonical collatz seed selection when collatz runtime is active
- silently fork incompatible phase semantics across surfaces

## Horizon relation
Internal phase runtime beneath bridge projection and orbital diagnostics.

## Authority rule
Canonical phase dynamics source for active runtime; downstream metrics derive from it.
