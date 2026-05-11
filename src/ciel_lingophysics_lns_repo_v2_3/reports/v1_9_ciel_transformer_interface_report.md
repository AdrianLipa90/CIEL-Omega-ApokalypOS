# v1.9 CIEL-Transformer Interface Patch Report

Added deterministic interface components for transformer-facing CIEL-LNS/Ω features.

## Added

- `docs/36_CIEL_TRANSFORMER_INTERFACE.md`
- `docs/37_CIEL_STRUCTURAL_STATISTICS.md`
- `docs/38_AUXILIARY_LOSSES_AND_ATTENTION_BIAS.md`
- `data/transformer_features/*`
- `schemas/ciel_lns_transformer_feature_tensor.schema.json`
- `schemas/ciel_lns_attention_bias.schema.json`
- `src/lingophysics/transformer_features.py`
- `src/lingophysics/attention_bias.py`
- `src/lingophysics/auxiliary_losses.py`
- `src/lingophysics/ciel_validator_loop.py`
- `tests/test_transformer_features.py`
- `tests/test_attention_bias.py`
- `tests/test_auxiliary_losses.py`
- `tests/test_ciel_validator_loop.py`

## Boundary

This is an interface patch, not a trained model. It defines feature tensors, attention-bias rules, auxiliary loss descriptors and a validator loop that can later wrap a transformer.

## Epistemic status

`draft_seed`: the weights and feature dimensions are provisional and must be validated empirically.
