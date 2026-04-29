# Geometry Engine and UI Surface

## Principle

The geometry engine maps formal state into an operational chart.
The renderer displays the chart.
Do not mix them.

## Geometry engine responsibilities

- compute orbital positions
- compute geodesic dependencies
- compute activity overlays
- compute tension/conflict overlays
- compute focus transitions
- compute orbit precession and stability diagnostics

## Poincaré disk responsibilities

Use the disk for:
- distance-to-attractor reading
- conflict clustering
- geodesic edge placement
- transition continuity
- orbital shell differentiation

## Bloch local views

Use Bloch-like views only as local inspectors:
- local phase relations
- spin orientation
- reduced triadic or qubit-like state summaries

## UI surface responsibilities

The native UI must:
- open instantly
- show the orbital field
- support entity inspection
- support session inspection
- support memory inspection
- show provenance and dependency traces
- expose autonomy and reduction diagnostics

## Non-goals

Do not implement:
- classic tabbed admin panel as the primary experience
- fake orbital visuals without state backing
- webview-first shell as the final architecture
