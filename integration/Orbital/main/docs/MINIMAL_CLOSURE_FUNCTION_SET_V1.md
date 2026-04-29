# MINIMAL CLOSURE FUNCTION SET V1

## Strict closure core
1. `_build_core_phase_vector`
2. `delta_H`
3. `R_H`
4. `evaluate_unified_euler_constraint`
5. `apply_active_euler_feedback`
6. `V_information`

Chain:
phase vector -> Delta_H -> R_H -> closure evaluation -> feedback -> potential

## Runtime context
- `UnifiedSystem.run_text_cycle`
- `MemoryCorePhaseBridge.step`
