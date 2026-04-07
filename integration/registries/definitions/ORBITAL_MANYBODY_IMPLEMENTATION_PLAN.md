# Hierarchical Orbital Many-Body Implementation Plan v0.2

## Objective
Refactor the orbital card system so each object card and each subsystem card carries enough structure to represent:
- limited information regime,
- subsystem horizon / event-horizon style boundary,
- holonomic leakage policy,
- many-body synchronization role,
- local versus orbit versus system `tau`,
- bridge / broker / Lagrange-style transfer roles,
- **systemic privacy** between internal subsystem knowledge and exportable subsystem knowledge.

The implementation must avoid semantic shortcuts: every new field added to the card system must have a deterministic derivation rule, persistence path, and audit trail.

---

## New architectural law

### Systemic Privacy Law
Each subsystem must preserve an internal knowledge layer that is **not** directly exported outside its horizon.
Only a horizon-projected external layer may leave the subsystem.

Formally:
- `K_i^int` = internal knowledge / internal cards / unresolved local superposition
- `K_i^ext` = external/exportable knowledge
- `Π_H` = horizon projection operator

Required relation:

`K_i^ext = Π_H(K_i^int)`

This means:
- internal cards may contain richer local state,
- external cards must expose only normalized results / summaries / leak-compatible projections,
- subsystem privacy is not optional metadata; it is part of the architecture.

---

## Problem ⇄ Solution Ledger

### P1. Flat semantic cards are insufficient
**Problem:** current cards only carry `orbital_role`, `orbital_confidence`, and `semantic_role`.

**Solution:** extend cards to `orbital object card v0.2` with explicit hierarchy and information-boundary fields.

### P2. No explicit hierarchy between object and enclosing subsystem
**Problem:** functions, classes, methods, and constants are not linked to a deterministic container card.

**Solution:** derive `container_card_id` from the file card and reuse it as the first local subsystem boundary.

### P3. No explicit horizon/boundary formalism
**Problem:** cards cannot express where direct visibility ends and where only leakage is allowed.

**Solution:** derive `horizon_id`, `horizon_class`, `information_regime`, `visible_scopes`, and `leak_policy` for each card.

### P4. No storage layer for many-body metadata
**Problem:** the database library stores only the older, thinner card schema.

**Solution:** extend `records.sqlite` schema and manifest summaries to persist the new fields and counts.

### P5. No implementation roadmap recorded in-repo
**Problem:** system intent lives only in conversation and risks drift.

**Solution:** keep an explicit implementation-plan document and TODO ledger inside the definitions/card sector.

### P6. No explicit systemic privacy for subsystems
**Problem:** subsystem-local reasoning risks being flattened into globally visible card state.

**Solution:** introduce separate internal/private and external/export layers for subsystem cards, connected by an explicit horizon projection rule.

### P7. No dedicated private card layer for subsystem-only work
**Problem:** local half-conclusions, internal traces, and unresolved internal candidate states have no reserved representation.

**Solution:** define `internal subsystem cards` as non-export cards used only inside a subsystem, and define export cards as horizon-projected outputs.

---

## Phase Map

### Phase 0 — Alignment and constraints
- Freeze current `main` head.
- Record implementation plan and TODOs.
- Identify the current resolver and DB persistence boundaries.

### Phase 1 — Card schema v0.2 ✅
- Extend orbital resolver outputs with:
  - `card_schema`
  - `container_card_id`
  - `manybody_role`
  - `subsystem_kind`
  - `parent_orbital_role`
  - `horizon_id`
  - `horizon_class`
  - `information_regime`
  - `visible_scopes`
  - `leak_policy`
  - `tau_role`
  - `lagrange_roles`
- Extend `orbital_assignment_report.json` with counts for the new fields.
- Extend DB library schema and manifest for persistence.

### Phase 2 — Systemic privacy and internal cards
- Formalize internal vs export card layers.
- Define subsystem-private card schema (`internal_card_schema`).
- Define horizon projection operator semantics (`Π_H`).
- Define which fields are exportable, which are internal-only, and which are leak-derived.
- Add deterministic `export_result` / `export_confidence` / `residual_uncertainty` placeholders.

### Phase 3 — Horizon semantics and leakage rules
- Formalize horizon classes and allowed visibility transitions.
- Encode the first deterministic leak-policy table.
- Make `lagrange_roles` explicit for bridge / broker / transfer-node objects.
- Attach privacy constraints to horizon class semantics.

### Phase 4 — Local synchronization scaffolding
- Add explicit local synchronization metadata:
  - `tau_local`
  - `tau_orbit`
  - `tau_system` hooks or derivation slots
- Define the first subsystem/board aggregation rules.
- Define how private subsystem state condenses into exportable half-conclusions.

### Phase 5 — Runtime integration
- Feed card-derived horizon and regime metadata into orbital runtime / bridge layers.
- Feed systemic privacy constraints into export/reporting boundaries.
- Ensure downstream reports can consume the richer card schema.

### Phase 6 — Audit and tests
- Add regression tests for:
  - recursion guard,
  - stable IDs,
  - deterministic container/horizon derivation,
  - persistence of the v0.2 fields,
  - internal-vs-export card isolation,
  - horizon projection correctness.

---

## Internal / external card design target

### Public / export card layer
Must carry only subsystem-exportable state, for example:
- `export_state`
- `export_result`
- `export_confidence`
- `residual_uncertainty`
- `information_regime`
- `leak_policy`
- `visible_scopes`
- `horizon_class`
- `tau_role`
- `manybody_role`

### Internal subsystem card layer
Must remain private to the subsystem, for example:
- `internal_card_id`
- `internal_candidate_states`
- `internal_conflict_state`
- `internal_superposition_state`
- `internal_resolution_trace`
- `internal_tau_local`
- `internal_memory_mode`
- `internal_visibility = PRIVATE_SUBSYSTEM_ONLY`

---

## Acceptance criteria for Phase 2
1. Subsystem-private cards exist as a distinct schema or storage layer.
2. Export cards do not contain internal-only fields.
3. Every subsystem card can describe a horizon projection boundary.
4. The DB layer and reports distinguish internal/private vs export/public records.
5. At least one deterministic export-result placeholder exists for subsystem output.

---

## Current implementation target
This branch has completed **Phase 1** and now targets **Phase 2**: systemic privacy, subsystem-private cards, and horizon-projected export semantics.
