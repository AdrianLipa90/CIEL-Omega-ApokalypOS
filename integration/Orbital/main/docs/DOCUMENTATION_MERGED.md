# CIEL/Ω — Merged Documentation
### *Canonical Single-File Reference — CIEL-_SOT_Agent & Orbital Systems*
A. Lipa, S. Sakpal, M. Kamecka, U. Ahmad (2025). © 2025 Adrian Lipa / Intention Lab

Status: **canonical merged documentation** for the `CIEL-_SOT_Agent` repository and the embedded orbital runtime.

This file consolidates the following source documents:
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/OPERATIONS.md`
- `integration/Orbital/main/README.md`
- `integration/Orbital/main/docs/DOCUMENTATION_CANON.md`
- `integration/Orbital/main/docs/MECHANISM_SCOPE.md`
- `integration/Orbital/main/docs/FORMALISM_V0.md`
- `integration/Orbital/main/docs/RUNTIME_TARGETS_V0.md`
- `integration/Orbital/main/docs/MD_AUDIT_NOTES.md`
- `integration/Orbital/main/data/source/CIEL_OMEGA_COMPLETE_SYSTEM/README.md`
- `integration/Orbital/main/data/source/CIEL_OMEGA_COMPLETE_SYSTEM/MERGE_MANIFEST.md`
- `docs/integration/ORBital_INTEGRATION_ADDENDUM.md`
- `docs/integration/ORBITAL_INFRASTRUCTURE_RULES.md`
- `docs/integration/SAPIENS_SURFACE_BINDING.md`
- `docs/integration/MACHINE_AUTHORITY_SURFACE.md`
- `README_CANONICAL_V2.md`
- `CHANGELOG.md`

Conflict resolution rule: prefer canonical-tier files, newest audited status, implementation-backed claims over aspirational claims.

---

## Table of Contents

1. [System Identity and Ecosystem Role](#1-system-identity-and-ecosystem-role)
2. [Repository Architecture](#2-repository-architecture)
3. [Operational Flow](#3-operational-flow)
4. [Orbital System — Mechanism Layer](#4-orbital-system--mechanism-layer)
5. [Relational Mechanism Formalism v0](#5-relational-mechanism-formalism-v0)
6. [Runtime Targets v0](#6-runtime-targets-v0)
7. [CIEL_OMEGA_COMPLETE_SYSTEM — Embedded Runtime](#7-ciel_omega_complete_system--embedded-runtime)
8. [Orbital Integration Rules](#8-orbital-integration-rules)
9. [Sapiens Surface Binding](#9-sapiens-surface-binding)
10. [Machine Authority Surface](#10-machine-authority-surface)
11. [Documentation Canon and Audit Notes](#11-documentation-canon-and-audit-notes)
12. [Validation Layer](#12-validation-layer)
13. [Changelog](#13-changelog)
14. [Canonical Reading Order](#14-canonical-reading-order)

---

## 1. System Identity and Ecosystem Role

`CIEL-_SOT_Agent` is the **integration attractor** for the CIEL ecosystem.

It binds — but does not replace — the canonical theory repository, the Omega demo cockpit, Metatime, and the larger mechanism workspace. Integration is expressed through:

- repository identity and semantic phase,
- weighted coupling,
- Euler-style closure defect,
- orbital coherence diagnostics,
- bridge-state reduction,
- packet-aware human-model interaction,
- machine-readable indexing,
- multi-agent coordination on GitHub.

### Ecosystem roles

| Repository | Role |
|---|---|
| **canon / Seed of the Worlds** | Source of truth for axioms, definitions, derivations, manifests, and nonlocal repository hyperspace |
| **ciel-omega-demo** | Cockpit, UI surface, educational analogy layer, orbital preview, and legacy ergonomic reference |
| **Metatime** | Historical theory, phenomenology, and earlier simulation/archive layer |
| **CIEL-_SOT_Agent** | Integration kernel, synchronizer, compatibility harness, orbital bridge host, Sapiens interaction seed, and public operational attractor |

### Interpretive rule

The repository should be read through this direction:

```
orbital source architecture
  -> imported orbital runtime
  -> native bridge reduction
  -> relational-formal Sapiens surface
  -> packet / session / report artifacts
