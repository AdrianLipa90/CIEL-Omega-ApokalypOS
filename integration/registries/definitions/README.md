# Orbital / Nonlocal Definition Registry

This sector is the output target for the automatic definition-catalog patch.

## Goal
Extract formal definitions from active code, assign them to orbital roles, and emit a nonlocal edge map that can be hyperlinked into the wider hyperspace / nonlocal registry.

## Pipeline
1. `python scripts/build_orbital_definition_registry.py`
   - scans configured roots
   - extracts file nodes and formal definitions
   - emits `definition_registry.json` and `definition_registry.csv`
2. `python scripts/resolve_orbital_semantics.py`
   - assigns orbital roles and semantic roles heuristically
   - emits `orbital_definition_registry.json` and `orbital_assignment_report.json`
3. `python scripts/build_nonlocal_definition_edges.py`
   - builds nonlocal / hyperref edges
   - emits `nonlocal_definition_edges.json`

## Output files
- `definition_registry.json`
- `definition_registry.csv`
- `orbital_definition_registry.json`
- `orbital_assignment_report.json`
- `nonlocal_definition_edges.json`

## Design principle
The patch does **not** pretend to understand all domain semantics. It first captures structure faithfully, then assigns orbital meaning with explicit confidence, then emits a graph that can be hand-corrected where needed.


## Latest run snapshot
- run mode: `bootstrap_audio_orbital_and_catalog.py --skip-download`
- definition records: **10995**
- nonlocal edges: **74388**
- unresolved orbital assignments: **462**
- orbit counts:
  - `IDENTITY`: 9862
  - `CONSTITUTIVE`: 156
  - `DYNAMIC`: 351
  - `INTERACTION`: 61
  - `OBSERVATION`: 51
  - `BOUNDARY`: 52
  - `UNRESOLVED`: 462

## Tracking policy
The generator emits very large machine artifacts (`definition_registry.json`, `definition_registry.csv`, `orbital_definition_registry.json`, `nonlocal_definition_edges.json`).
This branch updates the generator scripts and commits the lightweight state / report files needed to record the run without forcing multi-megabyte catalog artifacts into Git.
