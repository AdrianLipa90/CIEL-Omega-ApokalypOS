# CIEL Structural Statistics

CIEL statistics are not corpus frequencies by default. They are structural measurements over the card graph and linguistic operators.

Core statistics:

| Statistic | Meaning |
|---|---|
| `operator_incidence` | how strongly a token/card behaves as an operator |
| `concept_mass` | semantic mass of a concept card |
| `case_reconstruction_cost` | cost of recovering a role across languages |
| `scope_ambiguity` | unresolved or competing scope readings |
| `deixis_unresolved_score` | degree of unresolved place/time/manner anchoring |
| `event_frame_fit` | compatibility of token roles with a predicate frame |
| `tame_vector_norm` | amount of TAM-E marking carried by expression |
| `antonym_phase_error` | violation of Euler antonym constraint |
| `synonym_phase_error` | violation of synonym phase coherence |
| `graph_distance` | concept/operator graph separation |

These statistics can be used as:

- extra input features,
- target labels for auxiliary losses,
- attention bias components,
- validation checks after generation,
- diagnostics for cross-language reconstruction.

The important difference from ordinary statistics:

```text
Token co-occurrence says: these words appear together.
CIEL statistics say: these structures must remain invariant.
```