```

---

## 2. Repository Architecture

The repository is organized as a layered coupling structure. Higher layers must not silently replace lower ones.

### Subsystem 1 — Integration kernel

Models repositories as coupled phase-carrying identities and exposes:
- repository registry, coupling map, weighted Euler vector, closure defect, pairwise tension, machine-readable synchronization reports.

Primary anchors:
- `src/ciel_sot_agent/repo_phase.py`
- `src/ciel_sot_agent/synchronize.py`
- `integration/repository_registry.json`
- `integration/couplings.json`

### Subsystem 2 — GitHub coupling

Pulls current upstream heads, detects changes, propagates phase shifts, emits refreshed integration artifacts.

Primary anchors:
- `src/ciel_sot_agent/gh_coupling.py`
- `scripts/run_gh_repo_coupling.py`
- `integration/gh_upstreams.json`
- `integration/reports/live_gh_coupling_report.json`

### Subsystem 3 — Orbital runtime / diagnostic

Lives under `integration/Orbital/`. Imported-and-extended diagnostic runtime for relational orbital structure. Contains: sector/state models, orbital couplings, metrics, dynamics, geometry extraction, bootstrap helpers, read-only global diagnostic pass, orbital reports.

Primary anchors:
- `integration/Orbital/main/model.py`
- `integration/Orbital/main/registry.py`
- `integration/Orbital/main/metrics.py`
- `integration/Orbital/main/dynamics.py`
- `integration/Orbital/main/bootstrap.py`
- `integration/Orbital/main/global_pass.py`
- `scripts/run_orbital_global_pass.py`

### Subsystem 4 — Orbital bridge

Reduces orbital diagnostics into actionable integration state. Converts orbital runtime outputs into control, status, and support forms.

Emits: state manifest, health manifest, recommended control profile, bridge metrics, bridge reports.

Primary anchors:
- `src/ciel_sot_agent/orbital_bridge.py`
- `scripts/run_orbital_bridge.py`
- `integration/reports/orbital_bridge/`

### Subsystem 5 — Sapiens interaction and panel

Exposes two coupled surfaces: the packet-oriented client runtime and the panel foundation shell. Initializes Sapiens session state, derives interaction state from bridge/orbital state, builds model or panel payloads, and persists session artifacts.

Primary anchors:
- `src/ciel_sot_agent/sapiens_client.py`
- `src/ciel_sot_agent/sapiens_panel/`
- `scripts/run_sapiens_panel.py`
- `integration/reports/sapiens_client/`

### Subsystem 6 — GUI (Quiet Orbital Control)

Flask-based operator-facing web interface. Reads prepared state, manifests, and reports from backend layers. Exposes: main dashboard (coherence index, health, mode), JSON API endpoints for status/panel/GGUF, GGUF model manager.

Primary anchors:
- `src/ciel_sot_agent/gui/app.py`
- `src/ciel_sot_agent/gui/routes.py`
- `src/ciel_sot_agent/gguf_manager/manager.py`
- `docs/gui/CIEL_GUI_IDENTITY_BRIEF_AND_UX_PHILOSOPHY.md`

### Subsystem 7 — Documentation and registry manifold

Machine-readable and human-readable manifold describing how all layers relate.

Primary anchors:
- `docs/`
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`
- `integration/hyperspace_index_orbital.json`
- `integration/index_registry_orbital.yaml`

### Coupling structure

| Coupling level | Key observables |
|---|---|
| Repository-level | identity, phase, mass/weight, semantic relation type, GitHub-upstream change propagation |
| Orbital | orbital positions, phase relations, coherence weights, information mass, geometric distance, Berry-like phase terms, zeta-pole support structures |
| Bridge | state geometry, health interpretation, control recommendations, reportable integration outputs |
| Sapiens | relation, orbital state, bridge state, session identity, memory residue, model packet preparation |

### Main folders

