# v1.2 Dynamic Deictic Operator Patch Report

## Summary

This patch adds dynamic deictic operators to CIEL-LNS/Ω Lingophysics.

The user correction was: words such as `gdzieś` and `kiedyś` are still dynamic operators. This patch formalizes that class.

## Added

- `docs/22_DYNAMIC_DEICTIC_OPERATORS.md`
- `docs/23_DYNAMIC_DEIXIS_RESOLUTION_ALGORITHMS.md`
- `data/operator_families/deictic_dynamic.yaml`
- `data/operator_families/deictic_dynamic.json`
- `data/operator_cards/dynamic_deictic_operators_5lang.yaml`
- `data/operator_cards/dynamic_deictic_operators_5lang.json`
- `data/operator_cards/dynamic_deictic_surfaces_5lang.csv`
- `data/operator_compositions/dynamic_deictic_resolution.yaml`
- `data/graphs/dynamic_deictic_operator_graph.json`
- `data/graphs/dynamic_deictic_operator_graph.graphml`
- `data/heatmaps/dynamic_deictic_feature_matrix.csv`
- `schemas/ciel_lns_dynamic_deictic_operator.schema.json`
- `src/lingophysics/dynamic_deixis.py`
- `tests/test_dynamic_deixis.py`

## Core rule

```text
gdzieś / somewhere   = unresolved spatial anchor
kiedyś / sometime    = unresolved temporal anchor
jakoś / somehow      = unresolved manner anchor
skądś / from somewhere = unresolved source anchor
dokądś / to somewhere = unresolved destination anchor
```

## Safety / epistemic note

The system must preserve unresolved anchors instead of hallucinating false precision.

```text
UnresolvedAnchor is a valid semantic state.
```
