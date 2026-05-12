# CIEL-LNS/Ω Lingophysics Repository

Version: `0.6.0-draft`  
Generated: `2026-05-10T00:36:33.852952+00:00`

This repository is a seed implementation and specification pack for **CIEL-LNS/Ω**, a linguistic-network standard that treats meaning as rhythmic holonomic geometry.

It contains:

- Markdown specification files for the lingophysical formalism.
- JSON Schemas for objects, relations, language profiles and patterns.
- YAML language profiles for English and Polish.
- Small handcrafted bilingual seed data for English and Polish.
- HDF5 seed store for lexemes, relations and phase/mass arrays.
- Reference algorithms for computing semantic mass, potential, holonomy, antonym constraints, consensus and cross-linguistic drift.

This repo intentionally does **not** include proprietary dictionary data. PWN and Oxford data should only be imported through a licensed API/export or with explicit permission. For open bootstrap data, prefer Open English WordNet and plWordNet/Słowosieć when their license terms fit the project.

## Core slogan

> Meaning is not a token. Meaning is a structured trajectory through glyph, grammar, knot, potential, orbit, memory, consensus and identity.

## Canonical pipeline

```text
Surface
→ Language gauge
→ Equation
→ Semantic knot
→ Invariant
→ Meaning state
→ Semantic mass
→ Potential field
→ Orbit / attractor
→ Affect and outcome
→ Consensus holonomy
→ Memory
→ Identity
```

## Repository layout

```text
docs/       Formal specification and algorithms
schemas/    JSON Schema definitions
configs/    Runtime and language profiles
data/       Seed lexeme data in YAML/JSON/HDF5
src/        Reference Python algorithms
tests/      Minimal validation notes/examples
examples/   Example sentence objects
```

## Immediate next step

1. Validate the schemas.
2. Expand seed lexemes using licensed/open lexical sources.
3. Add parser adapters for Polish and English.
4. Run cross-linguistic invariant tests.
5. Calibrate weights and thresholds empirically.


## v0.7 Multilingual concept-card patch

This patch adds the first full concept card: `water/woda`. A concept card is one semantic attractor with many language surfaces, including near-synonyms, antonyms, inflected forms, contextual use, language-specific operators, grammar gauge vectors, heatmaps and graph exports.

Key files:

- `data/concept_cards/water.yaml`
- `data/concept_cards/water.json`
- `data/concept_cards/water_multilingual_card.csv`
- `data/grammar/*_grammar_math.yaml`
- `data/heatmaps/*.csv`
- `outputs/heatmaps/*.png`
- `outputs/graphs/water_concept_graph.png`
- `data/hdf5/ciel_lingophysics_concept_cards_v0_7.h5`


## v0.8 update: Operator Library

This repository now separates `CONCEPT_CARD` from `OPERATOR_CARD`.

New files:
- `data/operator_cards/core_operators_5lang.yaml`
- `data/operator_cards/core_operators_5lang.json`
- `data/operator_cards/core_operator_cards.csv`
- `data/operator_cards/core_operator_surfaces_5lang.csv`
- `data/operator_cards/core_operator_duals.csv`
- `data/operator_cards/core_operator_library.xlsx`
- `schemas/ciel_lns_operator_card.schema.json`
- `docs/12_OPERATOR_CARD_MODEL.md`
- `docs/13_FUNCTIONAL_WORDS_AND_DUAL_OPERATORS.md`
- `src/lingophysics/operator_card.py`

Core principle:

```text
Concept cards store semantic bodies.
Operator cards store functions that bind, transform, localize, negate, query or phase-shift concept cards.
```
## v0.9 Operator Algebra Patch

This patch formalizes lingophysics as catalogued operator algebra, not merely concept-card storage.

New canonical split:

```text
CONCEPT_CARD    semantic body / attractor / mass-bearing object
OPERATOR_CARD   function / force / curvature acting on concepts, clauses or operators
```

