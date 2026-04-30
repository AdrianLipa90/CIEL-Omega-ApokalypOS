# SAT-GEOMETRY-0001 — ciel_geometry: Poincaré Disk Engine

## Identity
- **subsystem_id:** `SAT-GEOMETRY-0001`
- **name:** `ciel_geometry`
- **class:** `geometry_engine`
- **active_status:** `ACTIVE`
- **foundation_pack_phase:** `P3 + P5 + P6`
- **last_updated:** `2026-04-30`
- **tests:** `30 passed`

## Anchors
- `src/ciel_geometry/__init__.py`
- `src/ciel_geometry/loader.py`
- `src/ciel_geometry/disk.py`
- `src/ciel_geometry/edges.py`
- `src/ciel_geometry/layout.py`
- `src/ciel_geometry/semantic_mass.py` — P3: M_sem operator
- `src/ciel_geometry/subjective_time.py` — P3: Δτ operator
- `src/ciel_geometry/renderer_ascii.py`
- `src/ciel_geometry/renderer_mpl.py`
- `~/.claude/ciel_site/orbital.html` — Bloch sphere + Poincaré disk (HTML/JS)
- `tests/test_ciel_geometry.py`

## Role
Maps live CIEL system state (sectors, entities, coupling matrix, bridge metrics) onto a Poincaré disk geometry. Produces a `DiskLayout` snapshot — nodes with (x, y) positions, geodesic edges, and system metadata — ready for any renderer (ASCII, matplotlib, PySide6).

## Data Sources (read-only)
- `integration/Orbital/main/manifests/sectors_global.json` — 6 orbital sectors (θ, φ, amplitude)
- `integration/Orbital/main/manifests/couplings_global.json` — coupling matrix W_ij
- `integration/registries/ciel_entity_cards.yaml` — 40+ entities (coupling_ciel, phase, horizon_class)
- `integration/reports/orbital_bridge/orbital_bridge_report.json` — live bridge state

## Core Functions
- `poincare_radius(θ)` = tanh(tan(θ/2)) — maps polar angle to disk radius
- `sector_to_disk(θ, φ)` — spherical sector coords → (x, y)
- `entity_to_disk(coupling, phase)` — entity coupling+phase → (x, y)
- `geodesic_arc(x1,y1, x2,y2)` — Euclidean arc approximating hyperbolic geodesic
- `build_layout()` — full DiskLayout from live data
- `build_mass_table()` — P3: semantic mass M_sem per node + Kepler orbit period
- `compute_from_bridge()` — P3: subjective time Δτ per node from live bridge state

## Flow
- **input_from:** `integration/` JSON/YAML (updated by pipeline on each cycle)
- **output_to:** `DiskLayout` (nodes + edges + metadata), downstream renderers

## Authority
### May
- read from `integration/` manifests and registries
- produce `DiskLayout` snapshots for visualization
- be called by renderers (ASCII, GUI, export)

### Must not
- write to `integration/` or `src/ciel_sot_agent/`
- modify pipeline state
- implement GUI or frontend logic (that is P6 scope)

## Renderers available
- `renderer_ascii.py` — terminal ASCII disk (debug)
- `renderer_mpl.py` — matplotlib interactive cockpit (P6 MVP)
  - `python -m ciel_geometry.renderer_mpl` — static window
  - `python -m ciel_geometry.renderer_mpl --live` — auto-refresh every 5s
  - `python -m ciel_geometry.renderer_mpl --save out.png` — headless export

## Open (P6 next)
- PySide6 / Qt native renderer consuming `build_layout()` (when PySide6 installed)
- Click/inspect node in interactive window
- Animate coupling changes between pipeline cycles
