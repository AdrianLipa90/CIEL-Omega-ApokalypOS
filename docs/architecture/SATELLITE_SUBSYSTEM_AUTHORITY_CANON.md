# Satellite Subsystem Authority Canon

## Status
This document establishes explicit authority rules for satellite subsystems beyond the Omega root.

## Central rule
A satellite subsystem may express, export, transport, or preserve canonical meaning, but it must not silently replace the canonical runtime source of truth.

## Authority matrix

### SAT-NOEMA-0001 — NOEMA ⇄ SOT ⇄ SapiensOrbital
- **class:** `satellite_export_surface`
- **active_status:** `ACTIVE_EXPORT_SURFACE`
- **role:** Canonical DSL/spec/export bridge for projected meaning from the canonical orbital/nonlocal state.
- **input_from:** `canonical orbital/nonlocal registry`
- **output_to:** `registry_export.noema + contract concordance`
- **authority_rule:** SOT runtime and registries remain canonical; NOEMA is export/spec surface only.
- **may:**
  - export projected meaning from canonical registry state
  - carry human-auditable specification and concordance artifacts
  - serve as downstream DSL/spec surface for audited projection
- **must_not:**
  - override SOT runtime or registry source of truth
  - introduce independent orbital logic outside canonical bridge/reduction flow
  - be treated as upstream donor of runtime state

### SAT-SAPIENS-0001 — Sapiens Integration Layer
- **class:** `satellite_interaction_surface`
- **active_status:** `ACTIVE_SURFACE_AND_REPORT_LAYER`
- **role:** Human-model shell/controller above bridge/orbital/session/settings state.
- **input_from:** `orbital_bridge reduction outputs`
- **output_to:** `packet/session/transcript/panel state`
- **authority_rule:** Must not become second source of truth for orbital or bridge logic.
- **may:**
  - express bridge-reduced state as packet/session/transcript/panel surfaces
  - manage human-facing controller and settings state
  - host shell logic above bridge/orbital outputs
- **must_not:**
  - become a second source of truth for orbital logic
  - recompute bridge state independently of the canonical reduction path
  - override canonical runtime identities or couplings

### SAT-AUDIO-0001 — Audio Orbital Stack
- **class:** `satellite_io_stack`
- **active_status:** `ACTIVE_OPTIONAL_IMPORT_STACK`
- **role:** Local speech skeleton around Omega and Orbital.
- **input_from:** `audio/VAD/STT`
- **output_to:** `sapiens packet -> omega/orbital -> response -> TTS`
- **authority_rule:** Kept auditable and optional; heavy models remain external until configured.
- **may:**
  - provide optional local audio I/O around Omega and Orbital
  - normalize audio into packet-facing forms
  - remain auditable as a peripheral stack
- **must_not:**
  - override canonical Omega runtime semantics
  - silently import heavy models as mandatory runtime requirements
  - be treated as core source of truth rather than optional I/O

### SAT-RELMECH-0001 — Relational Mechanism Import Bundle
- **class:** `satellite_reference_import`
- **active_status:** `ACTIVE_REFERENCE_IMPORT`
- **role:** Text-first preserved mechanism spine import for reviewable closure/holonomy/reduction-memory logic.
- **input_from:** `consolidated mechanism analysis`
- **output_to:** `reviewable registries and mechanism notes`
- **authority_rule:** Preserve and reference; do not split into ad hoc partial packs.
- **may:**
  - preserve and expose mechanism spine for review
  - support refactor and interpretation of pairwise/closure/holonomy/reduction-memory logic
  - serve as reference import tied to the active canon
- **must_not:**
  - replace active runtime canon without explicit migration
  - be split into ad hoc partial packs that lose mechanism continuity
  - masquerade as current executable source of truth

## Order of authority
1. Omega active runtime and canonical registries
2. Orbital and bridge reduction outputs
3. Satellite interaction/export/I/O/reference surfaces
4. Historical or derived exports

## Consequence
If a satellite subsystem conflicts with the canonical Omega runtime, the Omega runtime wins until an explicit migration is performed.