| Folder | Contents |
|---|---|
| `docs/` | Human-readable architecture, hypotheses, analogies, operations, orbital addenda, shared plans |
| `integration/` | Machine-readable contracts, registries, mappings, couplings, reports, orbital integration layers |
| `integration/Orbital/` | Imported-and-extended orbital runtime, manifests, diagnostics, orbital report surface |
| `src/ciel_sot_agent/` | Executable integration code: synchronization, GitHub coupling, orbital bridge, Sapiens client, validators, panel logic, Flask GUI, GGUF model manager |
| `scripts/` | Thin operational launchers |
| `tests/` | Validation layer |

---

## 3. Operational Flow

The project is a sequence of reductions and bridges, not a monolithic executable.

```
relation
  -> orbital state
  -> bridge reduction
  -> session/packet
  -> report/memory residue
```

### Automation chain

```
.github/workflows/gh_repo_coupling.yml
  -> scripts/run_gh_repo_coupling.py
  -> src/ciel_sot_agent/gh_coupling.py
  -> integration/ (updated artifacts)
```

### Orbital execution chain

```
scripts/run_orbital_global_pass.py
  -> integration/Orbital/main/global_pass.py
  -> integration/Orbital/main/dynamics.py
  -> integration/Orbital/main/metrics.py
  -> integration/Orbital/main/reports/
```

### Operational launchers

- `scripts/run_gh_repo_coupling.py`
- `scripts/run_gh_repo_coupling_v2.py`
- `scripts/run_index_validator_v2.py`
- `scripts/run_orbital_global_pass.py`
- `scripts/run_orbital_bridge.py`
- `scripts/run_repo_phase_sync.py`
- `scripts/run_repo_sync_v2.py`
- `scripts/run_sapiens_panel.py`

Console entry points (via `pyproject.toml`): `ciel-sot-sapiens-client`, `ciel-sot-gui`.

### Report layers

| Layer | Path |
|---|---|
| Primary integration reports | `integration/reports/initial_sync_report.json`, `integration/reports/live_gh_coupling_report.json` |
| Orbital bridge reports | `integration/reports/orbital_bridge/` |
| Orbital runtime reports | `integration/Orbital/main/reports/` |
| Sapiens session reports | `integration/reports/sapiens_client/` |

---

## 4. Orbital System — Mechanism Layer

Status: **canonical mechanism and registry repo** for the embedded `CIEL_OMEGA_COMPLETE_SYSTEM` snapshot.

This layer is the **mechanism layer** — not the final physics closure and not a product-level orbital cockpit.

### Primary outputs

- `registries/runtime_files.csv`
- `registries/runtime_functions.csv`
- `registries/orchestrator_graph_edges.csv`
- `registries/formal_symbols.csv`
- `registries/symbol_to_runtime_map.csv`
- `registries/phase_couplings.csv`

### Out of scope at this stage

- Final derivations of `D_f`, `J(epsilon)`, or full metric closure
- Treating any single PDF as Source of Truth
- Presenting the embedded runtime as a fully integrated orbital product
- Claiming that the orbital subsystem already closes the runtime decision loop

### Working rule

1. inventory
2. map
3. graph
4. only then derive

### Current audit status

- Package import topology normalized
- Test suite passing
- CLI smoke run passing
- Orbital subsystem functional as a diagnostic engine
- Orbital subsystem **not yet proven** to be the active runtime control law

### Mechanism scope

Canonical runtime analyzed here: `CIEL_OMEGA_COMPLETE_SYSTEM` only.

Principles:
- only confirmed or explicitly candidate values,
- separate confirmed / candidate / unresolved,
- no demo code in canonical graph,
- no final physics closure in this stage.

---

## 5. Relational Mechanism Formalism v0

This layer tracks the mechanism layer only. The metric is left emergent.

### Core objects

| Symbol | Definition |
|---|---|
| Base state manifold | Local spherical / projective chart |
| `C_i` | Cycles |
| `gamma_i = ∮_Ci A` | Phase of a cycle |
| `Sigma_i = (tau_i, gamma_i, F_i)` | Local fingerprint |
| `W_ij` | Holonomic pair relation |
| `F_ij` | Pair correction / coupling result |
| `Delta_H = Σ_k exp(i gamma_k)` | Euler-Berry closure defect |
| `R_H = |Delta_H|²` | Holonomic defect norm |
| `V_rel = kappa_H R_H + V_I + V_D` | Relational potential |

