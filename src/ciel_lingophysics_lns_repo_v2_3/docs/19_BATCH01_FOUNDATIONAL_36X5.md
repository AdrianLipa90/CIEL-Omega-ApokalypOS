# 19. Batch01 Foundational 36×5

Batch ID: `batch01_foundational_36x5`

This patch adds 36 foundational concept cards across five languages: PL, EN, DE, FR, ES.

The batch is a draft seed. It does not import PWN, Oxford, or any external dictionary dataset. All lexical material is a working seed for later human validation.

## Counts

- Concept cards: 36
- Language panels: 180
- Relation rows: 454
- Operator links: 115

## Data artifacts

- `data/concept_cards/batch01_foundational_36x5/*.yaml`
- `data/concept_cards/batch01_foundational_36x5/*.json`
- `data/concept_cards/batch01_foundational_36x5/batch01_multilingual_concept_cards.xlsx`
- `data/sqlite/cielingo_batch01_v1_0.sqlite`
- `data/hdf5/cielingo_batch01_v1_0.h5`
- `data/graphs/batch01_concept_operator_graph.graphml`
- `outputs/heatmaps/batch01_grammar_gauge_distance.png`
- `outputs/heatmaps/batch01_concept_operator_incidence.png`

## Validation status

The test suite verifies basic counts, language coverage, concept/operator separation, SQLite presence, and operator-link integrity.
