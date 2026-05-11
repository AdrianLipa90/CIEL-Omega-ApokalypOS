# v1.0 Batch01 Local Library Patch Report

Generated: 2026-05-10T01:20:24.015825+00:00

## Added

- 36 concept cards × 5 languages = 180 language panels.
- Separate concept/operator library growth model.
- Batch01 YAML/JSON/CSV/XLSX artifacts.
- SQLite database: `data/sqlite/cielingo_batch01_v1_0.sqlite`.
- HDF5 matrix store: `data/hdf5/cielingo_batch01_v1_0.h5`.
- Graph exports: JSON and GraphML.
- Heatmaps: grammar gauge distance and concept-operator incidence.
- Tests for concept/operator separation and batch counts.

## Important limitation

This is a curated seed, not an authoritative multilingual dictionary. Synonyms, antonyms, forms, and examples are placeholders for iterative validation. No external dictionary data was imported.

## Next recommended patch

v1.1 should add the `BatchRegistry` and a conflict detector:

```text
new card -> compare to prior cards -> tag synonyms/antonyms/false-friends -> update graph -> emit conflict report
```

## Test result

Local test command:

```bash
PYTHONPATH=. pytest -q
```

Result: `20 passed`.
