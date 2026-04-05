# MASTER PLAN FOR ALL AGENTS — ATTENTION

## Document purpose

This file defines the shared implementation direction for the **Main Control / Settings / Communication / Support Panel for Sapiens**.

It is written to align all agent work with the current shape of `CIEL-_SOT_Agent` and to prevent parallel, semantically conflicting UI or control surfaces.

---

## Current project reading

At the time of writing, the repository already contains four relevant layers:

1. **integration kernel**
   - repository synchronization,
   - machine-readable registries,
   - GitHub coupling,
   - report layers.

2. **orbital runtime / diagnostic layer**
   - imported and extended under `integration/Orbital/`,
   - exposes a global read-only diagnostic pass,
   - writes orbital diagnostic reports.

3. **orbital bridge layer**
   - implemented in `src/ciel_sot_agent/orbital_bridge.py`,
   - maps orbital outputs into:
     - state manifest,
     - health manifest,
     - recommended control,
     - bridge reports in `integration/reports/orbital_bridge/`.

4. **Sapiens interaction seed layer**
   - implemented in `src/ciel_sot_agent/sapiens_client.py`,
   - builds a human-model interaction packet from session state plus orbital/bridge state.

This means the correct next move is **not** to create an isolated chat UI.
The correct next move is to build a **panel-orchestrator shell** above these layers.

---

## Primary design law

The Sapiens panel must remain consistent with the orbital-holonomic reading of the project.

### Dependency order

relation -> state -> control -> memory -> surface

Operationally this means:

1. **orbital state** is computed first,
2. **bridge control state** is derived from orbital state,
3. **Sapiens session and packet state** are derived from bridge state,
4. **panel surface** renders and controls these states.

The panel must therefore be **state-driven**, not widget-driven.

---

## Main panel definition

The project should implement a single main panel shell with four primary tabs:

- **Control**
- **Settings**
- **Communication**
- **Support**

All system-facing labels, messages, and artifacts must remain in **English**.

---

## Tab 1 — Control

### Purpose
Operational control of model-facing system state.

### Required sections

- **System Status**
  - Coherence Index
  - Closure Penalty
  - System Health
  - Risk Level
  - Recommended Action
  - Current Orbital Mode
  - Truth Axis
  - Attractor State

- **Execution Controls**
  - Run Orbital Pass
  - Run Bridge Update
  - Start or Refresh Sapiens Session
  - Build Model Packet
  - Export Current State

- **Stability Controls**
  - Read-only mode
  - Guided mode
  - Standard mode
  - Deep mode

### Implementation source anchors

- `integration/Orbital/main/global_pass.py`
- `src/ciel_sot_agent/orbital_bridge.py`
- `integration/Orbital/main/phase_control.py`

---

## Tab 2 — Settings

### Purpose
Persistent configuration of the interaction regime.

### Required sections

- **Identity**
  - Sapiens ID
  - Relation Label
  - Preferred Mode
  - Memory Policy

- **Interaction Policy**
  - Truth Axis
  - Packet depth / memory excerpt length
  - Bridge auto-refresh
  - Session persistence policy

- **Orbital Runtime Settings**
  - Steps
  - dt
  - tau eta / tau reg
  - auto-bootstrap manifests

- **Language and UI**
  - system language: English
  - response style presets
  - support verbosity
  - raw JSON visibility

### Implementation rule

Settings must persist into a machine-readable file under `integration/sapiens/`.
They must not live only in UI-local state.

---

## Tab 3 — Communication

### Purpose
Direct Sapiens-to-model interaction.

### Required sections

- **Conversation Panel**
  - user input,
  - model output,
  - turn history.

- **Packet View**
  - latest model packet,
  - relation state,
  - state geometry,
  - control profile.

- **Session Memory**
  - transcript,
  - recent turns,
  - timestamps,
  - persisted session JSON.

### Implementation source anchors

- `src/ciel_sot_agent/sapiens_client.py`
- `integration/reports/sapiens_client/`

### Critical rule

Communication must not be implemented as a generic flat chat box.
It must expose the **interaction packet as a first-class object**.

---

## Tab 4 — Support

