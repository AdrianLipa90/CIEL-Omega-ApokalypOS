# v1.1 Case Gauge Patch Report

## Added

- `docs/20_CASE_GAUGE_LAYER_SLAVIC_TO_WEAK_CASE_LANGUAGES.md`
- `docs/21_CASE_GAUGE_ALGORITHMS.md`
- `data/case_systems/slavic_case_gauge.yaml/json`
- `data/case_mappings/pl_case_to_5lang_surface_strategies.csv`
- `data/case_mappings/case_gauge_reconstruction_cost_matrix.csv`
- `data/graphs/case_gauge_mapping_graph.json/graphml`
- `schemas/ciel_lns_case_gauge.schema.json`
- `src/lingophysics/case_gauge.py`
- `tests/test_case_gauge.py`

## Conceptual patch

Slavic cases are now represented as compressed role operators. Mapping to English/French/Spanish is not treated as simple preposition replacement; it is handled as target-language reconstruction through word order, adpositions, clitics, agreement, punctuation, and verb valency.

German remains a bridge language because it preserves productive case morphology, although less richly than Polish.

## Status

Curated formal seed. No external dictionary content imported.
