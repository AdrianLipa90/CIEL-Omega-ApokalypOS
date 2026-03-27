# Orbital integration import

This directory hosts a dedicated Orbital import from the current audited relational mechanism workspace.

Imported into a separate branch for integration review only.

## Source

- source snapshot: `CIEL_RELATIONAL_MECHANISM_REPO_snapshot_no_gguf_post_holonomic_consolidation_2026-03-27_v2.zip`
- source module root: `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/`
- source manifests: `manifests/orbital/sectors_global.json`, `manifests/orbital/couplings_global.json`

## Layout here

- `integration/Orbital/main/` — imported orbital module snapshot
- `integration/Orbital/main/manifests/` — imported orbital global manifests
- `integration/Orbital/IMPORT_MANIFEST.json` — machine-readable import note

This import does not modify the theory repository and is intended as a standalone integration layer inside `CIEL-_SOT_Agent`.
