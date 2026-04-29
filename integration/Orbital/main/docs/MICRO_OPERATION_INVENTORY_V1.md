# MICRO OPERATION INVENTORY V1

First-pass AST decomposition of the three core files for the chain `A_ij -> Delta_H -> R_H`.

## Scope
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/metrics.py`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/constraints/euler_constraint.py`
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/phase_equation_of_motion.py`

## Critical mechanism functions included
- `metrics.py`: A_ij, A_matrix, _complex_coupling, berry_pair_phase
- `euler_constraint.py`: _build_core_phase_vector, apply_active_euler_feedback, evaluate_unified_euler_constraint
- `phase_equation_of_motion.py`: R_H, V_information, delta_H

## Summary
- **micro_target_file_count** = `3` — first-pass AST decomposition scope
- **micro_target_function_count** = `84` — all functions in first-pass target files
- **micro_critical_function_count** = `10` — critical mechanism functions across first-pass target files
- **critical_assign_count** = `71` — sum across critical mechanism functions in first-pass target files
- **critical_call_count** = `116` — sum across critical mechanism functions in first-pass target files
- **critical_if_count** = `5` — sum across critical mechanism functions in first-pass target files
- **critical_loop_count** = `3` — sum across critical mechanism functions in first-pass target files
- **critical_return_count** = `12` — sum across critical mechanism functions in first-pass target files
- **critical_binop_count** = `72` — sum across critical mechanism functions in first-pass target files
- **critical_compare_count** = `6` — sum across critical mechanism functions in first-pass target files
- **critical_comprehension_count** = `3` — sum across critical mechanism functions in first-pass target files
- **critical_try_count** = `0` — sum across critical mechanism functions in first-pass target files