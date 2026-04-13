# Scripts

## Role

This folder stores thin operational launchers for the SOT integration layer.

Scripts in this folder should remain small and explicit.
They should delegate real logic to `src/ciel_sot_agent/`.

## Current scripts

### Stable launchers

- `run_gh_repo_coupling.py` — launches the live GitHub coupling routine implemented in `src/ciel_sot_agent/gh_coupling.py`.
- `run_gh_repo_coupling_v2.py` — launches the v2 GitHub coupling routine in `src/ciel_sot_agent/gh_coupling_v2.py`.
- `run_index_validator_v2.py` — launches the v2 index validator implemented in `src/ciel_sot_agent/index_validator_v2.py`.
- `run_orbital_bridge.py` — emits bridge-state artifacts from `src/ciel_sot_agent/orbital_bridge.py`.
- `run_orbital_global_pass.py` — runs the orbital diagnostic pass from `integration/Orbital/main/global_pass.py`.
- `run_repo_phase_sync.py` — launches the repository phase synchronizer implemented in `src/ciel_sot_agent/synchronize.py`.
- `run_repo_sync_v2.py` — launches the v2 repository synchronizer implemented in `src/ciel_sot_agent/synchronize_v2.py`.
- `run_integration_mirror_sync.py` — synchronizes legacy and v2 integration mirror files via `src/ciel_sot_agent/integration_mirror.py`.
- `run_sapiens_panel.py` — launches the Sapiens panel foundation shell from `src/ciel_sot_agent/sapiens_panel/controller.py`.

### Bootstrap and import helpers

- `bootstrap_audio_orbital_and_catalog.py`
- `bootstrap_audio_orbital_stack.py`
- `build_nonlocal_definition_edges.py`
- `build_orbital_definition_registry.py`
- `export_orbital_registry_to_noema.py`
- `resolve_orbital_semantics.py`
- `run_audio_orbital_probe.py`
- `snapshot_audio_orbital_stack.sh`

### Note

There is no dedicated `run_sapiens_client.py` wrapper in this folder.
The packet-oriented Sapiens client is exposed as the packaged console script `ciel-sot-sapiens-client`, while the repo-local thin wrapper is `run_sapiens_panel.py`.

## Design rule

If a script grows beyond a thin wrapper, the implementation should move into `src/` and the script should stay only as a stable entrypoint.
