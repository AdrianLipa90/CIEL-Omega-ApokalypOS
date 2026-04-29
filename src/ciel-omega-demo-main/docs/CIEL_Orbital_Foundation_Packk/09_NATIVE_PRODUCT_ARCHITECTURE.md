# Native Product Architecture

## Product goal

A self-contained native desktop product with:
- local state engine
- geometry engine
- native renderer
- autonomy routing
- optional model integration
- no web server as the UI substrate

## Proposed top-level packages

- `ciel_orbital/kernel/`
- `ciel_orbital/registry/`
- `ciel_orbital/memory/`
- `ciel_orbital/autonomy/`
- `ciel_orbital/geometry/`
- `ciel_orbital/simulator/`
- `ciel_orbital/app/`
- `ciel_orbital/config/`
- `ciel_orbital/tests/`
- `docs/`
- `schemas/`

## Native UI stack

Recommended first implementation:
- Python
- Qt / PySide6
- QML only where needed for motion-rich orbital views

## Inference policy

Use:
1. own memory
2. own evidence / local retrieval
3. own operators
4. external LLM only if still necessary

Track:
`alpha_ciel + alpha_llm = 1`

Target:
`alpha_llm -> 0`

## MVP scope

- native startup
- orbital field view
- entity inspector
- session panel
- memory panel
- provenance view
- reduction diagnostics
- optional local model panel

## Hardening scope

- packaging
- crash handling
- state snapshot and recovery
- release bundles
- smoke tests
- offline mode
