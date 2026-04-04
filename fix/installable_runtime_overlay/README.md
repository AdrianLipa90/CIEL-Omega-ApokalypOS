# Installable runtime overlay

This overlay contains the tested file set that makes the repository installable and allows the bridge-facing entrypoints to run in an installed environment.

## Scope

Copy these files over the repository root:

- `pyproject.toml`
- `src/ciel_sot_agent/paths.py`
- `src/ciel_sot_agent/synchronize.py`
- `src/ciel_sot_agent/synchronize_v2.py`
- `src/ciel_sot_agent/orbital_bridge.py`
- `src/ciel_sot_agent/sapiens_client.py`
- `src/ciel_sot_agent/gh_coupling.py`
- `src/ciel_sot_agent/gh_coupling_v2.py`
- `src/ciel_sot_agent/runtime_evidence_ingest.py`
- `src/ciel_sot_agent/index_validator.py`
- `src/ciel_sot_agent/index_validator_v2.py`

## Why this overlay exists

The GitHub connector in this environment is reliable for creating new files and branches, but not for directly updating existing files in-place. This branch therefore stores the exact tested replacement files under `fix/installable_runtime_overlay/`.

## Expected verification

Run from the repository root:

```bash
pip install -e .
python -m pip wheel .
CIEL_SOT_ROOT=$PWD ciel-sot-sync
CIEL_SOT_ROOT=$PWD ciel-sot-orbital-bridge
CIEL_SOT_ROOT=$PWD ciel-sot-sapiens-client "test"
```

## Core intent

- package `integration/Orbital` with the installed distribution
- resolve runtime root through `resolve_project_root(__file__)`
- allow bridge and sapiens entrypoints to work after installation
