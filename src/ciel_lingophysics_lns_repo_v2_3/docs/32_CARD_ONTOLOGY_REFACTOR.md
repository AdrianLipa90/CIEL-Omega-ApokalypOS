# 32. Card Ontology Refactor

Version: v1.7.0

This patch hardens the CIELingo repository around a strict card ontology. The main correction is simple but structural:

```text
Not every word is a concept.
Some words are operators, gauges, anchors, scopes, frames, or grammatical control structures.
```

The library is therefore not a flat dictionary. It is a typed semantic machine:

```text
Library = Concepts + Operators + Relations + Grammar
```

## Canonical card classes

- `CONCEPT_CARD`: semantic masses and attractors. Examples: water, fire, truth, memory.
- `OPERATOR_CARD`: functions and forces. Examples: inside, contains, have, not, how/as/like.
- `OPERATOR_FAMILY`: algebraic families of related operators.
- `OPERATOR_COMPOSITION`: duals, inverses, negation and higher-order composition rules.
- `GRAMMAR_CARD`: local grammar gauge per language.
- `CASE_GAUGE_CARD`: hidden role operator encoded in morphology.
- `CASE_MAPPING`: cross-language realization strategy for case roles.
- `EVENT_FRAME`: predicate valency skeleton.
- `ONTOLOGICAL_ASPECT`: thing/concept and identity/state splits, including koto/mono and ser/estar.
- `TAME_CARD`: tense, aspect, mood, modality, evidentiality.
- `DEICTIC_CARD`: unresolved dynamic anchor, such as somewhere/sometime/somehow.
- `SCOPE_CARD`: quantifier, negation and scope control.
- `JSON_FALLBACK`: explicit degraded persistence record.

## Separation rule

A card should have one primary ontological class. Cross-links are allowed, but primary identity must stay clean. For example, `water` may link to `Inside` or `Contains`, but it does not become an operator. Likewise `inside` may mention `water` in examples, but it does not become a concept card.

## Why this matters

Without typed cards, the graph starts confusing masses with forces. A concept card curves semantic space by mass; an operator card changes trajectories by transformation power. These must be indexed separately before Batch02 expands the library.
