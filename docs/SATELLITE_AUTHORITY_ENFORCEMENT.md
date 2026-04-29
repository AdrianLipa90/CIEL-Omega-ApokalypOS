# Satellite Authority Enforcement

This document records active enforcement of satellite subsystem authority in code surfaces.

## Enforced surfaces
- `scripts/export_orbital_registry_to_noema.py` -> `SAT-NOEMA-0001`
- `src/ciel_sot_agent/sapiens_client.py` -> `SAT-SAPIENS-0001`
- `src/ciel_sot_agent/sapiens_panel/controller.py` -> `SAT-SAPIENS-0001`
- `src/ciel_sot_agent/gui/routes.py` -> `SAT-SAPIENS-0001`
- `scripts/run_audio_orbital_probe.py` -> `SAT-AUDIO-0001`

## Rule
Satellite surfaces may express, export, transport, or render canonical state, but they must not become a second source of truth for orbital, bridge, or canonical runtime logic.

## Environment note
- GUI authority surface depends on `flask` and is declared both in optional GUI dependencies and pinned runtime requirements for local surface validation.
