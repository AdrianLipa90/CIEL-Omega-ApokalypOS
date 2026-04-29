# Machine Canonicalization Progress

## Purpose

This note records concrete progress made in Phase 3 of the controlled transition toward v2 machine authority.

## Progress achieved

### Machine authority is now explicitly declared
- `integration/MACHINE_AUTHORITY_V2.md`

This establishes the target machine-readable authority direction:
- `integration/indices/hyperspace_index_v2.json`
- `integration/registries/index_registry_v2.yaml`

### Legacy machine files are now explicitly demoted at the documentation level
- `docs/architecture/LEGACY_MACHINE_MIRROR_POLICY.md`
- `docs/integration/MACHINE_AUTHORITY_SURFACE.md`

These documents establish that:
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

remain valid compatibility mirrors,
but are no longer the preferred machine authority surfaces.

## Resulting state

The repository now has:
- target machine authority declaration,
- legacy mirror policy,
- human-readable machine authority surface,
- v2-aware runtime readers already consuming or preferring v2 machine paths.

## What this resolves

This resolves the earlier ambiguity where legacy and v2 machine-readable layers could still appear equally primary at the documentation level.

That ambiguity is now reduced.

## What remains unfinished

The following are still not complete:
- legacy machine files have not been rewritten in place,
- final in-place root authority switch has not occurred,
- not every runtime reader is guaranteed converged yet.

## Current verdict

Machine canonicalization status is now:
- **declared**,
- **surface-supported**,
- **runtime-supported in key readers**,
- **not yet destructively finalized**.

## Recommended next move

The next move should be preparation of final in-place switch materials for the remaining legacy authority surfaces.
