# Sapiens Integration Layer

## Role

This folder stores machine-readable contracts and human-readable notes for the Sapiens panel layer.

It is the configuration and integration surface for the future Sapiens Main Panel.
It is not the orbital runtime itself and not the canonical theory layer.

## Current objects

- `settings_defaults.json` — default panel configuration values.
- `panel_manifest.json` — machine-readable manifest for the Sapiens panel foundation.
- `AGENT1.md` — scope note for Agent 1 work in this layer.

## Structural rule

The Sapiens panel must remain a controller-driven shell above:
- orbital state,
- bridge state,
- session state,
- settings state.

It must not become a second source of truth for orbital or bridge logic.
