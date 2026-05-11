# 33. Card Migration and Type Resolution

Version: v1.7.0

This document defines how existing v1.6 files are migrated into the v1.7 card ontology.

## Resolution pipeline

```text
path -> declared type -> inferred type -> payload check -> ontology status -> report
```

If declared and inferred types disagree, the validator reports `TYPE_MISMATCH`. If no type can be inferred, the file is classified as `ROOT_OR_MISC` and must remain visible in repo coherence reports.

## Non-guessing rule

Unknown type is not silently normalized. It is recorded as an unresolved ontology state:

```text
UNRESOLVED_CARD_TYPE
```

## Migration from v1.6

The v1.6 repo already separated major folders. v1.7 makes that separation explicit and machine-checkable. The migration map lives in:

```text
data/card_ontology/card_type_migration_map_v1_7.json
```

## Validation goals

- concept cards do not define primary operator algebra;
- operator cards define arity or formal modes;
- deictic cards declare anchor domain;
- scope cards preserve ambiguity instead of guessing;
- generated binary artifacts do not override canonical YAML/JSON sources;
- fallback records are explicit and auditable.
