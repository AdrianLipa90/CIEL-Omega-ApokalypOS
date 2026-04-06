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


## Recursion guard
The definition registry must not ingest its own generated card artifacts. The normalization step removes paths under `integration/registries/definitions/` and stabilizes definition IDs with line numbers so the card graph remains non-self-referential across reruns.

## Database library
4. `python scripts/build_definition_db_library.py`
   - compiles the enriched registry into a **database library** under `db_library/`
   - writes `records.sqlite`, `reports.sqlite`, relation-sharded edge databases and `manifest.json`

### Why a database library
The full registry becomes too large and too self-referential as a monolithic JSON export. The database library keeps the catalog queryable, indexed and split by concern (`records`, `reports`, sharded `edges_*`) instead of forcing one gargantuan tracked text artifact.
