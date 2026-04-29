# SAT-SAPIENS-0001 — Sapiens Integration Layer

## Identity
- **subsystem_id:** `SAT-SAPIENS-0001`
- **name:** `Sapiens Integration Layer`
- **class:** `satellite_interaction_surface`
- **active_status:** `ACTIVE_SURFACE_AND_REPORT_LAYER`

## Anchors
- `integration/sapiens/README.md`
- `integration/sapiens/panel_manifest.json`
- `src/ciel_sot_agent/sapiens_client.py`
- `src/ciel_sot_agent/sapiens_panel/controller.py`
- `src/ciel_sot_agent/sapiens_panel/reduction.py`

## Role
Human-model shell/controller above bridge/orbital/session/settings state.

## Flow
- **input_from:** `orbital_bridge reduction outputs`
- **output_to:** `packet/session/transcript/panel state`

## Authority
### May
- express bridge-reduced state as packet/session/transcript/panel surfaces
- manage human-facing controller and settings state
- host shell logic above bridge/orbital outputs

### Must not
- become a second source of truth for orbital logic
- recompute bridge state independently of the canonical reduction path
- override canonical runtime identities or couplings

## Canonical dependency
Receives and expresses bridge state; does not define it.

## Horizon relation
Interactive surface just beyond bridge reduction.

## Authority rule
Must not become second source of truth for orbital or bridge logic.
