# v1.4 TAM-E and Storage Fallback Patch Report

## Added

- TAM-E layer: tense, aspect, mood, modality and evidentiality.
- Event phase encoding for grammatical event states.
- Cross-language TAM-E operator surfaces for PL, EN, DE, FR, ES.
- Storage fallback protocol: if HDF5 export fails, write JSON fallback and explicit report.
- Tests for TAM-E signatures and fallback behavior.

## New files

```text
docs/26_TAME_TENSE_ASPECT_MOOD_EVIDENTIALITY.md
docs/27_STORAGE_FALLBACK_JSON_PROTOCOL.md
data/tame/tame_operator_system.yaml
data/tame/tame_operator_system.json
data/tame/tame_feature_matrix.csv
data/operator_families/tame_modality_evidentiality.yaml
data/operator_compositions/tame_scope_interactions.yaml
schemas/ciel_lns_tame.schema.json
schemas/ciel_lns_storage_fallback.schema.json
src/lingophysics/tame.py
src/lingophysics/storage_fallback.py
tests/test_tame_layer.py
tests/test_storage_fallback.py
```

## Fallback rule

```text
try preferred storage
if error: write JSON fallback + explicit report
```

## Epistemic status

Curated seed. No external dictionary import.
