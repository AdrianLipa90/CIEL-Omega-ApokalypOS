# CIEL-LNS/Ω v0.7 Concept Card Model

A concept card is not a dictionary entry. It is a multilingual attractor object. One card represents one conceptual basin, while each language provides a local surface, grammar gauge, lexical family, antonym phase constraints, contextual use and operators.

## Canonical rule

```text
ConceptCard = Attractor + {LanguageSurface_l} + Relations + Operators + Metrics + Provenance
```

For a concept `c` and language `l`:

```text
Surface_l(c) -> GrammarGauge_l -> Equation_l -> Knot_l -> Invariant(c)
```

The card stores translations, near-synonyms, antonyms, inflected forms, contextual examples, graph edges and operator mappings. It must not copy proprietary dictionary definitions unless licensing allows machine-readable redistribution.

## Water card

The seed card `data/concept_cards/water.yaml` demonstrates the pattern: PL/EN/DE/FR/ES/JA surfaces orbit around one water attractor.
