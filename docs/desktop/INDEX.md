# Desktop Layer Index

This index introduces the `CIEL-Desktop` repository from the perspective of `CIEL-_SOT_Agent`.

## Why this folder exists

The desktop layer should be visible from the Source-of-Truth side of the system.
Without that, the operator shell exists downstream but remains weakly bound in the global architecture.

This folder provides that binding.

## Documents in this folder

- `CIEL_DESKTOP_BOOTSTRAP_ON_SOT.md`
  - SoT-side bootstrap description for the desktop layer
- `CIEL_DESKTOP_GLOBAL_BINDING.md`
  - explicit dependency and truth-direction statement
- `CIEL0_PROTOCOL_BINDING.md`
  - relation between the desktop layer and the CIEL/0 Knowledge Coherence Protocol

## Short semantic summary

- `CIEL-_SOT_Agent` remains the canonical source of truth
- `CIEL-Desktop` remains the operator-facing desktop surface
- the desktop repo is downstream, not competitive
- desktop actions remain explicit and bind back into SoT-visible artifacts

## Reading order

1. `CIEL_DESKTOP_BOOTSTRAP_ON_SOT.md`
2. `CIEL_DESKTOP_GLOBAL_BINDING.md`
3. `CIEL0_PROTOCOL_BINDING.md`
