# 44. Energy-Aware Generation Pipeline

Status: Draft implementation layer, v2.2.

CIELingo reduces generation cost by avoiding unnecessary generation, not by
assuming that a dense model can magically inspect only a selected part of its
weights.

## Energy model

The initial estimator is intentionally simple. It uses relative units:

```text
cost ≈ model_multiplier × token_count × pass_count
```

Model multipliers are policy-level approximations:

```text
NO_LLM      0.00
SMALL_GGUF  1.00
MEDIUM_GGUF 3.00
LARGE_GGUF  8.00
```

These are not hardware measurements. They are planning values that allow the
router to compare alternatives and log expected savings.

## Expected saving sources

```text
1. Retrieval: choose only relevant cards/operators.
2. Context reduction: feed fewer tokens into any model call.
3. Gate selection: use smaller model levels where possible.
4. Validator-first: avoid generation when structural validation is enough.
5. Cache reuse: reuse resolved bundles and feature tensors.
6. Fallback clarity: record degradation rather than retrying blindly.
```

## Mature target

In a mature CIELingo loop, most routine queries should be handled by:

```text
NOEMA index + card graph + operator algebra + validator
```

GGUF should be invoked for:

```text
new or low-confidence structures
factual validation
hard synthesis
cross-language ambiguity
scope/case/TAM-E conflicts
human-review preparation
```

## Advisory rule

```text
GGUF verdict is advisory, not canonical.
```

Canonical status requires structural validation, graph consistency, audit, and
provenance/human review when the object carries factual or normative load.
