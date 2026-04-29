# CIEL Ω Demo Integration

Status: canonical integration note for the demo-shell surface.

## Purpose

This document binds the public/demo shell to the SOT Agent integration layer.
It exists as the canonical cross-reference target expected by the v2 index validator.

## Canonical anchors

- Upstream shell map: `integration/upstreams/ciel_omega_demo_shell_map.json`
- Demo inventory: `integration/upstreams/ciel_omega_demo_shell_inventory.json`
- Registry: `integration/registries/index_registry_v2.yaml`
- Bridge runtime: `src/ciel_sot_agent/orbital_bridge.py`

## Integration rule

The demo shell is an imported/publication surface. It must not outrank the local canon inside
`src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega` or the SOT Agent runtime under `src/ciel_sot_agent`.

## Operational note

Use the demo shell for cockpit/publication mapping and not as a parallel source of truth.