### Minimal pipeline

```
relation -> orbital -> orchestration -> reduction -> memory
```

### Confirmed couplings

- `tau_i` couples to pair structure through `(tau_i, tau_j, gamma_i, gamma_j, W_ij) -> F_ij`
- `epsilon` couples to `D`
- `gamma_i` couples to `A`
- `W_ij` is induced by a connection along a path between cycles
- `Delta_H` is constructed from the phase family `{gamma_k}`
- `R_H` is induced by `Delta_H`
- `V_rel` is induced by `R_H`

### Not frozen here

- Final `D_f`
- Final `J(epsilon)`
- Final metric
- Final Kepler layer
- Final tetrahedral horizon dynamics

### Tetrahedral toy extension

A regular tetrahedral frame `T_4` may be embedded into the spherical base as a minimal nontrivial spatial scaffold. Tracked as a toy extension, not a frozen runtime law.

---

## 6. Runtime Targets v0

Conservative runtime target policy for current mechanism symbols.

### Classification rules

- `confirmed` — direct name/path/semantic match in runtime
- `candidate` — strong but not yet manually validated runtime landing zone
- `low confidence` — excluded from this registry; remain in raw hit tables only

### Primary registries

- `registries/runtime_symbol_targets.csv`
- `registries/runtime_symbol_function_targets.csv`
- `registries/runtime_file_symbol_hits.csv`

---

## 7. CIEL_OMEGA_COMPLETE_SYSTEM — Embedded Runtime

Canonical merged build of the CIEL/Ω runtime, memory sector, vocabulary layer, and Euler/EBA closure machinery.

### Axiomatic anchor

- `../../POSTULATES_CANON_PL_EN.md`
- `../CIEL_FOUNDATIONS/axioms/AX-0100-canonical-relational-phase-postulates.md`
- `../CIEL_FOUNDATIONS/derivations/D-0101-phase-components-from-aij-tau.md`

### What this build is

A merged Python system that combines:
- a **runtime/core layer** for phase-aware state evolution
- a **memory stack** (perceptual, working, semantic, procedural, affective, identity)
- a **vocabulary/ontology layer** with canonical symbols, aliases, and runtime bindings
- a **bridge** joining core, memory, vocabulary, and Euler/EBA closure metrics
- a **unified entrypoint** for simple end-to-end execution

Not a monolithic script — a modular package centered around `ciel_omega/`.

### Current health

| Check | Status |
|---|---|
| `UnifiedSystem.create()` | ✓ works |
| `run_text_cycle(...)` | ✓ works |
| CLI smoke path | ✓ works |
| `pytest -q` | ✓ passes (56 passed) |

### Package size

258 Python files inside `ciel_omega/` (244 excluding `TODO/`).

Largest subsystems by file count:

| Subsystem | Files |
|---|---|
| `memory/` | 36 |
| `core/` | 23 |
| `ext/` | 17 |
| `runtime/` | 11 |
| `emotion/` | 11 |
| `mathematics/` | 11 |
| `vocabulary/` | 10 |
| `ciel/` | 9 |
| `cognition/` | 8 |
| `fields/` | 7 |

### Top-level architecture

#### 1. Unified entrypoint — `ciel_omega/unified_system.py`

`UnifiedSystem` creates the orchestrator and phase bridge, runs one text-processing cycle, returns a compact result bundle: `core_metrics`, `vocabulary_metrics`, `euler_metrics`, memory metadata.

```python
from ciel_omega.unified_system import UnifiedSystem

system = UnifiedSystem.create(identity_phase=0.25)
out = system.run_text_cycle(
    "Euler-constraint integration test.",
    metadata={"salience": 0.8, "confidence": 0.76, "novelty": 0.61},
)
print(out["euler_metrics"])
```

#### 2. Core ↔ memory ↔ vocabulary bridge — `ciel_omega/bridge/memory_core_phase_bridge.py`

