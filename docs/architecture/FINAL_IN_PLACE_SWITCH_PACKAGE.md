# Final In-Place Switch Package

## Purpose

This package prepares the final manual or tooling-assisted in-place switch for the remaining legacy authority surfaces.

It does not perform the destructive switch itself.
It provides the exact target replacement set and switch order.

## Covered in-place targets

The final in-place switch package covers these remaining legacy-first surfaces:
- `README.md`
- `docs/INDEX.md`
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

## Target replacement sources

### Root surface
- replace `README.md` with the content model defined by `README_CANONICAL_V2.md`

### Documentation index surface
- replace `docs/INDEX.md` with the content model defined by `docs/INDEX_CANONICAL_V2.md`

### Machine-readable index surface
- replace `integration/hyperspace_index.json` with the content model defined by `integration/indices/hyperspace_index_v2.json`

### Machine-readable registry surface
- replace `integration/index_registry.yaml` with the content model defined by `integration/registries/index_registry_v2.yaml`

## Required switch order

1. confirm current branch is refreshed to main,
2. preserve backups or retain file history,
3. switch `README.md`,
4. switch `docs/INDEX.md`,
5. switch `integration/hyperspace_index.json`,
6. switch `integration/index_registry.yaml`,
7. run v2 validators and runtime entrypoints,
8. only then mark legacy alternates as compatibility or archive surfaces.

## Post-switch validation set

After the in-place switch, run at minimum:
- `scripts/run_index_validator_v2.py`
- `scripts/run_gh_repo_coupling_v2.py`
- `scripts/run_repo_sync_v2.py`

And review:
- `integration/reports/live_gh_coupling_report.json`
- any path resolution fields emitted by v2-aware runtimes

## Constraint

This package assumes:
- orbital protected-sector rules remain unchanged,
- v2 runtime readers remain preferred,
- legacy compatibility mirrors may still remain elsewhere during a grace period,
- no deletion occurs before validation passes.

## Companion files in this package

- `docs/architecture/IN_PLACE_SWITCH_CHECKLIST.md`
- `docs/architecture/README_MD_REPLACEMENT.md`
- `docs/architecture/DOCS_INDEX_MD_REPLACEMENT.md`
- `docs/architecture/HYPERSPACE_INDEX_JSON_REPLACEMENT.md`
- `docs/architecture/INDEX_REGISTRY_YAML_REPLACEMENT.md`
