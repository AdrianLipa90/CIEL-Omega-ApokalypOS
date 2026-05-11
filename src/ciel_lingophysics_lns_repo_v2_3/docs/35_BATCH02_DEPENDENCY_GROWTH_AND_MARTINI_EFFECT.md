# Batch02 Dependency Growth and the Martini Effect

As the concept library grows, every new card must be compared against the existing semantic field. The expensive part is not adding a row; it is resolving a narrowing glass of relations: synonyms, antonyms, false friends, operator hooks, event frames, case realizations, scope interactions, and cross-language reconstruction cost.

## Required pipeline

```text
new card
→ classify card type
→ attach language panels
→ attach operator hooks
→ compare against existing cards
→ detect synonym / antonym / false-friend candidates
→ map grammar per language
→ update graph
→ update heatmaps
→ validate
→ report unresolved issues
```

## Batch-size rule

```text
0–100 cards      batch 36
100–200 cards    batch 20
200+ cards       batch 15
400+ cards       batch 10 or curated patches
```
