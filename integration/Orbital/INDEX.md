# Orbital Index

Local navigation and protection rules for the orbital sector inside `CIEL-_SOT_Agent`.

## Sector identity

`integration/Orbital/` is a protected import sector.
It hosts an integration-facing projection of the orbital architecture, not an arbitrary Python package and not the native SOT bridge layer.

## Layer map

### 1. Full source architecture
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/README.md` — canonical source statement for the orbital coherence engine
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/model.py` — orbital system state objects
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/registry.py` — manifest-driven load layer
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/global_pass.py` — repository-scale diagnostic pass

### 2. Imported orbital integration layer
- `integration/Orbital/README.md` — import overview
- `integration/Orbital/AGENT1.md` — local integration rules
- `integration/Orbital/ARCHITECTURE_BINDING.md` — binding to the source architecture
- `integration/Orbital/IMPORT_MANIFEST_V2.md` — repaired human-readable import note
- `integration/Orbital/IMPORT_MANIFEST_REPAIRED.json` — repaired machine-readable import manifest

### 3. Executable imported runtime
- `integration/Orbital/main/README.md` — mechanism/runtime interpretation
- `integration/Orbital/main/AGENT1.md` — local executable rules
- `integration/Orbital/main/model.py`
- `integration/Orbital/main/registry.py`
- `integration/Orbital/main/phase_control.py`
- `integration/Orbital/main/rh_control.py`
- `integration/Orbital/main/global_pass.py`
- `integration/Orbital/main/metrics.py`
- `integration/Orbital/main/dynamics.py`
- `integration/Orbital/main/extract_geometry.py`

### 4. Native downstream bridge
- `src/ciel_sot_agent/orbital_bridge.py` — native reduction layer consuming orbital outputs

## Protected rules

1. Keep imported orbital files visibly imported or integration-facing.
2. Keep `integration/Orbital/main/` coherent as a small executable package.
3. Prefer explicit diagnostic artifacts over hidden write-back.
4. Do not let orbital runners silently rewrite non-orbital registry layers.
5. If the imported layer changes, update manifest notes and launcher references together.
6. Do not flatten this sector into generic package cleanup during repository refactor.

## Current refactor status

The orbital sector now has:
- a canonical architectural note in `docs/architecture/ORBITAL_ARCHITECTURE_CANON.md`
- an integration-binding note in `integration/Orbital/ARCHITECTURE_BINDING.md`
- this local navigation index

This index should be treated as the preferred local entrypoint for orbital navigation during the refactor period.
