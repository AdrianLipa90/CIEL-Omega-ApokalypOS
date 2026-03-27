# Scripts

## Role

This folder stores thin operational launchers for the SOT integration layer.

Scripts in this folder should remain small and explicit.
They should delegate real logic to `src/ciel_sot_agent/`.

## Current scripts

- `run_gh_repo_coupling.py` — launches the live GitHub coupling routine implemented in `src/ciel_sot_agent/gh_coupling.py`.

## Design rule

If a script grows beyond a thin wrapper, the implementation should move into `src/` and the script should stay only as a stable entrypoint.