Instantiates core runtime, memory orchestrator, and vocabulary orchestrator. Synchronizes phase-like quantities between subsystems. Computes Euler/EBA closure reports. Applies active Euler feedback with rollback protection.

#### 3. Euler / EBA constraint system

Files: `ciel_omega/constraints/euler_constraint.py`

Computes sector-wise phase closure metrics for: memory, core, vocabulary/semantic, affect. Computes unified closure and pairwise phase tension. Optionally applies active correction only if the step improves closure.

Current role: diagnostics + guarded active regulator.

#### 4. Memory stack — `ciel_omega/memory/`

Major areas: perceptual, working, semantic, procedural, affective, identity memory. Also includes holonomy, braid invariants, potential, coupling, synchronization, and audit logging.

#### 5. Vocabulary and ontology

Files: `ciel_omega/vocabulary.yaml`, `ciel_omega/vocabulary/`, `ciel_omega/vocabulary_tools/`

Pipeline:
```
text -> extracted symbols -> canonical_id -> ontology record -> runtime binding
```

#### 6. Higher-level engine stack — `ciel_omega/ciel/`

High-level engine and backend integration. CLI entrypoint. Registry for language backends.

Key files: `ciel_omega/ciel/engine.py`, `ciel_omega/ciel/cli.py`, `ciel_omega/ciel/__main__.py`

#### 7. Additional subsystems

| Subsystem | Purpose |
|---|---|
| `emotion/` | Affective core and orchestration |
| `cognition/` | Perception, intuition, prediction, decision, introspection |
| `fields/` | Intention, sigma, soul invariant, unified sigma field |
| `resonance/` | Resonance operators and tensors |
| `symbolic/` | Glyph interpretation pipeline |
| `bio/` | EEG and Schumann-related helpers |
| `runtime/` | Backend adapter and controller |
| `visualization/` | Color/visual core |
| `compute/` | GPU-related helpers |

### Merge provenance

The merged artifact was assembled from three source tarballs:

1. `CIEL_OMEGA_FIXED_ALL_6_BABOL_PATCHED.tar.gz` — runtime/core base
2. `CIEL_CONSOLIDATED_v3.1.7_MEMORY_SECTOR_COMPLETE.clean.tar.gz` — full memory sector overlay
3. `VOCABULARY_COMPLETE_SYSTEM.tar.gz` — full vocabulary overlay

Merge rules:
- base tree extracted from FIXED_ALL_6
- memory sector overlaid from v3.1.7
- vocabulary package overlaid from VOCABULARY_COMPLETE_SYSTEM
- removed `__pycache__`, `.pyc`, `.pyo`, `.pytest_cache`
- added `ciel_omega/bridge/memory_core_phase_bridge.py`
- added `ciel_omega/unified_system.py`
- patched `ciel_omega/vocabulary/orchestrator.py` to use package-relative imports

### Key demos

```bash
# Unified Euler demo
python ciel_omega/demo_unified_euler.py

# Vocabulary resolution demo
python ciel_omega/demo_vocabulary_resolve.py
```

Additional demos: `demo_ciel_omega_complete.py`, `demo_full_pipeline.py`, `demo_memory_system.py`, `demo_holonomic_orchestrator.py`

### Known limitations

1. Warnings in the test suite — several tests return values instead of asserting
2. Mixed maturity across modules — some exploratory or legacy demo code remains
3. Runtime bindings may be partially deferred — not every symbol maps to a fully invoked execution path in every subsystem
4. In-package `ciel_omega/README.md` is outdated — this merged document is the accurate reference

---

## 8. Orbital Integration Rules

### What the orbital layer is

The orbital layer in `CIEL-_SOT_Agent` is:
- an imported orbital subsystem
- an integration-facing runtime snapshot
- a diagnostic layer
- a bridge-adjacent executable package
- **not yet** the full native engine of the repository

Primary paths: `integration/Orbital/`, `integration/Orbital/main/`

### Canonical local rules

1. Imported orbital files must remain marked as imported or integration-facing.
2. The orbital layer must stay explicitly separated from native SOT integration code.
3. Orbital diagnostic runners must not silently rewrite non-orbital registry layers.
4. Prefer read-only diagnostics and explicit manifests over hidden write-back.
5. If new orbital files are added, launchers and manifest notes must stay synchronized.
6. If the orbital layer is extended, the import manifest or its addendum must be updated.

