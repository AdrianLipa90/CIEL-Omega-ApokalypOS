# Card Type Registry and Status Discipline

CIELingo separates linguistic objects into typed layers. This prevents ordinary concept cards from being confused with operators, scope markers, case gauges, deictic anchors, event frames, or generated graph artifacts.

## Main card/data classes

- `CONCEPT_CARD`: semantic masses and attractors
- `OPERATOR_CARD`: functions/forces that transform concepts
- `OPERATOR_FAMILY`: grouped operators such as possession, containment, modality
- `OPERATOR_COMPOSITION`: duals, inverses, negations, higher-order rules
- `GRAMMAR_CARD`: language-specific grammar mathematization
- `CASE_GAUGE_CARD`: case systems as hidden role operators
- `EVENT_FRAME`: valency frames and allowed predicate roles
- `ONTOLOGICAL_ASPECT`: koto/mono, ser/estar, identity/state being
- `TAME_CARD`: tense/aspect/mood/modality/evidentiality
- `DYNAMIC_DEICTIC_CARD`: somewhere/sometime/somehow style unresolved anchors
- `SCOPE_CARD`: quantifiers, negation and scope stacks
- `JSON_FALLBACK`: safe persistence under storage degradation

## Status discipline

`draft_seed` means hand-curated and usable for experiments, but not authoritative.
`canonical_schema` means a structure expected to remain stable unless intentionally versioned.
`generated` means reproducible output that can be regenerated.
`fallback` means legal degraded persistence.
`needs_review` means visible uncertainty.

The validator must never silently promote seed material to canonical knowledge.
