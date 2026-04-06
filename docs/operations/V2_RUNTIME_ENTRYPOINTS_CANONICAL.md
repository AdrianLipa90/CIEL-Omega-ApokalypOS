# V2 Runtime Entrypoints — Canonical Surface

## Purpose

This document defines the canonical operational surface for v2-aware runtime entrypoints during the controlled transition from preferred-v2 to canonical-v2.

It supersedes `docs/operations/V2_RUNTIME_ENTRYPOINTS.md` as the target operational guidance surface, while legacy operational notes remain valid as compatibility references until the final in-place switch is performed.

## Canonical rule

During canonical-v2 transition:
- v2-aware entrypoints are the default operational surface,
- legacy entrypoints remain executable but secondary,
- path resolution must remain explicit whenever a runtime can consume both v2 and legacy layouts.

## Canonical v2 entrypoints

### Index validation
- canonical launcher: `scripts/run_index_validator_v2.py`
- canonical module: `src/ciel_sot_agent/index_validator_v2.py`

Behavior:
- prefers `integration/registries/index_registry_v2.yaml`
- falls back to `integration/index_registry.yaml`
- tolerates the current shell-map transitional state where imported bindings may still reference `MAP-SOT-0001`

### Live GitHub coupling runtime
- canonical launcher: `scripts/run_gh_repo_coupling_v2.py`
- canonical module: `src/ciel_sot_agent/gh_coupling_v2.py`

Behavior:
- prefers class-separated v2 paths for registries, couplings, and upstream runtime state
- falls back to legacy flat paths when needed
- emits `path_resolution` in the report so the selected runtime geometry is explicit

### Repository synchronization runtime
- canonical launcher: `scripts/run_repo_sync_v2.py`
- canonical module: `src/ciel_sot_agent/synchronize_v2.py`

Behavior:
- prefers `integration/registries/repository_registry.json`
- prefers `integration/couplings/repository_couplings.json`
- falls back to `integration/repository_registry.json` and `integration/couplings.json`
- emits `path_resolution` so the selected synchronization geometry is explicit

## Secondary legacy entrypoints

These remain executable during transition, but they are secondary compatibility paths rather than canonical guidance:

- `scripts/run_gh_repo_coupling.py` -> `src/ciel_sot_agent/gh_coupling.py`
- `src/ciel_sot_agent/index_validator.py` -> legacy validator path
- `src/ciel_sot_agent/synchronize.py` -> legacy synchronization path

## Canonical operational dependency direction

Operationally, the repository should now be run through this direction:

`v2 machine registry -> v2-aware runtime reader -> explicit path resolution -> report/artifact surface`

and at the higher architectural layer:

`orbital source architecture -> imported orbital runtime -> native bridge reduction -> relational-formal Sapiens surface -> packet/session/report artifacts`

## Constraint

No operational note should present legacy entrypoints as primary once a validated v2-aware runtime path exists.
