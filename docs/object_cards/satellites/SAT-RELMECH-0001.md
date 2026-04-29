# SAT-RELMECH-0001 — Relational Mechanism Import Bundle

## Identity
- **subsystem_id:** `SAT-RELMECH-0001`
- **name:** `Relational Mechanism Import Bundle`
- **class:** `satellite_reference_import`
- **active_status:** `ACTIVE_REFERENCE_IMPORT`

## Anchors
- `integration/imports/relational_mechanism/README.md`
- `integration/imports/relational_mechanism/MANIFEST.json`
- `integration/imports/relational_mechanism/IMPORT_NOTES.md`
- `integration/imports/relational_mechanism/registries/minimal_pairwise_function_set.csv`
- `integration/imports/relational_mechanism/registries/minimal_closure_function_set.csv`
- `integration/imports/relational_mechanism/registries/minimal_holonomy_function_set.csv`
- `integration/imports/relational_mechanism/registries/minimal_reduction_memory_function_set.csv`

## Role
Text-first preserved mechanism spine import for reviewable closure/holonomy/reduction-memory logic.

## Flow
- **input_from:** `consolidated mechanism analysis`
- **output_to:** `reviewable registries and mechanism notes`

## Authority
### May
- preserve and expose mechanism spine for review
- support refactor and interpretation of pairwise/closure/holonomy/reduction-memory logic
- serve as reference import tied to the active canon

### Must not
- replace active runtime canon without explicit migration
- be split into ad hoc partial packs that lose mechanism continuity
- masquerade as current executable source of truth

## Canonical dependency
Supports Omega root as a reference import, not active runtime source.

## Horizon relation
Reference-preserving import beyond the active execution horizon.

## Authority rule
Preserve and reference; do not split into ad hoc partial packs.
