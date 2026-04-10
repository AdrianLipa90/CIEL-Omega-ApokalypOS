# Orbital Integration Addendum

## Purpose

This file brings the imported and extended orbital subsystem into the human-readable navigation layer of `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold`.

It does not replace `docs/INDEX.md`.
It acts as an addendum until direct in-place update of the main index is available.

## Orbital layer in this repository

Primary path:
- `integration/Orbital/`

Important objects:
- `integration/Orbital/README.md` — orbital import overview
- `integration/Orbital/AGENT1.md` — orbital integration scope
- `integration/Orbital/IMPORT_MANIFEST_V2.md` — repaired import addendum for the broken original manifest
- `integration/Orbital/main/AGENT1.md` — executable orbital package scope
- `integration/Orbital/main/global_pass.py` — read-only diagnostic orbital pass
- `scripts/run_orbital_global_pass.py` — launcher for the orbital pass

## Current role of the orbital subsystem

Inside this repository the orbital layer is currently treated as:
- imported mechanism/runtime snapshot,
- diagnostic subsystem,
- read-only integration-facing pass,
- not yet the full engine of the SOT repository.

## Coupling chain

The current orbital execution chain is:

1. `scripts/run_orbital_global_pass.py`
2. `integration/Orbital/main/global_pass.py`
3. `integration/Orbital/main/dynamics.py`
4. `integration/Orbital/main/metrics.py`
5. generated orbital reports under `integration/Orbital/main/reports/`

## Status

The orbital layer is now minimally executable.
The next step is to fold its report and object metadata into the broader machine-readable indices.
