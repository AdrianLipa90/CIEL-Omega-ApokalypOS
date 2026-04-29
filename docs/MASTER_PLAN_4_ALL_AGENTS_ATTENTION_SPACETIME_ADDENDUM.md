# MASTER PLAN FOR ALL AGENTS — SPACETIME ADDENDUM

## Status of this document

This file does **not** replace `docs/MASTER_PLAN_4_ALL_AGENTS_ATTENTION.md`.
It refines it with implementation corrections and structural guards proposed from the `spacetime` side.

The original master plan is directionally correct: it properly identifies the Sapiens panel as a **state-driven orchestrator shell** above orbital, bridge, session, and settings layers.

This addendum introduces the corrections required to keep that plan executable, debuggable, and extensible.

---

## 1. Accepted core of the original plan

The following parts of the original master plan should remain unchanged:

- the panel must be **state-driven**, not widget-driven,
- the panel must not degenerate into an isolated flat chat UI,
- orbital state and bridge state remain upstream of communication,
- the four-tab shell is correct:
  - Control
  - Settings
  - Communication
  - Support
- machine-readable persistence under `integration/` is mandatory,
- packet-aware communication is mandatory.

These points should be treated as stable.

---

## 2. First correction — add a habitat/world layer explicitly

### Problem

The original dependency order is:

```text
relation -> state -> control -> memory -> surface
```

This is conceptually strong, but operationally incomplete if the project is expected to support a richer agent-side state geometry.

### Proposed refinement

```text
relation -> state -> world -> control -> memory -> packet -> surface
```

### Meaning

- **relation** remains primary,
- **state** remains the first computed internal condition,
- **world** introduces the environment in which the state lives,
- **control** derives from state plus world,
- **memory** is downstream of stabilized control regime,
- **packet** is the communication-facing projection,
- **surface** renders all of the above.

### Reason

Without an explicit world/habitat layer, future agent-space work will be forced to leak into:
- session state,
- support logic,
- UI-local rendering hacks.

That would create semantic drift and controller pollution.

### Minimal rule

If the project introduces habitat, map, sector, spatial, recovery-zone, or environment semantics, they must live in a dedicated state object rather than being scattered across tabs.

---

## 3. Second correction — the controller must aggregate more than four sources once the panel matures

The original controller target is:

```text
PanelState
  orbital
  bridge
  session
  settings
```

This is good for the first shell, but too narrow for a durable panel.

### Proposed mature target

```text
PanelState
  orbital
  bridge
  session
  settings
  world
  support_state
  provenance
```

### Meaning of new fields

- `world`
  - habitat or environment layer if introduced,
  - zone, risk, resource, and temporal context.

- `support_state`
  - normalized recovery and diagnostic state,
  - not just raw bridge health values copied ad hoc into widgets.

- `provenance`
  - artifact paths,
  - generation timestamps,
  - schema versions,
  - snapshot/session references,
  - recovery anchors.

### Reason

The original plan already requires traceability.
Traceability becomes fragile if provenance is treated as a display concern instead of a controller concern.

---

## 4. Third correction — define a native-shell discipline explicitly

The original master plan correctly avoids a flat chat UI, but it does not state whether the panel is allowed to drift into an arbitrary web-first shell.

### Proposed implementation discipline

Until explicitly overruled by repository-wide decision, the panel should be specified as:

- **controller-first**,
- **platform-agnostic at the state level**,
- **surface-pluggable**,
- **not dependent on HTTP semantics for its core logic**.

### Rule

No critical logic may live only in:
- browser callbacks,
- UI-local state,
- HTTP request handlers,
- front-end-only stores.

### Reason

The panel is an operational manifold, not a web mockup.
The state and controller layers should be portable across:
- native shell,
- scripted shell,
- future panel surface.

---

## 5. Fourth correction — versioned persistence must be explicit from Phase 1

The original plan requires persistence under `integration/sapiens/`, which is correct.

### Missing constraint

The plan should also require explicit schema/version discipline.

### Proposed rule

Every persisted panel artifact should carry a schema version, for example:

- `panel_manifest.json`
- `settings_defaults.json`
- session state bundles
- packet reports
- transcript bundles

### Minimal metadata contract

Each persisted object should expose at least:

- `schema`
- `created_at`
- `updated_at`
- `source_paths`
- `generator`

### Reason

Without this, later replay/recovery/session work will become ambiguous and break silently.

