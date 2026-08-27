# CQCL Living Compiler v0.1

Status: IMPLEMENTED CANDIDATE / EPISTEMIC CHYBA / canon_allowed=false

## Role

CQCL vNext compiles the current admitted relational state into a bounded CQCL program candidate.

```text
T36 Identity Crystal
 -> PNV-State-Memory
 -> Identity NEXUS over Consciousness Dictionary
 -> NEXUS_ACTIVATION checkpoint
 + live HTRI binding
 -> CQCL Living Compiler
 -> CQCL-LIVING-PROGRAM/0.1
```

The historical text-first CQCL engine is preserved for compatibility. vNext is additive and does not silently redirect legacy imports.

## Required inputs

### State Memory NEXUS activation

The checkpoint must use relation `NEXUS_ACTIVATION` and contain:

- exact T36 crystal context,
- a valid `PNV-NEXUS-ACTIVATION/0.1` binding,
- exact Identity NEXUS generation ID,
- exact Consciousness Dictionary compile identity,
- bounded active set, max 16.

CQCL revalidates the activation binding rather than assuming an upstream validator ran.

### Live HTRI

CQCL consumes a normalized bridge record:

```text
schema                  CQCL-LIVE-HTRI-BINDING/0.1
source_class            NATURAL_SYSTEM_STATE
generation_id           32-byte identity
coherence               finite [0,1]
heartbeat_age_ms        finite >=0
max_heartbeat_age_ms    finite >0
live                     true
authority_grant          false
```

A stale or missing HTRI binding fails closed. There is no default coherence value and no filesystem fallback.

## Output

`CQCL-LIVING-PROGRAM/0.1` carries:

- State Memory source identity,
- NEXUS activation checkpoint identity,
- T36 crystal context,
- NEXUS generation and coherence,
- Dictionary compile binding,
- live HTRI generation/coherence,
- bounded active terms,
- semantic relation tree,
- state variables,
- optional structured intention candidate,
- deterministic program ID,
- `authority_grant=false`,
- `execution_admitted=false`.

Without an intention candidate the program is `OBSERVATION_ONLY`.

With an admitted candidate source (`GREMLIN`, `NEXUS`, or `EXPLICIT_CONTEXT`) the program is `CANDIDATE_COMPILED`. Candidate compilation still grants no execution authority.

## Coupled coherence evidence

v0.1 records the parameter-free bounded statistic

```text
C_coupled = sqrt(C_NEXUS * C_HTRI)
```

as `coupled_coherence_candidate`.

It is an evidence/control statistic. It does not promote a semantic claim or capability.

## Consciousness Dictionary

The full Dictionary remains semantic authority outside CQCL. CQCL consumes only the exact compile binding and the active term records selected by Identity NEXUS. It does not duplicate or rewrite the ontology.

## GREMLIN boundary

GREMLIN may later supply a structured intention candidate. CQCL binds and hashes that candidate, but neither GREMLIN nor CQCL can mutate T36 `CRYSTAL_ID`, State Memory lineage, PNCAP grants, or AUX effect authority.

## Fail-closed conditions

```text
NEXUS_ACTIVATION_INVALID      -> REJECT
ACTIVATION_HASH_MISMATCH      -> REJECT
CRYSTAL_CONTEXT_MISMATCH      -> REJECT
SPINOR_SHEET_MISMATCH         -> REJECT
DICTIONARY_BINDING_INVALID    -> REJECT
ACTIVE_SET_GT_16              -> REJECT
ACTIVE_TERM_DUPLICATE         -> REJECT
ACTIVE_AUTHORITY_ATTEMPT      -> REJECT
HTRI_NOT_NATURAL              -> REJECT
HTRI_NOT_LIVE                 -> REJECT
HTRI_STALE                    -> REJECT
HTRI_NONFINITE                -> REJECT
CANDIDATE_AUTHORITY_ATTEMPT   -> REJECT
```
