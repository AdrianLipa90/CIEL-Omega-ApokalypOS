# V2 Canonical Switch Readiness

## Purpose

This file records the current readiness state for moving from v2 preferred to v2 canonical.

## Readiness summary

### Ready now
- v2 documentation surface exists (`README_REFACTOR_V2.md`, `docs/INDEX_V2.md`)
- v2 machine-readable surface exists (`integration/indices/hyperspace_index_v2.json`, `integration/registries/index_registry_v2.yaml`)
- v2 runtime readers exist for:
  - index validation,
  - GitHub coupling,
  - synchronization
- v2 launchers exist for those readers
- migration map exists
- orbital protected-sector rule exists

### Not ready yet
- `README.md` has not been switched to canonical v2 guidance
- `docs/INDEX.md` has not been switched to canonical v2 guidance
- `docs/operations/V2_RUNTIME_ENTRYPOINTS.md` does not yet include synchronization runtime
- legacy machine-readable authority still exists in parallel:
  - `integration/hyperspace_index.json`
  - `integration/index_registry.yaml`
- legacy runtime modules still exist and are not yet consistently marked secondary

## Blocking set

### Blocking documentation items
- root README surface still not canonical-v2
- legacy docs index still not canonical-v2

### Blocking machine items
- legacy machine registry still treated as active parallel authority
- legacy hyperspace index still treated as active parallel authority

### Blocking runtime items
- not all readers are confirmed v2-aware yet
- operational entrypoint note is incomplete until synchronization runtime is recorded there

## Non-blocking but important
- shell-map transition state still mixes legacy and v2 object identity conventions
- this is currently tolerated by the v2 validator and therefore is not a hard blocker for readiness capture

## Readiness verdict

Current verdict:
- **ready for controlled canonicalization planning**
- **not yet ready for destructive canonical switch**

## Recommended immediate actions

1. update operational note to include synchronization runtime,
2. mark legacy entrypoints as compatibility paths in operational docs,
3. prepare canonical surface rewrite for `README.md` and `docs/INDEX.md`,
4. prepare authoritative-machine switch notes for registry/index ownership.