### Architecture constraints

- Do not absorb orbital runtime into `src/` — even if `integration/Orbital/main/` is executable Python, its imported/runtime status is part of the repository's meaning.
- Keep orbital runtime and orbital bridge **distinct**: `integration/Orbital/main/` is the imported runtime; `src/ciel_sot_agent/orbital_bridge.py` is the native reduction layer.
- Preserve manifest-first interpretation through import manifests, explicit launcher paths, human-readable addenda, and report directories.
- Treat write-back as exceptional — any future orbital process writing into broader integration state must be explicit, documented, auditable, and distinguishable from read-only diagnostics.

---

## 9. Sapiens Surface Binding

### Dependency chain

```
src/ciel_sot_agent/orbital_bridge.py
  -> src/ciel_sot_agent/sapiens_client.py
```

The bridge computes: state manifest, health manifest, recommended control, bridge metrics.

The Sapiens client maps that bridge output into a `state_geometry` with:

| Field | Meaning |
|---|---|
| `surface` | Interaction mode and recommended action |
| `internal_cymatics` | Coherence index, closure penalty, system health |
| `spin` | Topological charge proxy from bridge metrics |
| `axis` | Truth |
| `attractor` | Orbital-holonomic-stability |

### Correct dependency direction

```
orbital source architecture
  -> imported orbital runtime
  -> native bridge reduction
  -> Sapiens surface protocol
  -> model packet / transcript / session state
```

### Key orbital observables flowing to Sapiens

- `R_H` — holonomic defect norm
- `closure_penalty`
- `Lambda_glob`
- Health-like stability observables
- Recommended control mode (through the bridge)

### Relational-formal protocol constraints

The Sapiens surface must enforce:
- truth over smoothing
- explicit uncertainty over false certainty
- explicit distinction between fact / inference / hypothesis / unknown
- minimal semantic distortion
- preservation of the user-intent axis

### Preferred spin: truth-seeking, not comfort-seeking

Bridge state may influence urgency or caution, but the contract fixes the preferred spin as truth-seeking. The attractor is minimal distortion under truthful, coherent response conditions — not mere pleasantness.

---

## 10. Machine Authority Surface

### Target canonical machine authority

| File | Role |
|---|---|
| `integration/indices/hyperspace_index_v2.json` | Target canonical machine index authority |
| `integration/registries/index_registry_v2.yaml` | Target canonical machine registry authority |

### Legacy compatibility mirrors

The following remain valid during transition but are **compatibility mirrors**, not preferred authorities:
- `integration/hyperspace_index.json`
- `integration/index_registry.yaml`

### Reading rule

```
target v2 authority
  -> fallback-aware runtime reader
  -> legacy mirror compatibility
```

Not the reverse.

### Dependency links

- `integration/MACHINE_AUTHORITY_V2.md` — declaration
- `docs/architecture/MACHINE_CANONICALIZATION_PLAN.md` — plan
- `docs/architecture/MACHINE_CANONICALIZATION_READINESS.md` — readiness report
- `docs/architecture/LEGACY_MACHINE_MIRROR_POLICY.md` — mirror policy

---

## 11. Documentation Canon and Audit Notes

### Canonical document hierarchy

#### Repo-level canon
1. `README.md` — repository purpose and scope
2. `docs/MECHANISM_SCOPE.md` — what this repo is and is not
3. `docs/FORMALISM_V0.md` — current mechanism-layer formal objects
4. `docs/RUNTIME_TARGETS_V0.md` — conservative runtime target policy
5. `docs/MD_AUDIT_NOTES.md` — markdown audit notes, drift, and update log

#### Embedded runtime canon
6. `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/README.md` — build-level structure and verified behavior
7. `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/README.md` — high-level package overview (not final source of truth for implementation status)
8. `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/README.md` — orbital subsystem scope

