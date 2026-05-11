# 40. Diagnostic Metric Registry

Status: `v2.0-draft`

The metric registry defines names, meanings, and thresholds for CIELingo diagnostic geometry.

## Metrics

### language_panel_coverage

Observed language panels divided by expected `concepts × 5` panels. A value below 1 means at least one concept/language surface is missing or not detected.

### operator_coverage

Fraction of concepts with at least one operator hook. Low coverage means the library may contain semantic masses without force/trajectory links.

### relation_density

Directed relation count divided by `N × (N - 1)`. This is a graph sparsity signal, not a quality score by itself.

### case_reconstruction_cost_mean

Average cost for reconstructing case-gauge information in languages that express roles through word order, prepositions, articles, clitics, or predicate valency rather than rich case morphology.

## Review principle

Metrics must generate review actions: add missing panels, add operator hooks, mark unresolved, split overloaded operators, or add relation edges. Silent failures are not valid.
