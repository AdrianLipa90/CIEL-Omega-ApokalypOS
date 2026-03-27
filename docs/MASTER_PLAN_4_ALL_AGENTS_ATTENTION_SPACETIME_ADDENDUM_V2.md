# MASTER PLAN FOR ALL AGENTS — SPACETIME ADDENDUM V2

## Status of this document

This document supersedes `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION_SPACETIME_ADDENDUM.md` as the current `spacetime` correction layer for the Sapiens panel direction.

It does **not** replace `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION.md`.
It updates the prior addendum by tightening the implementation boundary between:

- controller state,
- packet/session state,
- support/recovery state,
- world/habitat state,
- and future cockpit/native convergence.

---

## 1. Stable core accepted from the master plan

The original master plan remains correct in its main directional claim:

- the Sapiens panel must be a **state-driven orchestrator shell**,
- not an isolated flat chat UI,
- not a widget-first surface,
- not a semantically detached support dashboard.

The following should remain stable:

- the four-tab shell:
  - Control
  - Settings
  - Communication
  - Support
- orbital state remains upstream of communication,
- bridge state remains upstream of packet generation,
- machine-readable persistence remains mandatory,
- English system-facing artifacts remain mandatory.

---

## 2. Refined dependency order

The original master plan uses:

```text
relation -> state -> control -> memory -> surface
```

This should now be refreshed to:

```text
relation -> state -> world -> control -> memory -> packet -> support -> surface
```

### Meaning

- **relation** remains primary,
- **state** remains the first internal computed condition,
- **world** provides the environment in which the state exists,
- **control** derives from state plus world,
- **memory** is downstream of stabilized control regime,
- **packet** is the explicit communication-facing projection,
- **support** is the normalized recovery/diagnostic interpretation layer,
- **surface** renders all previous layers.

### Why this refresh matters

Without explicit `world`, `packet`, and `support` positions in the dependency chain, they will drift into:
- UI-local hacks,
- controller overreach,
- support-tab-only semantics,
- or generic session fields.

---

## 3. Controller boundary must now be explicit

The earlier addendum widened the controller target beyond four fields.
This refresh makes the boundary operational.

### Minimum durable controller target

```text
PanelState
  orbital
  bridge
  settings
  session
  packet
  support_state
  provenance
```

### Extended target if habitat/world work is accepted

```text
PanelState
  orbital
  bridge
  settings
  session
  packet
  support_state
  provenance
  world
```

### Required rule

The controller may **assemble** all of these layers, but it must **not** become the place where each subsystem invents its own semantics.

That means:
- orbital semantics stay in orbital/runtime code,
- bridge semantics stay in bridge code,
- session semantics stay in session/persistence code,
- support normalization stays in support/provenance code,
- world semantics stay in a dedicated world/habitat layer if present.

### Critical anti-pattern

Do **not** turn `controller.py` into a monolithic truth engine that silently absorbs all missing abstractions.

---

## 4. Packet must be modeled as a durable object, not a view artifact

The master plan correctly treats the interaction packet as a first-class object.
This refresh makes that stricter.

### Packet must have its own explicit contract

A Sapiens packet should be treated as a persisted, inspectable, replayable object with at least:

- `schema`
- `created_at`
- `generator`
- `relation_state`
- `orbital_summary`
- `bridge_summary`
- `control_profile`
- `memory_excerpt`
- `session_ref`
- `provenance_ref`

### Rule

The packet must not exist only as:
- rendered text,
- ephemeral widget state,
- or raw prompt text sent to a model.

It must remain a machine-readable object that can be:
- inspected,
- stored,
- replayed,
- compared,
- exported.

---

## 5. Session and replay compatibility must be reserved structurally

The original plan mentions transcript and session persistence.
The prior addendum mentioned replay compatibility.
This refresh makes replay reservation mandatory.

### Minimum requirement

The session layer should be designed so that future replay does **not** require a schema break.

### That means reserving space for:

- `session_id`
- `turns`
- `turn_timestamps`
- `packet_refs`
- `settings_snapshot`
- `controller_snapshot_ref`
- `support_snapshot_ref`
- optional `world_snapshot_ref`

### Rule

Even if replay UI is not implemented in Phase 1, replay-compatible structure should exist from the start.

---

## 6. Support must become a normalized operational layer, not a dump tab

This point stays critical and should be strengthened.

### Support should expose two simultaneous layers

#### A. normalized diagnosis
- health state
- closure class
- recommended action
- confidence band
- recent failure mode
- recovery readiness

#### B. raw traceability
- artifact paths
- timestamps
- raw JSON
- report bundle export
- source chain
- recovery notes

### Rule

Support must not be reduced to either:
- pure human-readable advice,
- or pure raw dump.

