# integration/index_registry.yaml Replacement

## Replacement rule

For the final in-place switch:
- replace the full content of `integration/index_registry.yaml`
- with the full content of `integration/registries/index_registry_v2.yaml`

## Source of truth for replacement

- source file: `integration/registries/index_registry_v2.yaml`
- target file: `integration/index_registry.yaml`

## Interpretation

The target file should become the canonical-v2 machine-readable registry surface in place.
The source v2 file may remain present during a grace period as an explicit canonical reference copy.
