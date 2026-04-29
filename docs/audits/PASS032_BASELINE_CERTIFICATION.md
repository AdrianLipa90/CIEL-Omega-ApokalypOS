# PASS032 Baseline Certification

## Scope
This pass stabilizes the deduplicated canon baseline from pass031 and focuses on:
- Debian packaging reliability
- package/test audit coherence
- Sapiens panel component API compatibility
- GUI importability without forcing optional Flask at import time
- removal of transient build/cache artifacts from the source tree

## Concrete fixes applied
- `packaging/deb/build_deb.sh`
  - cleans local build artifacts before wheel build
  - deletes `__pycache__`, `*.pyc`, `build/`, and `ciel_sot_agent.egg-info` before packaging
  - downloads pinned dependency wheels from `constraints.txt` instead of resolving `REPO_ROOT[gui]` directly
- `packaging/deb/constraints.txt`
  - refreshed pins for current binary-wheel availability (`PyYAML 6.0.3`, `MarkupSafe 3.0.3`)
  - pinned `scipy` and `h5py`
- `packaging/deb/var/lib/ciel/models/`
  - added to package skeleton
- `packaging/deb/opt/ciel-sot-agent/wheels/`
  - added to package skeleton
- `src/ciel_sot_agent/gui/app.py`
  - deferred Flask hard failure until runtime (`create_app`), keeping module importable for audit tests
- `tests/test_pipeline_audit.py`
  - updated expected canonical top-level package modules to include:
    - `local_ciel_surface.py`
    - `satellite_authority.py`
- `scripts/run_ciel_inference_surface.py`
  - now explicitly integrates with `src.ciel_sot_agent.paths`
- `src/ciel_sot_agent/sapiens_panel/support.py`
  - backward-compatible signature restored for `build_support_view`
- `src/ciel_sot_agent/sapiens_panel/communication.py`
  - backward-compatible signature restored for `build_communication_view`
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/monolith/unified_memory.py`
  - replaced deprecated `datetime.utcnow()` calls with timezone-aware UTC timestamps

## Targeted verification completed in this pass
The following targeted certification set passed in this session:
- `tests/test_braid_nonlocal_coupling.py`
- `tests/test_ciel_pipeline.py`
- `tests/test_packaging.py`
- `tests/test_pipeline_audit.py`
- `tests/test_sapiens_panel_components.py`
- `tests/test_synchronize_v2.py`
- `tests/test_main.py`
- `tests/test_orbital_runtime.py`
- `tests/test_orbital_semantics.py`
- `tests/test_runtime_sync_integration.py`

Additional per-module runs also passed earlier in the same certification flow for:
- GGUF manager/comparison
- durability
- GitHub coupling v1/v2
- index validators v1/v2
- repo phase
- repository machine map
- runtime evidence ingest
- Sapiens client/session/panel/surface policy

## Certification note
A single monolithic `pytest tests` run remains a poor certification target in this environment because it exceeds the short execution window when run as one batch. The repo is therefore certified here by a broad module-by-module pass rather than one giant aggregate invocation.

## Status
This repo snapshot is a materially cleaner baseline than pass031 and is suitable as the base for the next implementation moves.
