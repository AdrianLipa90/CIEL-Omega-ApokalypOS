# v0.9 Operator Algebra Patch Report

## Purpose

The repository has been updated to represent lingophysics as a catalogue of concept cards plus operator cards. This prevents functional words such as `jak`, `ma`, `zawiera`, `wewnątrz`, `nie`, `i`, `do`, `od` from being flattened into ordinary concept entries.

## Added

- Lingophysical operator algebra documentation.
- Operator taxonomy across identity, possession, containment, spatial, temporal, logical, causal, modal, comparison, transformation, epistemic, affective and consensus families.
- Composition rules for duals, inverses, negations and higher-order operators.
- Rule-based disambiguation seeds for `have/mieć` and `how/jak/as/like`.
- Operator family YAML files.
- Operator composition YAML files.
- Operator algebra JSON/YAML index.
- Python modules for operator algebra, composition and disambiguation.
- Tests covering duality, Euler phase constraints and mode selection.

## Structural rule

```text
Library = Concepts + Operators + Relations + Grammar
```

## Validation result

Run from repository root:

```bash
python -m pytest -q
```

Expected: all tests pass.