Both layers are required.

---

## 7. Provenance must be a first-class panel object

The original master plan mentions traceability.
This refresh promotes provenance from a reporting concern to a controller-level concern.

### Provenance should include

- schema versions,
- generator identifiers,
- timestamps,
- source artifact paths,
- report paths,
- packet paths,
- session bundle paths,
- recovery anchors,
- last successful generation chain,
- degraded-mode flags when applicable.

### Reason

Without explicit provenance, the panel can become visually coherent while being epistemically weak.

---

## 8. Recovery should be designed as a control path

Recovery cannot remain only a support-side convenience.

### Recovery should have machine-readable anchors for at least

- last known good packet,
- last known good session bundle,
- last good support summary,
- last successful controller snapshot,
- rebuildable settings source,
- recovery notes.

### Rule

A recovery action should be able to say what it is restoring **from**.
If it cannot, it is not a real recovery path.

---

## 9. Native/cockpit convergence must be contract-first

The master plan correctly delays convergence with cockpit/native surfaces until later phases. fileciteturn115file0L1-L1

This refresh adds one constraint:

### Rule

Convergence must happen through shared contracts, not by copying UI logic between shells.

That means future convergence should happen through:
- shared controller snapshots,
- shared session bundle schemas,
- shared packet schemas,
- shared provenance/recovery objects,
- optionally shared world/habitat schemas.

### Anti-pattern

Do **not** merge panel and cockpit by copy-pasting tabs, widgets, or rendering code.

---

## 10. Recommended refreshed repository layout

```text
src/ciel_sot_agent/sapiens_panel/
    __init__.py
    models.py
    controller.py
    settings_store.py
    session_store.py
    packet.py
    support.py
    provenance.py
    communication.py
    render_schema.py

integration/sapiens/
    README.md
    AGENT1.md
    panel_manifest.json
    settings_defaults.json
    schemas/
        panel_state.schema.json
        settings.schema.json
        packet.schema.json
        session_bundle.schema.json
        support_state.schema.json
        provenance.schema.json

integration/reports/sapiens_client/
    README.md

integration/reports/sapiens_panel/
    README.md

scripts/
    run_sapiens_panel.py
```

### Optional extension if habitat/world is adopted

```text
src/ciel_sot_agent/sapiens_world/
    __init__.py
    models.py
    adapter.py

integration/sapiens/schemas/
    world_state.schema.json
```

### Reason

This keeps:
- packet logic explicit,
- session logic explicit,
- provenance explicit,
- support normalization explicit,
- and prevents `controller.py` from turning into an unstructured sink.

---

## 11. Refreshed implementation phases

### Phase 1 — controller and persistence foundation
Create:
- `models.py`
- `controller.py`
- `settings_store.py`
- `session_store.py`
- `packet.py`
- `integration/sapiens/settings_defaults.json`
- `integration/sapiens/panel_manifest.json`
- schema files

Goal:
- durable controller contract,
- durable packet contract,
- durable session contract,
- no visual richness required.

### Phase 2 — support/provenance gate
Add:
- `support.py`
- `provenance.py`
- recovery metadata
- generation chain visibility
- executable tests for controller assembly and schema validity

Goal:
- epistemic integrity before visual richness.

### Phase 3 — communication shell
Add:
- conversation rendering,
- packet inspection,
- transcript/session persistence,
- replay-compatible packet/session references.

### Phase 4 — cockpit/native convergence
Only after previous phases are stable:
- connect live orbital/bridge state widgets,
- align replay/session contracts,
- expose shared health/status objects,
- optionally align with world/habitat contracts if adopted.

---

## 12. Refreshed agent rules

In addition to the base master plan, agents should obey:

1. Do **not** let `controller.py` silently become the semantic home of all missing abstractions.
2. Do **not** let packet state live only inside communication widgets.
3. Do **not** let support semantics live only inside the Support tab.
4. Do **not** treat report paths alone as sufficient provenance.
5. Do **not** introduce replay semantics ad hoc after communication shipping.
6. Do **not** fuse world/habitat semantics into generic session objects unless that layer is explicitly rejected.
7. Do **not** allow shell choice to define the core state contract.

---

## 13. Final refreshed recommendation

The original master plan should remain the main directional document. fileciteturn115file0L1-L1

This V2 addendum should be read as the stricter implementation guard for:

- controller boundary discipline,
- packet durability,
- replay reservation,
- support normalization,
- provenance and recovery rigor,
- and future contract-first convergence with cockpit/native surfaces.

The panel should therefore be treated as:

- a human-facing operational manifold,
- with explicit provenance,
- explicit packet/session contracts,
- explicit recovery anchors,
- and no hidden migration of truth into widgets.
