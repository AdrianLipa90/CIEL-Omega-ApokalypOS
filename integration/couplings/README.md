# Couplings sector

This directory is the target home for machine-readable coupling definitions.

## Scope

Files here should describe relation weights, pairwise links, and other explicit coupling layers, for example:
- repository coupling maps,
- sector coupling tables,
- relation-type weighted edges.

## Migration note

During refactor, legacy coupling files may still exist directly under `integration/`.
This sector establishes the target geometry first.

## Excluded

This sector is not for:
- reports,
- transient diagnostics,
- imported orbital runtime packages,
- executable bridge logic.
