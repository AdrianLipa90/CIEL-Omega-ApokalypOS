# NOEMA and GGUF Teacher-Validator Roadmap v2.1

This document defines the repository-level policy for using NOEMA retrieval and GGUF/LLM validation during CIELingo model development.

## 1. Roles

```text
NOEMA       retrieval, routing, nonlocal card/operator access, local subgraph selection
CIELingo    structured parser, feature tensor builder, validator, learner
GGUF/LLM    advisory teacher-validator for uncertain or factual cases
Human       final reviewer for unresolved conflicts and canonical promotion
```

## 2. Non-goals

This policy does not claim that a dense GGUF model executes only a selected subset of internal weights. A dense local model still usually runs full inference for generated tokens. Energy reduction is expected mainly from:

- shorter context,
- fewer model calls,
- fewer repair retries,
- local graph/rule resolution,
- confidence-based escalation,
- cache reuse,
- possible future sparse/adapted execution.

## 3. Teacher-validator loop

```text
CIELingo proposes analysis
→ local validator checks invariants
→ NOEMA checks graph consistency
→ if confidence is insufficient, GGUF gives advisory verdict
→ verdict fusion writes agree/disagree/uncertain/needs_review
→ canonical status only after structural validation and review/provenance when needed
```

## 4. Confidence policy

```text
if local_confidence >= 0.85 and validator_pass and no_noema_conflict:
    do_not_call_gguf
elif unresolved_scope_or_case or medium_confidence:
    call_small_or_medium_validator_if_available
elif low_confidence or factual_claim or cross_language_conflict:
    call_gguf_as_teacher_validator
else:
    mark_needs_review
```

## 5. Canonicality rule

```text
GGUF verdict alone cannot make a card, relation, operator mapping, or translation canonical.
```

A canonical item requires at least:

- schema validity,
- card ontology validity,
- relation/invariant validation,
- diagnostic graph consistency,
- explicit status and audit trail,
- source/provenance or human review when factual.

## 6. Planned v2.2 implementation

The next implementation patch should add:

- `src/lingophysics/noema_index.py`
- `src/lingophysics/noema_router.py`
- `src/lingophysics/inference_gate.py`
- `src/lingophysics/energy_estimator.py`
- tests for routing decisions and audit output