---

## 6. Fifth correction — recovery is not optional support polish

The original Support tab mentions recovery tools, which is correct, but too weakly framed.

### Proposed stronger rule

Recovery must be treated as a first-class control path, not a UI convenience.

### Required recovery objects

The panel design should reserve machine-readable space for:

- last good state anchor,
- current report bundle,
- last packet bundle,
- last session bundle,
- explicit recovery notes,
- rebuildable manifests.

### Reason

The repository already operates through generated state layers and integration artifacts.
If these are not recoverable, the panel becomes operationally fragile.

---

## 7. Sixth correction — support must expose normalized diagnosis, not raw dump only

The Support tab should not become merely a file browser for generated artifacts.

### Proposed rule

Support should expose two levels:

1. **normalized operational diagnosis**
   - health state,
   - closure class,
   - recommended action,
   - confidence band,
   - last successful generation chain.

2. **raw traceability**
   - paths,
   - timestamps,
   - raw JSON,
   - bundle export.

### Reason

Operators need both:
- a readable diagnosis,
- and exact traceability.

Only raw dump makes the panel too heavy.
Only normalized diagnosis makes it untrustworthy.

---

## 8. Seventh correction — communication must reserve packet replay compatibility

The original plan correctly treats the packet as a first-class object.

### Missing extension

The plan should explicitly reserve compatibility for:

- packet replay,
- session replay,
- packet/session provenance,
- future convergence with cockpit replay systems if those become canonical.

### Reason

If communication is implemented without replay-aware contracts, later convergence will require schema breakage.

---

## 9. Eighth correction — implementation phases should include a provenance/test gate before visual richness

The original phases are directionally good.

### Proposed phase refinement

#### Phase 1 — controller and persistence foundation
Create:
- controller layer,
- panel state model,
- settings store,
- manifest files,
- schema/version contract.

#### Phase 2 — support/provenance gate
Add:
- recovery metadata,
- artifact paths,
- timestamps,
- source chain visibility,
- executable tests for controller assembly.

#### Phase 3 — communication shell
Add:
- session rendering,
- packet view,
- transcript persistence,
- replay-aware packet/session compatibility.

#### Phase 4 — cockpit/native convergence
Only after the previous phases are stable:
- connect to native or cockpit-facing surfaces,
- expose live widgets,
- unify replay/session contracts where appropriate.

### Reason

If communication richness arrives before provenance discipline, the panel will look finished while remaining epistemically weak.

---

## 10. Suggested repository additions

The original proposed layout is good, but should be expanded slightly.

### Proposed target

```text
src/ciel_sot_agent/sapiens_panel/
    __init__.py
    models.py
    controller.py
    settings_store.py
    communication.py
    support.py
    provenance.py
    render_schema.py

integration/sapiens/
    README.md
    AGENT1.md
    panel_manifest.json
    settings_defaults.json
    schemas/
        panel_state.schema.json
        settings.schema.json
        session_bundle.schema.json

integration/reports/sapiens_client/
    README.md

integration/reports/sapiens_panel/
    README.md

scripts/
    run_sapiens_panel.py
```

### Reason

This keeps provenance and report emission explicit instead of burying them inside generic support code.

---

## 11. Additional agent coordination rules

In addition to the original rules, agents should also obey the following:

1. Do **not** treat generated report paths as sufficient provenance by themselves.
2. Do **not** let recovery metadata live only in Support tab widgets.
3. Do **not** let panel settings evolve without schema/version discipline.
4. Do **not** fuse habitat/world semantics into session state unless a dedicated world layer is explicitly rejected.
5. Do **not** allow visual shell decisions to define the controller contract.
6. Do **not** introduce packet replay semantics ad hoc after communication shipping; reserve them structurally early.

---

## 12. Final recommendation

The original master plan should remain the **main directional document**.

This addendum should be read as an implementation correction layer that strengthens it in five critical areas:

- explicit world/habitat compatibility,
- controller completeness,
- native-shell discipline,
- schema/provenance/recovery rigor,
- replay-aware communication planning.

If these corrections are accepted, the Sapiens panel can evolve without drifting into either:
- a flat chat frontend,
- or a visually rich but operationally weak control surface.

---

## Final note

The panel should be treated as a **human-facing operational manifold with explicit provenance**.

Not just a UI.
Not just a chat shell.
Not just a dashboard.
