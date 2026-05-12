# CIEL-LNS/Ω v1.4: Storage Fallback Protocol

This protocol implements the rule:

```text
if preferred storage fails, fallback to JSON or JSONL.
```

The goal is not elegance. The goal is survival of state.

## Motivation

CIELingo uses several storage layers:

- YAML for readable cards and configs
- JSON for stable interchange and fallback
- CSV/XLSX for human spreadsheets
- SQLite for indexed relational queries
- HDF5 for dense vectors, matrices, heatmaps, and numeric datasets
- GraphML/JSON for graph exports

Binary and dependency-heavy formats can fail because of missing libraries, file locks, platform issues, or schema mismatches. A failed HDF5 export must never destroy a batch pulse.

## Canonical fallback rule

```text
write(target_format)
if error:
    write(JSON fallback)
    write(fallback report)
    continue pipeline
```

## Required metadata

Every fallback record must include:

```yaml
preferred_format: hdf5 | sqlite | xlsx | graphml | other
fallback_format: json | jsonl
used_fallback: true
error_type: string
error_message: string
target_path: string
fallback_path: string
timestamp_utc: string
```

## Epistemic rule

Fallback is not silent. Fallback must be reported.

```text
Silent fallback = invalid state transition
Reported fallback = valid degraded mode
```

## Data integrity rule

If a binary export fails, the JSON fallback must preserve at least:

- batch id
- object ids
- relation ids
- language panels
- operator links
- matrices as nested arrays or sparse records
- schema version
- provenance of the export attempt

## Implementation module

The implementation lives in:

```text
src/lingophysics/storage_fallback.py
```

It provides:

```python
write_hdf5_or_json(data, h5_path, json_path=None)
write_json_fallback(data, json_path, metadata)
```

The result object explicitly reports whether fallback was used.