#### Historical / non-canonical (useful but not authoritative)
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/README_old.md` — historical architecture snapshot
- Audit reports in `docs/` — point-in-time reports, not standing canon
- Generated vocabulary summaries — derived artifacts, not normative spec
- Manual upload markdown files under `references/manual_uploads/` — reference material only

### Conflict resolution rule

If two markdown files disagree:
- prefer the file listed above as canonical
- prefer the newest audited status over older marketing language
- prefer implementation-backed claims over aspirational claims

### Audit findings

#### Canon drift
Several markdown files describe the same system from different phases. Main risk: future/aspirational architecture stated as if already implemented, or old marketing language treated as runtime fact.

#### Implementation drift
The embedded runtime is healthy and testable, but some markdown files overstated current integration status. Most important example: the orbital subsystem is functional as a diagnostic engine but is not yet documented as fully closing the runtime decision loop.

### Current documentation posture

| Status | Items |
|---|---|
| **Confirmed** | Repository mechanism scope; current testable state of embedded runtime; orbital subsystem exists and runs as diagnostics; package imports and CLI smoke path healthy |
| **Partial** | Active coupling of orbital metrics into runtime decision policy; full end-to-end autonomy layer; product-level cockpit / native control interface |
| **Not yet proven** | Final metric closure; final `D_f`; final `J(epsilon)`; complete productization of the orbital architecture |

### Documentation rule for future edits

When editing or extending docs, preserve the distinction:
- **implemented**
- **partially implemented**
- **planned / conceptual**

---

## 12. Validation Layer

Representative test anchors:

| Test file | Covers |
|---|---|
| `tests/test_repo_phase.py` | Repository phase synchronization |
| `tests/test_gh_coupling.py` | GitHub coupling |
| `tests/test_gh_coupling_v2.py` | GitHub coupling v2 |
| `tests/test_index_validator.py` | Index validation |
| `tests/test_index_validator_v2.py` | Index validation v2 |
| `tests/test_orbital_runtime.py` | Orbital runtime |
| `tests/test_sapiens_client_packet.py` | Sapiens client packet |
| `tests/test_sapiens_panel.py` | Sapiens panel |
| `tests/test_gui.py` | Flask GUI routes and API |
| `tests/test_gguf_manager.py` | GGUF model manager |

Run:

```bash
python -m pytest tests/
```

CI additionally runs:

```bash
python -m ruff check src/ciel_sot_agent
```

---

## 13. Changelog

### [0.1.0] — 2026-04-01

**Added**
- Root `pyproject.toml` making the repository installable via `pip install -e .`
- CLI entry points for synchronization, GitHub coupling, validators, orbital bridge, and Sapiens client
- CI workflow for pull requests and pushes to `main` (install, lint, test gates)
- `ruff` and `mypy` baseline configuration for the canonical package
- Production readiness protocol and release gate contract

**Changed**
- Declared runtime dependency on `PyYAML`
- Clarified repository status distinguishing tested logic from production release readiness

---

## 14. Canonical Reading Order

For a first reading of the full system, inspect in this order:

1. This document (`DOCUMENTATION_MERGED.md`) — consolidated reference
2. `README.md` — repository identity and role
3. `integration/Orbital/main/README.md` — orbital mechanism scope
4. `integration/Orbital/main/docs/MECHANISM_SCOPE.md` — scope boundary
5. `integration/Orbital/main/docs/FORMALISM_V0.md` — formal objects
6. `integration/Orbital/main/docs/MD_AUDIT_NOTES.md` — current audit state
7. `integration/Orbital/main/data/source/CIEL_OMEGA_COMPLETE_SYSTEM/README.md` — embedded runtime
8. Subsystem READMEs as needed

For implementation inspection, inspect source files in this order:

1. `ciel_omega/unified_system.py`
2. `ciel_omega/bridge/memory_core_phase_bridge.py`
3. `ciel_omega/constraints/euler_constraint.py`
4. `ciel_omega/vocabulary.yaml`
5. `ciel_omega/vocabulary_tools/resolver.py`
6. `ciel_omega/vocabulary_tools/symbol_extractor.py`
7. `ciel_omega/memory/` (orchestrators and memory types)
8. `ciel_omega/ciel/engine.py`
