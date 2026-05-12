# CIELingo Implementation Roadmap v2.1

Status: draft canonical roadmap.  
Scope: general repository plan, model-development stages, NOEMA-first routing, and GGUF teacher-validator policy.

## 1. Repository direction

CIELingo is not an ordinary dictionary project. It is a typed linguistic-physics system built from concept cards, operator cards, grammar gauges, event frames, diagnostics, and validator loops.

Core rule:

```text
Library = Concepts + Operators + Relations + Grammar + Diagnostics + Learning Policy
```

Technical style rule:

```text
Repo artifacts must use technical language: schema, algorithm, status, validator, graph, tensor, fallback, audit.
No metaphysical or poetic claims should be introduced as technical assertions.
```

## 2. Current baseline

The current implemented local baseline is `v2.0 Diagnostic Geometry Layer`:

- 72 concept cards across 5 languages: PL, EN, DE, FR, ES.
- operator cards and operator algebra.
- case gauge, dynamic deixis, event frames, ontological aspect, TAM-E, scope/quantifier/negation.
- transformer interface skeleton with feature tensors, attention bias, auxiliary tasks, and validator loop.
- diagnostic geometry: cross-language reconstruction costs, operator density, relation matrices, conflict/unresolved registry.

This roadmap supersedes the old v0.7 roadmap that focused mainly on concept expansion.

## 3. Stage plan

### P0 — Foundation complete, v0.6-v2.0

Goal: establish the formalism, typed card layers, first concept batches, operator algebra, diagnostics, and transformer interface skeleton.

Exit condition: local tests pass, diagnostic registry has no blockers, fallback manifests exist.

### P1 — Roadmap and governance correction, v2.1

Goal: define the staged plan and add the NOEMA-first / GGUF teacher-validator policy.

Deliverables:

- updated `docs/11_IMPLEMENTATION_ROADMAP.md`
- `docs/41_NOEMA_GGUF_TEACHER_VALIDATOR_ROADMAP.md`
- `data/roadmap/cielingo_stage_plan_v2_1.{json,yaml,csv}`
- `data/roadmap/gguf_teacher_validator_policy_v2_1.{json,yaml}`
- `data/roadmap/noema_inference_gate_policy_v2_1.{json,yaml}`
- roadmap schema, module and tests

### P2 — NOEMA Retrieval and Inference Gate, v2.2

Goal: route a prompt to the smallest sufficient subgraph and avoid model calls when structural validation is enough.

The gate must select between:

```text
no_model
small_model_or_adapter
gguf_teacher_validator
human_review
```

### P3 — GGUF Teacher-Validator Learning Loop, v2.3

Goal: use GGUF/LLM as an advisory validator during learning and hard-case review, not as the canonical source of truth.

Rule:

```text
GGUF verdict is advisory. Canonical status requires structural validation and, where relevant, provenance/human review.
```

### P4 — CIELingo Validator Hardening, v2.4

Goal: promote validators from file-level checks to semantic quality gates.

Validator must catch false equivalences involving:

- scope: `not every` vs `none`
- case roles: `pies gryzie kota` vs `kota gryzie pies`
- operator duals: `Inside(x,y)` vs `Contains(y,x)`
- ontology: `ser` vs `estar`, `koto` vs `mono`
- unresolved deictic anchors

### P5 — Batch03 Controlled Expansion, v2.5

Goal: add 20 concept cards × 5 languages using strengthened diagnostics.

Batch size now decreases because dependency density increases.

### P6 — Transformer Adapter Experiments, v2.6-v2.8

Goal: test CIEL feature tensors as auxiliary signals, attention bias, adapter features, or constrained-validator outputs.

Success requires measurable improvement on selected invariant tests or a clear negative result.

### P7 — Benchmark and Public Draft, v3.0

Goal: produce a technical draft, reproducibility pack, benchmark suite, and demo workflow that can be reviewed outside this conversation.

## 4. Batch-size policy

```text
0–100 concept cards      batch 36
100–200 concept cards    batch 20
200–400 concept cards    batch 15
400+ concept cards       batch 10 or curated patches only
```

Reason: each new card increases relation-checking cost against the existing graph.

## 5. GGUF / LLM role

GGUF should not dominate the system. It should validate and teach during uncertain cases.

```text
CIELingo accumulates structure.
NOEMA routes retrieval.
Validators enforce invariants.
GGUF provides advisory teacher-validator verdicts.
```

The mature direction is to reduce dependence on GGUF as local confidence grows.

## 6. NOEMA-first inference rule

```text
Input
→ NOEMA retrieval
→ local card/operator/event-frame subgraph
→ CIEL feature tensor
→ local validator
→ confidence policy
→ optional GGUF teacher-validator
→ verdict fusion
→ audit/fallback
```

A large model should not be called when the local graph and validators are sufficient.

## 7. Risk register

| Risk | Mitigation |
|---|---|
| Semantic dependency explosion | Decrease batch size, maintain relation deltas and unresolved registry. |
| GGUF over-trust | Keep GGUF verdict advisory, never canonical alone. |
| Manual seed treated as dictionary authority | Keep `curated_seed`, `draft`, `needs_review`, `unknown` statuses. |
| Cross-language flattening | Use case gauge, TAM-E, scope, event frames, ontological aspect and reconstruction costs. |
| Storage failure | Use JSON/JSONL fallback with explicit report. |
| Metaphorical language polluting claims | Keep repository documentation technical and auditable. |

## 8. Immediate next version

Recommended next implementation patch: `v2.2 NOEMA Retrieval and Inference Gate`.

It should add:

- NOEMA index schema
- routing policy
- inference gate policy
- confidence thresholds
- energy/cost estimator skeleton
- tests for no-model vs GGUF-validator routing
