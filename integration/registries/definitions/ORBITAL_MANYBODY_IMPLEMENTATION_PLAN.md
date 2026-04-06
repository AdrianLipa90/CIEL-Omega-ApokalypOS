# Hierarchical Orbital Many-Body Implementation Plan v0.1

## Objective
Refactor the orbital card system so each object card carries enough structure to represent:
- limited information regime,
- subsystem horizon / event-horizon style boundary,
- holonomic leakage policy,
- many-body synchronization role,
- local versus orbit versus system `tau`,
- bridge / broker / Lagrange-style transfer roles.

The implementation must avoid semantic shortcuts: every new field added to the card system must have a deterministic derivation rule, persistence path, and audit trail.

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

---

## Phase Map

### Phase 0 — Alignment and constraints
- Freeze current `main` head.
- Record implementation plan and TODOs.
- Identify the current resolver and DB persistence boundaries.

### Phase 1 — Card schema v0.2
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

### Phase 2 — Horizon semantics and leakage rules
- Formalize horizon classes and allowed visibility transitions.
- Encode the first deterministic leak-policy table.
- Make `lagrange_roles` explicit for bridge / broker / transfer-node objects.

### Phase 3 — Local synchronization scaffolding
- Add explicit local synchronization metadata:
  - `tau_local`
  - `tau_orbit`
  - `tau_system` hooks or derivation slots
- Define the first subsystem/board aggregation rules.

### Phase 4 — Runtime integration
- Feed card-derived horizon and regime metadata into orbital runtime / bridge layers.
- Ensure downstream reports can consume the richer card schema.

### Phase 5 — Audit and tests
- Add regression tests for:
  - recursion guard,
  - stable IDs,
  - deterministic container/horizon derivation,
  - persistence of the v0.2 fields.

---

## Acceptance criteria for Phase 1
1. Re-running the resolver yields deterministic `container_card_id` and `horizon_id` values.
2. Every non-file card has a non-null container reference.
3. Every card has an `information_regime` and `leak_policy`.
4. `records.sqlite` persists the new metadata.
5. `orbital_assignment_report.json` contains counts for the new dimensions.

---

## Current implementation target
This branch will implement **Phase 1** completely and only the scaffolding necessary to support later phases.
