# Integration Data Split Status

## Purpose

This file records the target class split for the `integration/` sector during repository refactor.

## Established target sectors

The following target sectors now exist additively:
- `integration/registries/`
- `integration/couplings/`
- `integration/indices/`
- `integration/upstreams/`

These sectors should become the target homes for machine-readable integration state classes.

## Protected exception

The orbital layer remains a protected import/runtime sector and is not part of the generic split:
- `integration/Orbital/`
- `integration/Orbital/main/`

This exception is structural, not temporary.

## Legacy-path status

Legacy files may still remain directly under `integration/` during migration.
That is intentional in phase 1 and phase 2.

## Planned migration classes

### registries
Examples:
- repository registries
- index registries
- stable identity inventories

### couplings
Examples:
- pairwise repository couplings
- weighted relation graphs
- explicit coupling tables

### indices
Examples:
- hyperspace index
- cross-reference maps
- machine-readable navigation structures

### upstreams
Examples:
- shell maps
- upstream inventory snapshots
- live upstream state descriptors

### reports
Existing report surfaces remain valid.
No destructive report migration is performed yet.

## Immediate consequence

Future cleanup should prefer moving machine-readable files by class into these sectors rather than keeping `integration/` flat.
At the same time, no change should violate the protected orbital-sector rules.
