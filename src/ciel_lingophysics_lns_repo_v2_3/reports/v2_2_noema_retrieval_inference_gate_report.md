# v2.2 NOEMA Retrieval and Inference Gate Patch Report

Status: completed local patch  
Generated: 2026-05-10T14:16:15.342618+00:00

## Summary

v2.2 introduces the first executable NOEMA routing layer for CIELingo. It adds
an index schema, a seed index, routing policy, inference gate policy, router
modules, a relative energy estimator, and tests.

## Key rules

- NOEMA routes first.
- CIELingo validates structurally.
- GGUF verdict is advisory, not canonical.
- Dense GGUF partial execution is not claimed.
- Unresolved high-impact issues route to human review.

## Added modules

```text
src/lingophysics/noema_index.py
src/lingophysics/noema_router.py
src/lingophysics/inference_gate.py
src/lingophysics/energy_estimator.py
```

## Added test files

```text
tests/test_noema_router.py
tests/test_inference_gate.py
```

## Next recommended patch

v2.3 GGUF Teacher-Validator Learning Loop.

## Local test adjustment

Inflected Polish glass forms (`szklance`, `szklankę`, `szklanki`) are included in the seed labels so routing can retrieve the container concept from `Woda jest w szklance`.
