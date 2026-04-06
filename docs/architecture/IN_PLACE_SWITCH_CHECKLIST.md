# In-Place Switch Checklist

## Before switch

- [ ] branch refreshed to current `main`
- [ ] target canonical replacement sources reviewed
- [ ] orbital protected-sector constraint reconfirmed
- [ ] v2 runtime entrypoints available
- [ ] no destructive deletion planned in same step

## Replacement actions

- [ ] replace `README.md` from `README_CANONICAL_V2.md`
- [ ] replace `docs/INDEX.md` from `docs/INDEX_CANONICAL_V2.md`
- [ ] replace `integration/hyperspace_index.json` from `integration/indices/hyperspace_index_v2.json`
- [ ] replace `integration/index_registry.yaml` from `integration/registries/index_registry_v2.yaml`

## After switch

- [ ] run `scripts/run_index_validator_v2.py`
- [ ] run `scripts/run_gh_repo_coupling_v2.py`
- [ ] run `scripts/run_repo_sync_v2.py`
- [ ] inspect explicit `path_resolution` fields in v2-aware outputs
- [ ] confirm no orbital path flattening occurred
- [ ] confirm legacy compatibility surfaces are not presented as primary guidance

## Success condition

The switch is successful when:
- root and docs surface now point first to canonical v2 guidance,
- machine-readable authority now points first to v2 registry/index surfaces,
- runtime validation passes without needing emergency rollback,
- legacy layers remain at most compatibility mirrors.