### Purpose
Assist the operator in stabilization, diagnosis, recovery, and guided usage.

### Required sections

- **Health and Diagnostics**
  - health manifest,
  - closure warnings,
  - risk level,
  - recommended action.

- **Recovery Tools**
  - rebuild manifests,
  - regenerate bridge report,
  - reset session,
  - export current bundle.

- **Guides**
  - what the modes mean,
  - what orbital pass does,
  - how bridge state changes communication behavior.

- **Traceability**
  - latest generated artifacts,
  - report timestamps,
  - transcript path,
  - packet path,
  - session path.

---

## Recommended repository layout

The first implementation should use the following layout:

```text
src/ciel_sot_agent/sapiens_panel/
    __init__.py
    models.py
    controller.py
    settings_store.py
    communication.py
    support.py
    render_schema.py

integration/sapiens/
    README.md
    AGENT1.md
    panel_manifest.json
    settings_defaults.json

integration/reports/sapiens_client/
    README.md

scripts/
    run_sapiens_panel.py
```

### Reason

This layout respects the current repository geometry:
- `src/` for executable logic,
- `integration/` for machine-readable contracts,
- `integration/reports/` for artifacts,
- `scripts/` for thin launchers.

---

## Controller model

The panel controller must aggregate four state sources:

- `orbital`
- `bridge`
- `session`
- `settings`

### Target structure

```text
PanelState
  orbital
  bridge
  session
  settings
```

### Required rule

No panel tab may construct truth independently of the controller.
The controller is the authoritative state assembler.

---

## Immediate implementation phases

## Phase 1 — panel foundation ✓ COMPLETE

Created:
- `src/ciel_sot_agent/sapiens_panel/models.py`
- `src/ciel_sot_agent/sapiens_panel/controller.py`
- `integration/sapiens/settings_defaults.json`
- `integration/sapiens/panel_manifest.json`
- `scripts/run_sapiens_panel.py`

Result:
- machine-readable and controller-driven shell in place,
- panel state aggregation (orbital, bridge, session, settings) verified by tests.

## Phase 2 — communication-centered shell (in progress)

Added:
- Flask-based Quiet Orbital Control web interface (`src/ciel_sot_agent/gui/`),
- GGUF model manager for first-startup model acquisition (`src/ciel_sot_agent/gguf_manager/`),
- GUI identity and UX philosophy document (`docs/gui/CIEL_GUI_IDENTITY_BRIEF_AND_UX_PHILOSOPHY.md`),
- energy budget and workflow policy (`docs/operations/WORKFLOW_GUI_ENERGY_BUDGET_POLICY.md`).

Still pending in this phase:
- packet-aware session rendering in the GUI,
- transcript and session persistence wired to the GUI communication tab,
- support diagnostics tab connected to the health manifest.

## Phase 3 — cockpit/native convergence

Only after the above is stable:
- connect the Sapiens panel to the cockpit/native surface if that layer is confirmed and stable,
- unify replay/session loading with the Sapiens session system,
- expose real-time orbital and bridge health widgets.

---

## Agent coordination rules

### All agents must obey the following

1. Do **not** create a separate human-model UI outside the Sapiens panel plan.
2. Do **not** bypass orbital state and bridge state when implementing communication.
3. Do **not** treat memory as prior to relation; relation state must remain primary.
4. Do **not** hard-code language drift into non-English system-facing artifacts.
5. Do **not** collapse support and control into one flat page.
6. Do **not** implement panel state independently inside isolated widgets.

### Required integration discipline

Every meaningful panel object should eventually be linked in:
- human-readable docs,
- a machine-readable index or manifest,
- tests where behavior is executable.

---

## Final implementation standard

The Sapiens panel will be considered aligned with the project only if it satisfies all of the following:

- English system-facing interface,
- Control / Settings / Communication / Support tab structure,
- controller-driven state model,
- orbital and bridge integration,
- packet-aware communication,
- report and transcript traceability,
- no semantic drift from the orbital-holonomic reading.

---

## Final note to all agents

The Sapiens panel is **not** just a UI.
It is the main human-facing operational manifold for the relation between Sapiens and the model.

Implement accordingly.
