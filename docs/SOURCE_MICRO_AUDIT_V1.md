# Source Micro Audit V1

This audit covers the executable core of `CIEL-_SOT_Agent` after local consolidation.

## Scope
- `src/ciel_sot_agent/repo_phase.py`
- `src/ciel_sot_agent/gh_coupling.py`
- `src/ciel_sot_agent/index_validator.py`
- `src/ciel_sot_agent/synchronize.py`
- `scripts/run_repo_phase_sync.py`
- `scripts/run_gh_repo_coupling.py`

## Derived counts
- analyzed files: 6
- analyzed functions: 23
- critical functions: 8

## Operation totals
- assign: 136
- call: 378
- if: 61
- loop: 21
- return: 29
- binop: 55
- compare: 38
- try: 4
- comprehension: 9

## Highest-density files
- `src/ciel_sot_agent/index_validator.py`: calls=225, binops=13, assigns=57, functions=7
- `src/ciel_sot_agent/gh_coupling.py`: calls=101, binops=27, assigns=57, functions=8
- `src/ciel_sot_agent/repo_phase.py`: calls=47, binops=11, assigns=18, functions=7
- `src/ciel_sot_agent/synchronize.py`: calls=5, binops=4, assigns=4, functions=1
- `scripts/run_gh_repo_coupling.py`: calls=0, binops=0, assigns=0, functions=0

## Critical functions
- `src/ciel_sot_agent/repo_phase.py::closure_defect`
- `src/ciel_sot_agent/repo_phase.py::all_pairwise_tensions`
- `src/ciel_sot_agent/repo_phase.py::build_sync_report`
- `src/ciel_sot_agent/gh_coupling.py::propagate_phase_changes`
- `src/ciel_sot_agent/gh_coupling.py::build_live_coupling`
- `src/ciel_sot_agent/index_validator.py::validate_demo_shell_inventory_data`
- `src/ciel_sot_agent/index_validator.py::validate_demo_shell_map_data`
- `src/ciel_sot_agent/index_validator.py::validate_index_registry`

## Reading of the result
The current executable core is dominated by:
- validation,
- live GitHub coupling,
- registry synchronization.

So the present local SoT agent is still a registry/coupling engine first, and only secondarily a broader relational runtime.
