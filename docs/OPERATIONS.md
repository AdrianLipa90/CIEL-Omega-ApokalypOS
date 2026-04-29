# Operations

## Purpose

This document makes the repository's operational layer explicit.
It focuses on the documented control surface that refreshes live integration state and keeps local folder documentation synchronized with executable behavior.

## Immediate orientation (updated 2026-04-17)

Start here when resuming work:
- **`CIEL_CANON.py`** — canonical entrypoint, run `python3 CIEL_CANON.py` for live system status.
- `AGENT.md` — standing agent rules and current implementation track.
- `agentcrossinfo.md` — multi-agent coordination, lock table, handoff log.
- `docs/INDEX.md` — global documentation navigation.

Legacy orientation files (still valid for historical context):
- `docs/operations/CIEL_REPO_WORKSTYLE_SESSION_HANDOFF.md`
- `docs/operations/ORBITAL_DYNAMICS_LAW_V0_TODO.md`

## Coupling chain

The current documented operational chain is:
1. `.github/workflows/gh_repo_coupling.yml`
2. `scripts/run_gh_repo_coupling.py`
3. `src/ciel_sot_agent/gh_coupling.py`
4. `integration/`

This chain defines how scheduled or manual repository-coupling execution propagates into refreshed machine-readable state.

## Status note

Status note: the documented operational scope is intentionally narrower than the full repository contents.
This file only describes the stable control surface that must remain explicit and auditable.

## Documentation rule

Whenever the operational chain changes, update the documentation in the local folder docs that expose that surface.
At minimum, keep this file, `.github/workflows/README.md`, the active operation ledger, and any affected local folder documentation synchronized.

## Execution surfaces

### `scripts/`
The stable repo-local wrapper documented here is:
- `scripts/run_gh_repo_coupling.py`

### `.github/`
GitHub provides the automation control surface for scheduled and manual execution.

### `.github/workflows/`
The currently documented workflow is:
- `gh_repo_coupling.yml` — scheduled/manual repository coupling refresh and commit-on-change automation.

## Why this layer matters

The goal is to keep the coupling chain inspectable from workflow trigger to written integration output.
That means the workflow, the launcher, the Python module, the resulting `integration/` artifacts, and the active operation memory must remain readable as one auditable path.
