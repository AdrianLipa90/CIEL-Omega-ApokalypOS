# Braid architecture exploration

## Repo scan summary
- Total files: 1331
- Python files: 568
- Braid-named files: 25

## Active architecture axis
- Entry runtime: `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/main.py`
- Human-facing control: `ciel_orchestrator.py` -> `ciel/engine.py`
- Monolith memory persistence: `memory/monolith/unified_memory.py`
- Nonlocal memory / M0-M8: `memory/orchestrator.py`
- Physics/memory bridge: `bridge/memory_core_phase_bridge.py`
- Explicit braid kernel: `core/braid/*`

## What was already present
- `core/braid/*` already implemented loops, scars, scheduler, glyphs, runtime.
- `memory/braid_invariant.py` already implemented M7 long-timescale braid memory.
- `memory/monolith/unified_memory.py` already captured braid traces into durable ledger.

## What was missing or only half-wired
- No explicit scar severity/classification surfaced in braid outputs.
- Loop execution had no exposed budget control path in adapter/runtime.
- Bridge could silently fall back to mini runtime, splitting braid visibility.
- Braid summary was not propagated consistently to cycle/runtime surfaces.

## What was added in this pass
- Scar classification + severity in `core/braid/scars.py`
- Budget-aware batching in `core/braid/scheduler.py`
- Prompt/domain/budget encoding in `core/braid/adapter.py`
- Budget-aware loop execution metadata in `core/braid/runtime.py`
- Braid summary propagation in `memory/orchestrator.py`
- Braid summary exposed by `bridge/memory_core_phase_bridge.py`
- Braid summary exposed by `unified_system.py` and `ciel/engine.py`
- Focused regression test in `tests/test_braid_system_runtime.py`

## Current interpretation
The braid system is not a new foreign subsystem. It is now a more explicit transverse layer crossing:
1. symbolic loop execution (`core/braid`),
2. deep memory M7 (`memory/braid_invariant.py`),
3. durable bifurcation ledger (`memory/monolith/unified_memory.py`),
4. runtime bridge / orchestration surfaces.

## Pass 3 — Domain Profiles, Cards, and Orbital Diagnostics

- Added per-domain coupling profiles for `orbital`, `memory`, `ethics`, `dialogue`, `research`, and `generic`.
- Added explicit `braid ↔ nonlocal` operational cards with card IDs, roles, and activation weights.
- Added adaptive reweighting from scar taxonomy and drift class.
- Added orbital diagnostics consumption of braid weights, including status, mode, alerts, and top card IDs.
