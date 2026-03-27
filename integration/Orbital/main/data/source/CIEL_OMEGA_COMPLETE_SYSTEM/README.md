# CIEL OMEGA COMPLETE SYSTEM

Canonical merged build of the CIEL/Ω runtime, memory sector, vocabulary layer, and Euler/EBA closure machinery.

This README describes the **actual structure and current audited behavior** of the packaged system at `/CIEL_OMEGA_COMPLETE_SYSTEM`, based on direct inspection and runtime tests of this workspace.



Status note:
- this file is treated as the build-level reference for the embedded runtime in this workspace,
- but claims below should still be read in light of the audit reports under `docs/`.

## Axiomatic anchor
The runtime-facing orbital and closure machinery is globally anchored to:
- `../../POSTULATES_CANON_PL_EN.md`
- `../CIEL_FOUNDATIONS/axioms/AX-0100-canonical-relational-phase-postulates.md`
- `../CIEL_FOUNDATIONS/derivations/D-0101-phase-components-from-aij-tau.md`

These files define the current repo-level postulate canon, the local foundations bridge, and the closest derivation note linking transport, tau modes, phase closure, and holonomic residuals.

## What this build is

This artifact is a merged Python system that combines:

- a **runtime/core layer** for phase-aware state evolution
- a **memory stack** with perceptual, working, semantic, procedural, affective, and identity memory
- a **vocabulary/ontology layer** with canonical symbols, aliases, and runtime bindings
- a **bridge** that joins core, memory, vocabulary, and Euler/EBA closure metrics
- a **unified entrypoint** for simple end-to-end execution

It is not a single monolithic script. It is a modular package centered around `ciel_omega/` with demos, tests, and support files.

## Current health of the build

Verified on this audited workspace:

- `UnifiedSystem.create()` works
- `run_text_cycle(...)` works
- CLI smoke path works
- `pytest -q` passes

Current audit result in this workspace:

- **56 passed**
- CLI smoke run passes
- import topology normalized

Important limitation:
- the optional Hugging Face backend path still requires the external `transformers` dependency and is not treated here as a blocking failure of the core runtime.

## Package size and structure

Inside `ciel_omega/` there are currently **258 Python files** including `TODO/`, or **244 Python files** when `TODO/` is excluded.

Largest subsystems by file count:

- `memory/` — 36
- `core/` — 23
- `ext/` — 17
- `runtime/` — 11
- `emotion/` — 11
- `mathematics/` — 11
- `vocabulary/` — 10
- `ciel/` — 9
- `cognition/` — 8
- `fields/` — 7

## Top-level architecture

### 1. Unified entrypoint

File:

- `ciel_omega/unified_system.py`

Main object:

- `UnifiedSystem`

Purpose:

- creates the orchestrator and the phase bridge
- runs one text-processing cycle
- returns a compact result bundle:
  - `core_metrics`
  - `vocabulary_metrics`
  - `euler_metrics`
  - memory metadata

Minimal usage:

```python
from ciel_omega.unified_system import UnifiedSystem

system = UnifiedSystem.create(identity_phase=0.25)
out = system.run_text_cycle(
    "Euler-constraint integration test.",
    metadata={"salience": 0.8, "confidence": 0.76, "novelty": 0.61},
)
print(out["euler_metrics"])
```

### 2. Core ↔ memory ↔ vocabulary bridge

File:

- `ciel_omega/bridge/memory_core_phase_bridge.py`

Purpose:

- instantiates the core runtime, memory orchestrator, and vocabulary orchestrator
- synchronizes phase-like quantities between subsystems
- computes Euler/EBA closure reports
- applies active Euler feedback with rollback protection
- uses vocabulary extraction/resolution to feed semantic symbols into the closure stack

This is the main integration layer of the build.

### 3. Euler / EBA constraint system

Files:

- `ciel_omega/constraints/euler_constraint.py`
- `ciel_omega/constraints/__init__.py`

Purpose:

- compute sector-wise phase closure metrics for:
  - memory
  - core
  - vocabulary / semantic
  - affect
- compute unified closure and pairwise phase tension
- optionally apply active correction only if the step improves closure

Current role:

- diagnostics + guarded active regulator

### 4. Memory stack

Directory:

