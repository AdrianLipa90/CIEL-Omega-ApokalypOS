# MASTER PLAN FOR ALL AGENTS — ATTENTION

## Document purpose

This file defines the shared implementation direction for the **Main Control / Settings / Communication / Support Panel for Sapiens**.

It is written to align all agent work with the current shape of `CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold` and to prevent parallel, semantically conflicting UI or control surfaces.

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
   - builds a human-model interaction packet,
   - consumes bridge-aware state,
   - stores session-facing artifacts.

This means the panel must not be invented from nothing.
It must be built as the **human-facing operational manifold** of those existing layers.

---

## Required panel structure

The panel must use the following main tabs:

1. **Control**
2. **Settings**
3. **Communication**
4. **Support**

These tabs are mandatory because they reflect real operational distinctions:

- **Control** = direct action and system state interaction,
- **Settings** = persistent preferences and runtime mode selection,
- **Communication** = explicit interaction channel between Sapiens and the model,
- **Support** = diagnostics, logs, health indicators, and operational help.

---

## Meaning of each tab

### 1. Control
Must expose:
- start / stop / reset style orchestration hooks,
- orbital pass execution or bridge refresh triggers,
- mode selection where operationally justified,
- visible current system state summary.

This tab is action-oriented.
It must not be overloaded with transcript history or static documentation.

### 2. Settings
Must expose:
- model / runtime preferences,
- persistence-related settings,
- optional toggles that affect bridge or packet production,
- user-facing preference management.

This tab is configuration-oriented.
It must be distinct from direct execution control.

### 3. Communication
Must expose:
- the direct human-model communication channel,
- transcript or message history,
- session-aware exchange surface,
- later packet-aware interaction if the deeper runtime is connected.

This tab is the actual **Sapiens ⇄ model relation surface**.
It must be treated as central, not cosmetic.

### 4. Support
Must expose:
- diagnostics,
- health / warnings,
- logs,
- guidance / support materials,
- bridge and runtime readiness indicators.

This tab is not a junk drawer.
It is the explicit operational support surface.

---

## Current implementation directive

The panel should be implemented around the already existing:

- `src/ciel_sot_agent/sapiens_panel/controller.py`
- `src/ciel_sot_agent/sapiens_panel/reduction.py`
- `src/ciel_sot_agent/sapiens_client.py`
- orbital bridge artifacts under `integration/reports/orbital_bridge/`
- Sapiens manifests under `integration/sapiens/`

This means:

### The panel is not an isolated UI toy.
It is a controller-facing and state-reduced view over real manifests and packets.

---

## Required implementation philosophy

### Phase 1 — correct skeleton
Build or refactor the panel so that:
- the top-level structure is exactly Control / Settings / Communication / Support,
- state is managed centrally,
- tabs are semantically distinct,
- English system-facing language is used,
- the panel is prepared to consume bridge and packet state.

### Phase 2 — state coupling
Then connect:
- Control -> orbital bridge + recommended actions,
- Settings -> persistent defaults and model/runtime options,
- Communication -> session/transcript and later packet exchange,
- Support -> health manifest, diagnostics, warnings, logs.

### Phase 3 — cockpit/native convergence
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