New modules:

- `docs/14_LINGOPHYSICAL_OPERATOR_ALGEBRA.md`
- `docs/15_OPERATOR_TAXONOMY.md`
- `docs/16_OPERATOR_COMPOSITION_RULES.md`
- `docs/17_OPERATOR_DISAMBIGUATION_AND_ARGUMENT_TYPING.md`
- `data/operator_families/*.yaml`
- `data/operator_compositions/*.yaml`
- `data/operator_algebra/operator_algebra_index.{json,yaml}`
- `src/lingophysics/operator_algebra.py`
- `src/lingophysics/operator_composition.py`
- `src/lingophysics/operator_disambiguation.py`

Core theorem-style phrase:

```text
Concept cards are masses. Operator cards are forces. Grammar is geometry. Sentences are trajectories.
```


## v1.0 Local Batch01 Patch

The repository now includes the first batch-library seed:

- 36 foundational concept cards
- 5 languages per card: PL, EN, DE, FR, ES
- 180 language panels
- CSV, XLSX, JSON, YAML, SQLite, HDF5, GraphML, and PNG outputs
- concept/operator separation tests

The core implementation rule is:

```text
Library = Concepts + Operators + Relations + Grammar
```

Functional words are not stored as ordinary concepts. They are operator cards or operator families.


## v1.1 Case Gauge Layer

Adds Slavic case mapping as compressed semantic-role operators and target-language reconstruction strategies for EN/DE/FR/ES.


## v1.2 Dynamic Deictic Operators

Adds dynamic deictic operators such as `gdzieś`, `kiedyś`, `jakoś`, `skądś`, and `dokądś`. These are represented as unresolved anchors over place, time, manner, source, and destination, not as ordinary concept cards.


## v1.3 — Predicate Valency & Ontological Aspect

Adds event frames and ontological-aspect operators:

- predicate valency defines allowed roles before cases, word order or prepositions surface them;
- `koto/mono` style distinctions map abstract/event/fact vs object-like thinghood;
- `ser/estar` style distinctions split identity-being from state/location-being;
- English and Polish `be/być` are treated as polyfunctional operators requiring complement and context resolution.

## v1.4 TAM-E and Storage Fallback

This version adds the TAM-E layer for tense, aspect, mood, modality and evidentiality. It also adds an explicit storage fallback protocol: if HDF5 or another preferred storage target fails, the pipeline writes JSON/JSONL fallback data and records the error as part of the audit trail.


## v1.7 Card Ontology Refactor

The repository now enforces a typed card ontology. New data should be classified as one of the explicit card layers: concept, operator, operator family, operator composition, grammar, case gauge, case mapping, event frame, ontological aspect, TAM-E, deictic, scope, or fallback. This prevents concept masses and operator forces from collapsing into one flat dictionary layer.


## v1.8 Batch02 Expansion

Adds 36 concept cards × 5 languages as the second curated library batch.


## v2.0 Diagnostic Geometry Layer

Adds global diagnostics for cross-language reconstruction cost, operator density, relation-type matrices, conflict/unresolved registry, and a global concept/operator diagnostic graph.


## v2.1 Roadmap and Learning Policy

Adds the current staged roadmap and learning policy:

- NOEMA-first retrieval and local validation before GGUF/LLM calls.
- GGUF/LLM as advisory teacher-validator, not canonical source of truth.
- Explicit batch-size policy as graph density grows.
- Technical repository style: no metaphorical claims as technical assertions.
- Next recommended patch: `v2.2 NOEMA Retrieval and Inference Gate`.

## v2.2 NOEMA Retrieval and Inference Gate

The current local patch adds NOEMA-first routing and an inference gate. GGUF is
kept as an advisory teacher-validator, not as a canonical source of truth. The
system explicitly does not claim partial execution of dense GGUF weights;
expected savings come from retrieval, context reduction, model-size gating,
cache reuse, and fewer validation retries.