- `ciel_omega/memory/`

Major areas:

- perceptual memory
- working memory
- semantic memory
- procedural memory
- affective memory
- identity memory
- holonomy, braid invariants, potential, coupling, synchronization, and audit logging

This is the densest subsystem in the repository.

### 5. Vocabulary and ontology

Files/directories:

- `ciel_omega/vocabulary.yaml`
- `ciel_omega/vocabulary/`
- `ciel_omega/vocabulary_tools/`

Purpose:

- provide canonical symbol records
- provide aliases and ontology classes
- map surface symbols to `canonical_id`
- expose runtime bindings for ontology records

Important runtime tools:

- `vocabulary_tools/resolver.py`
- `vocabulary_tools/symbol_extractor.py`

Pipeline:

```text
text -> extracted symbols -> canonical_id -> ontology record -> runtime binding
```

### 6. Higher-level engine stack

Directory:

- `ciel_omega/ciel/`

Purpose:

- high-level engine and backend integration
- CLI entrypoint
- registry for language backends

Related orchestration files:

- `ciel_omega/ciel/engine.py`
- `ciel_omega/ciel/cli.py`
- `ciel_omega/ciel/__main__.py`

### 7. Additional subsystems

- `emotion/` — affective core and orchestration
- `cognition/` — perception, intuition, prediction, decision, introspection
- `fields/` — intention, sigma, soul invariant, unified sigma field
- `resonance/` — resonance operators and tensors
- `symbolic/` — glyph interpretation pipeline
- `bio/` — EEG and Schumann-related helpers
- `runtime/` — backend adapter and controller
- `visualization/` — color/visual core
- `compute/` — GPU-related helpers

## Key demos

### Unified Euler demo

```bash
python ciel_omega/demo_unified_euler.py
```

What it does:

- runs a `UnifiedSystem` cycle
- prints the Euler/EBA metric report as JSON

### Vocabulary resolution demo

```bash
python ciel_omega/demo_vocabulary_resolve.py
```

What it does:

- loads `vocabulary.yaml`
- extracts symbols from text
- resolves them to canonical ontology records and runtime bindings

### Legacy / broader demos

Examples:

- `demo_ciel_omega_complete.py`
- `demo_full_pipeline.py`
- `demo_memory_system.py`
- `demo_holonomic_orchestrator.py`

These remain useful as exploratory demos, but the canonical merged build is best understood through `UnifiedSystem`, the bridge, and the constraint/vocabulary pipeline.

## Testing

Run from inside `ciel_omega/`:

```bash
pytest -q
```

Current result on this build:

```text
58 passed, 46 warnings
```

## Known limitations

1. **Warnings in the test suite**
   Several tests return values instead of asserting. They pass, but the suite should be cleaned up.

2. **Mixed maturity level across modules**
   Some modules are production-like runtime components, while others are exploratory or legacy demos.

3. **Runtime bindings may be partially deferred**
   The ontology layer resolves symbols and provides bindings, but not every symbol is guaranteed to map to a fully invoked execution path in every subsystem.

4. **Existing package README inside `ciel_omega/` is outdated**
   The in-package `ciel_omega/README.md` still describes an older framing of the system. This top-level README is the more accurate description of the merged canonical build.

## Recommended way to read the system

If you want to understand the current architecture, inspect files in this order:

1. `ciel_omega/unified_system.py`
2. `ciel_omega/bridge/memory_core_phase_bridge.py`
3. `ciel_omega/constraints/euler_constraint.py`
4. `ciel_omega/vocabulary.yaml`
5. `ciel_omega/vocabulary_tools/resolver.py`
6. `ciel_omega/vocabulary_tools/symbol_extractor.py`
7. `ciel_omega/memory/` (orchestrators and memory types)
8. `ciel_omega/ciel/engine.py`

## Build provenance

See:

- `CANONICAL_BUILD_MANIFEST.md`
- `MERGE_MANIFEST.md`

These describe how the canonical merged artifact was assembled.

## Short summary

This build is best understood as a **merged experimental runtime** for:

- phase-aware core dynamics
- multi-sector memory
- ontology/vocabulary resolution
- Euler/EBA closure diagnostics and guarded feedback

It is structurally coherent, importable, testable, and currently passes its packaged test suite.
