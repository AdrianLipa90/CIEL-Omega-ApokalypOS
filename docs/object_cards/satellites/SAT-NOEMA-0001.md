# SAT-NOEMA-0001 — NOEMA ⇄ SOT ⇄ SapiensOrbital

## Identity
- **subsystem_id:** `SAT-NOEMA-0001`
- **name:** `NOEMA ⇄ SOT ⇄ SapiensOrbital`
- **class:** `satellite_export_surface`
- **active_status:** `ACTIVE_EXPORT_SURFACE`

## Anchors
- `integration/imports/noema_sapiens_orbital/README.md`
- `integration/imports/noema_sapiens_orbital/MANIFEST.json`
- `integration/imports/noema_sapiens_orbital/CONTRACT_CONCORDANCE.json`
- `integration/imports/noema_sapiens_orbital/generated/registry_export.noema`

## Role
Canonical DSL/spec/export bridge for projected meaning from the canonical orbital/nonlocal state.

## Flow
- **input_from:** `canonical orbital/nonlocal registry`
- **output_to:** `registry_export.noema + contract concordance`

## Authority
### May
- export projected meaning from canonical registry state
- carry human-auditable specification and concordance artifacts
- serve as downstream DSL/spec surface for audited projection

### Must not
- override SOT runtime or registry source of truth
- introduce independent orbital logic outside canonical bridge/reduction flow
- be treated as upstream donor of runtime state

## Canonical dependency
Depends on canonical Omega/Orbital/Bridge outputs.

## Horizon relation
Projected/exported layer beyond the bridge horizon.

## Authority rule
SOT runtime and registries remain canonical; NOEMA is export/spec surface only.
