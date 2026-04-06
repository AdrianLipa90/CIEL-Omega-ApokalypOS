# Machine Canonicalization Readiness

## Purpose

This file records whether the repository is ready to treat v2 machine-readable surfaces as canonical authority targets.

## Current assessment

### Strong signals in favor
- `integration/indices/hyperspace_index_v2.json` exists
- `integration/registries/index_registry_v2.yaml` exists
- canonical human-readable surfaces already point to v2 machine-readable layers:
  - `README_CANONICAL_V2.md`
  - `docs/INDEX_CANONICAL_V2.md`
- v2-aware runtime readers already exist for:
  - index validation
  - GitHub coupling
  - synchronization
- v2-aware runtimes already expose explicit path resolution

### Still incomplete
- legacy machine-readable files have not yet been marked in place as compatibility mirrors
- not all possible readers are confirmed v2-aware
- legacy machine authority is still socially and historically present in the repository surface

## Assessment by target

### `integration/indices/hyperspace_index_v2.json`
Assessment:
- ready to be treated as the **target canonical index authority surface**
- not yet ready to erase or silently supersede legacy flat index files in place

### `integration/registries/index_registry_v2.yaml`
Assessment:
- ready to be treated as the **target canonical registry authority surface**
- not yet ready for destructive replacement of the legacy flat registry file

## Readiness verdict

Verdict:
- **ready for authoritative-target designation**
- **not yet ready for destructive legacy replacement**

## Recommended next move

The next controlled move should be:
1. create an explicit machine-authority declaration surface,
2. mark legacy machine files as compatibility mirrors at the documentation level,
3. only later perform in-place edits or root authority rewrites.
