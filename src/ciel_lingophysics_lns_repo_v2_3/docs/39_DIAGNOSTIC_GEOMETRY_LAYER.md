# 39. Diagnostic Geometry Layer

Version: v2.0

This layer turns the current CIELingo seed library into a measurable diagnostic surface. It does not claim linguistic authority. It reports structural signals that help decide where the system is coherent, where it is under-specified, and where cross-language reconstruction may be costly.

## Purpose

The layer adds diagnostics for:

- cross-language grammar-gauge reconstruction cost,
- operator incidence and operator density,
- relation-type density by domain,
- global concept/operator graph growth,
- conflict, ambiguity, and unresolved-state tracking.

## Principle

```text
Diagnostics do not prove semantic correctness.
Diagnostics expose where semantic correctness must be checked.
```

The diagnostics are intentionally conservative. Warnings are preserved rather than smoothed away. Missing or unresolved states are valid seed states when explicitly reported.

## Main artifacts

```text
data/diagnostics/global_diagnostic_summary_v2_0.json
data/diagnostics/cross_language_reconstruction_costs.csv
data/diagnostics/operator_density_by_concept.csv
data/diagnostics/conflict_ambiguity_unresolved_registry.json
data/graphs/global_diagnostic_graph.json
outputs/heatmaps/v2_0_cross_language_reconstruction_cost.png
outputs/heatmaps/v2_0_operator_density_by_domain.png
outputs/heatmaps/v2_0_relation_type_matrix.png
```

## Interpretation

A high grammar-gauge distance does not mean translation failure. It means more structure must be reconstructed through word order, prepositions, event frames, case gauge, scope, or context.

A dense operator profile does not mean semantic truth. It means the concept is heavily mediated by functional words and should receive stronger validation when used in sentence-level tests.
