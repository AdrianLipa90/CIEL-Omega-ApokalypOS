# Operations

## Purpose

This document makes the repository's operational layer explicit.

The architecture already documents conceptual, scientific, and machine-readable layers.
This file adds the missing operational bridge for:

- `scripts/`
- `.github/`
- `.github/workflows/`

so that the repository does not describe only theory and registry while leaving automation implicit.

## Operational layers

### `scripts/`
Thin launcher layer.

Current documented object:
- `scripts/run_gh_repo_coupling.py` — stable entrypoint for the live GitHub coupling routine.

Role:
- provide a small execution surface,
- keep automation entrypoints legible,
- delegate real logic into `src/ciel_sot_agent/`.

### `.github/`
GitHub-native repository control surface.

Role:
- host workflow definitions,
- expose repository automation rules,
- keep automation attached to auditable repository state changes.

### `.github/workflows/`
Executable workflow layer.

Current documented object:
- `.github/workflows/gh_repo_coupling.yml` — scheduled/manual workflow that runs the live GH coupling routine and commits refreshed state artifacts.

## Coupling chain

The current automation path is:

1. `.github/workflows/gh_repo_coupling.yml`
2. `scripts/run_gh_repo_coupling.py`
3. `src/ciel_sot_agent/gh_coupling.py`
4. updated files in `integration/`

This chain should remain explicit and stable.

## Documentation rule

Whenever a new automation path is introduced, its layers should be visible in all of the following places when relevant:

- local folder documentation,
- a human-readable doc in `docs/`,
- machine-readable registry or report if it writes tracked state.

## Status note

This file closes part of the earlier documentation gap by making the operational layer visible.
It does not by itself replace future updates to higher-level indices when those files are revised.
