# Orbital Import Manifest V2

## Purpose

This file repairs the practical meaning of `integration/Orbital/IMPORT_MANIFEST.json` without rewriting that broken file in place.

## Current status

Orbital integration has been extended from a partial imported snapshot into a minimally executable orbital runtime layer.

## Confirmed executable files in `integration/Orbital/main/`

- `__init__.py`
- `model.py`
- `registry.py`
- `phase_control.py`
- `rh_control.py`
- `metrics.py`
- `dynamics.py`
- `extract_geometry.py`
- `global_pass.py`

## Confirmed launcher

- `scripts/run_orbital_global_pass.py`

## Manifest note

The original `IMPORT_MANIFEST.json` remains structurally broken and should be replaced or rewritten once direct in-place update is available.

## Follow-up tasks

1. fold this addendum into a repaired JSON manifest,
2. add orbital report paths to higher-level indices when root/index rewrite is available,
3. replace minimal runtime modules with exact audited snapshot copies if strict source parity is required.
