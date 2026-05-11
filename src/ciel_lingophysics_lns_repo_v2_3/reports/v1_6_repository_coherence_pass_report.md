# v1.6 Repository Coherence Pass Report

Generated UTC: 2026-05-10T13:08:13.520802+00:00

## Summary

This patch hardens the repository before Batch02 expansion. It adds explicit registries, schema coverage, file classification, relation integrity checks and fallback manifests.

## Coherence metrics before v1.6 additions

- file count scanned: 313
- YAML files: 105
- JSON files: 65
- YAML missing JSON counterpart: 54
- schemas: 15
- integrity blockers: 0
- integrity warnings: 1

## New artifacts

- `data/registry/card_type_registry_v1_6.*`
- `data/registry/canonical_status_registry_v1_6.*`
- `data/coherence/repository_coherence_summary_v1_6.*`
- `data/coherence/yaml_json_pair_audit_v1_6.*`
- `data/schema_coverage/schema_coverage_map_v1_6.*`
- `data/integrity/relation_integrity_report_v1_6.*`
- `data/json/fallback_manifest_v1_6.json`
- `schemas/ciel_lns_repo_coherence.schema.json`
- `src/lingophysics/repo_coherence.py`
- `tests/test_repo_coherence.py`

## Interpretation

No integrity blocker was detected in required v1.5/v1.6 core paths. Some YAML files intentionally do not have JSON mirrors yet; these are marked as WARN, not BLOCKER, because the repo still contains curated draft seed layers and human-readable operator families.

## Rule carried forward

```text
Unknown is legal. Hidden unknown is not.
WARN is visible uncertainty. BLOCKER is a stopped pipeline.
```
