# Docs Index

## Entry points

- `index.html` — static orbital cockpit preview intended for GitHub Pages
- `orbital_live.html` — manifest-driven live web preview
- `OMEGA_COCKPIT_1_0.md` — architectural specification for the Omega cockpit refactor
- `ORBITAL_PREVIEW.md` — operational guide for local launch and web publication

## Current documentation map

### Cockpit architecture
- `OMEGA_COCKPIT_1_0.md`
  - attractor-centered layout
  - orbital model
  - screen topology
  - badges, inspector, event strip
  - refactor phases

### Preview surfaces
- `index.html`
  - static web preview
- `orbital_live.html`
  - manifest-driven web preview
- `ORBITAL_PREVIEW.md`
  - local launch instructions
  - GitHub Pages publication steps

### Educational / analogy layer
- `analogies/README.md`
  - purpose and rules for using analogies
- `analogies/ANALOGY_REGISTRY.md`
  - concept -> image -> warning registry
- `analogies/TRUTH_ATTRACTOR_ANALOGIES.md`
  - analogies for truth, convergence, nodes, threads
- `analogies/MNEMONIC_BOOK_FOR_KIDS.md`
  - mnemonic teaching layer for children and beginners

## Runtime entrypoints in code

- `main/apps/omega_app.py` — legacy local runtime cockpit
- `main/apps/omega_orbital_app.py` — orbital cockpit preview
- `main/apps/orbital_cockpit.py` — orbital topology model
- `main/apps/orbital_panels.py` — navigation and identity/event builders
- `main/apps/orbital_manifest_export.py` — exporter for orbital manifest state

## Launch scripts

### Legacy
- `scripts/run_ui.sh`

### Orbital preview
- `scripts/run_orbital_ui.sh`
- `scripts/run_orbital_ui.ps1`
- `scripts/run_orbital_ui.cmd`
- `scripts/export_orbital_manifest.sh`

## Practical note

For a website, the critical files are now:
- `docs/index.html`
- `docs/orbital_live.html`
- `docs/orbital_manifest.json`

For humans navigating the repository, the documentation entry file remains:
- `docs/INDEX.md`
