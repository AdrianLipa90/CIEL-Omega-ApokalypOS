# V2 Runtime Entrypoints

## Purpose

This document records the preferred executable entrypoints during the repository-geometry migration.

It exists so that refactor work does not depend on implicit knowledge of which runtime modules already understand the v2 path geometry.

## Current rule

During migration:
- legacy entrypoints remain valid,
- v2-aware entrypoints are preferred whenever they exist,
- destructive replacement is deferred until convergence is stronger.

## Preferred v2 entrypoints

### Index validation
- preferred launcher: `scripts/run_index_validator_v2.py`
- preferred module: `src/ciel_sot_agent/index_validator_v2.py`

Behavior:
- prefers `integration/registries/index_registry_v2.yaml`
- falls back to `integration/index_registry.yaml`
- tolerates the current shell-map transitional state where imported bindings may still reference `MAP-SOT-0001`

### Live GitHub coupling runtime
- preferred launcher: `scripts/run_gh_repo_coupling_v2.py`
- preferred module: `src/ciel_sot_agent/gh_coupling_v2.py`

Behavior:
- prefers class-separated v2 paths for registries, couplings, and upstream runtime state
- falls back to legacy flat paths when needed
- emits `path_resolution` in the report so the selected runtime geometry is explicit

## Legacy entrypoints still valid

- `scripts/run_gh_repo_coupling.py` -> `src/ciel_sot_agent/gh_coupling.py`
- `src/ciel_sot_agent/index_validator.py` remains present as a legacy validator path

These remain valid during transition, but they are no longer the preferred runtime surface for refactor work.

## Why this matters

The repository now has:
- legacy geometry,
- target geometry,
- compatibility copies,
- v2 machine-readable indices,
- v2-aware runtime modules.

Without explicit preferred entrypoints, operators can accidentally run legacy-only modules and incorrectly conclude that the v2 migration is broken.

## Next expected move

As more readers become v2-aware, they should be added to this document until the v2 path becomes the default operational surface.
