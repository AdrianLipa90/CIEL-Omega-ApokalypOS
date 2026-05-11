# v1.7 Card Ontology Refactor Patch Report

Status: completed locally.

## What changed

This patch turns the v1.6 repository into a typed card system. It adds explicit ontology files, constraints, migration maps, documentation, schema and validator utilities.

## Core correction

```text
Not every word is a concept.
Concept cards are masses.
Operator cards are forces.
Grammar is geometry.
Sentences are trajectories.
```

## New validation

- concept cards cannot silently become primary operator definitions;
- operator cards missing arity/formal modes are warned;
- deictic cards may remain unresolved but must identify their anchor domain;
- scope cards preserve unresolved scope rather than guessing;
- repository files are classified into explicit ontology layers.

## Result

The repo is now ready for a cleaner Batch02 expansion because every new object must first declare or infer its card class.
