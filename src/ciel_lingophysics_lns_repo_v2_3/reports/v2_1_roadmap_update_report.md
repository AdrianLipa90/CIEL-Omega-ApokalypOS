# v2.1 Roadmap and Learning Policy Patch Report

## Summary

This patch updates the repository-level plan. The previous roadmap was an early v0.7 plan and no longer matched the current v2.0 repository state. This patch replaces it with a staged v2.1 roadmap and adds explicit NOEMA-first and GGUF teacher-validator policies.

## Added / updated

- Updated `docs/11_IMPLEMENTATION_ROADMAP.md`
- Added `docs/41_NOEMA_GGUF_TEACHER_VALIDATOR_ROADMAP.md`
- Added `data/roadmap/cielingo_stage_plan_v2_1.{json,yaml,csv}`
- Added `data/roadmap/gguf_teacher_validator_policy_v2_1.{json,yaml}`
- Added `data/roadmap/noema_inference_gate_policy_v2_1.{json,yaml}`
- Added `schemas/ciel_lns_roadmap.schema.json`
- Added `src/lingophysics/roadmap.py`
- Added `tests/test_roadmap.py`

## Key policy changes

1. NOEMA retrieval and local validation come before GGUF/LLM calls.
2. GGUF/LLM verdicts are advisory teacher-validator signals, not canonical truth.
3. Repository language should remain technical and auditable.
4. Batch size decreases as dependency density grows.
5. The next recommended implementation patch is `v2.2 NOEMA Retrieval and Inference Gate`.

## Status

- Data status: planning metadata only, no external dictionary import.
- Blockers: none.
- Expected test count after this patch: previous tests + roadmap tests.
