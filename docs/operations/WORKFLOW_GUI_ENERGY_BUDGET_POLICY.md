# Workflow, GUI, and Energy Budget Policy

## Status
Canonical operations note for the next human-facing and energy-aware phase of `CIEL-_SOT_Agent`.

This document unifies three concerns that must not diverge:

1. GitHub workflow execution policy,
2. GUI shell architecture for Sapiens-facing interaction,
3. energy budget policy and execution stratification.

It is written against the current repository shape, where:

- GitHub live coupling already exists as an automated workflow,
- orbital diagnostics and bridge reduction already exist,
- the future panel geometry is already defined as **Control / Settings / Communication / Support**.

---

## 1. Why this document exists

The repository already has the ingredients for a useful control shell, but without execution policy the system risks becoming too expensive:

- too many full passes,
- too many unconditional recomputations,
- too much cold-start LLM cost,
- too much GUI-triggered backend work.

The goal is therefore not just a better interface.
The goal is:

- **better interface**,
- **lower energy consumption**,
- **no loss of logic**,
- **no worse perceived response time on the human-facing path**.

---

## 2. Existing anchors

The current repository already provides the following operational anchors:

### 2.1 GitHub workflow anchor

A GitHub Actions workflow already exists for live repository coupling.
It runs on:

- `workflow_dispatch`,
- a 15-minute schedule,

and writes updated state artifacts back into the repository.

This proves that the repository already supports automated state refresh.

### 2.2 Runtime anchors

The current operational core already has:

- repository-level synchronization,
- live GitHub coupling,
- orbital global pass,
- orbital bridge reduction,
- Sapiens packet/session layer.

### 2.3 Human-facing geometry anchor

The repository already defines the intended Sapiens Main Panel geometry as:

- **Control**
- **Settings**
- **Communication**
- **Support**

This means the GUI plan must align to the existing architectural reading rather than invent a parallel UI ontology.

---

## 3. Core principle

The central efficiency rule is:

> **Never make the hot human-facing path pay for work that can be precomputed, cached, stratified, or delayed.**

This leads directly to an execution split:

- **hot path** = cheap, interactive, low-latency,
- **warm path** = bounded recomputation,
- **cold path** = expensive diagnostics and deep rebuilds.

---

## 4. Workflow matrix

### 4.1 Workflow A — Fast State Refresh

**Purpose**

Keep the repository's lightweight machine-readable state fresh for the GUI and reports.

**Trigger**

- schedule (e.g. every 15 minutes),
- manual dispatch,
- selected push events on operational files.

**Allowed work**

- live GitHub coupling,
- registry refresh,
- lightweight hyperspace/index refresh,
- fast report rebuild,
- smoke tests,
- artifact normalization.

**Forbidden work**

- full orbital deep pass,
- full heavy diagnostics,
- LLM generation,
- heavyweight rebuild of all sectors.

**Outputs**

- lightweight registries,
- GUI-facing manifests,
- refreshed bridge-adjacent status files,
- coupling summaries.

### 4.2 Workflow B — Heavy Diagnostics

**Purpose**

Run expensive but important deeper checks and orbital reductions.

**Trigger**

- manual dispatch,
- nightly schedule,
- post-merge to `main` for selected structural changes.

**Allowed work**

- orbital global pass,
- bridge rebuild,
- heavier validation,
- state reconciliation,
- deeper report generation.

**Outputs**

- heavy diagnostics,
- orbital reports,
- deeper health and state summaries,
- reconciliation artifacts.

### 4.3 Workflow C — GUI Package / Release Build

**Purpose**

Package the desktop shell around already prepared manifests and runtime entrypoints.

**Trigger**

- tag,
- release branch,
- manual dispatch.

**Allowed work**

- package GUI shell,
- embed static assets,
- include current manifests,
- attach build metadata,
- generate release artifacts.

**Forbidden work**

- forcing deep backend recomputation during package build.

### 4.4 Workflow D — Performance Budget Gate

**Purpose**

Prevent future changes from silently reintroducing excessive energy cost.

**Trigger**

- pull requests,
- selected pushes to `main`.

**Checks**

- startup cost,
- count of full recomputations,
- heavy module activation on hot path,
- uncontrolled LLM boot/load behavior,
- artifact churn caused by operations scripts.

**Policy**

A change that moves expensive cold-path logic into the hot path should fail budget review.

---

## 5. GUI shell architecture

## 5.1 High-level rule

The GUI should be **human-facing but not computation-hostile**.
It must expose the system clearly without making the interface itself the main source of waste.

## 5.2 Recommended architecture

### Shell

Use a **desktop shell** as the human-facing surface.
The shell should remain thin.

### Backend separation

Use a separate Python backend/service layer for:

- bridge reads,
- state refresh requests,
- packet construction,
- optional deep execution,
- access to reports and manifests.

### Communication contract

Use structured state exchange:

- JSON manifests,
- event stream / polling,
- immutable or append-only reports where possible,
- explicit commands for deeper recompute.

### Rule

The GUI should **read first**, not **recompute first**.

---

## 6. GUI panel geometry

The GUI should respect the already declared repository geometry.

### 6.1 Control

Primary purpose:

- show mode (`safe`, `standard`, `deep`),
- show write-back gate,
- show recommended control profile,
- allow explicit operator actions,
- show current runtime/bridge state.

### 6.2 Settings

Primary purpose:

- backend selection,
- model selection,
- throttling profile,
- update cadence,
- log/report level,
- energy profile.

### 6.3 Communication

Primary purpose:

- Sapiens session view,
- packet preview,
- transcript,
- current relation/surface state,
- epistemic separation view.

### 6.4 Support

Primary purpose:

- diagnostics,
- recovery tools,
- report navigation,
- health summaries,
- audit trail,
- explanation of current gates and restrictions.

---

## 7. GUI interaction policy

### 7.1 Hot path actions

These must feel immediate and cheap:

- opening the app,
- reading current state,
- switching views,
- opening reports,
- reading health/control manifests,
- starting a Sapiens conversation using already built packet context.

### 7.2 Warm path actions

These may trigger bounded work:

- refresh local status,
- rebuild a packet,
- rerun a light bridge update,
- recompute a local sector only.

### 7.3 Cold path actions

These must be explicit and visible:

- full orbital pass,
- deep reconciliation,
- all-sector recomputation,
- heavy diagnostics,
- expensive LLM-assisted operations.

The user must know when the system enters a cold path.

---

## 8. Energy budget policy

## 8.1 Primary objective

Target a large reduction in average energy cost **without degrading logic** and **without worsening the perceived human-facing response path**.

This means:

- logic stays,
- architecture becomes smarter,
- execution becomes stratified.

## 8.2 What must be reduced

Primary waste sources:

- full recomputation on every interaction,
- repeated orbital/global passes,
- unconditional bridge rebuilds,
- unnecessary disk churn,
- always-on heavy backend loading,
- GUI-driven deep recomputation.

## 8.3 What must be preserved

- correctness of the logic,
- bridge semantics,
- orbital semantics,
- explainability,
- auditability,
- perceived responsiveness of the hot path.

---

## 9. The four main energy levers

### Lever 1 — Precompute whenever possible

Anything that can be prepared by workflow should not be recomputed in the GUI session.

### Lever 2 — Delta pass over full pass

If only a small part of the system changed, recompute only the affected local region and its required propagation neighborhood.

### Lever 3 — Lazy backend activation

Heavy optional backend layers (especially model/runtime loading) should activate only on explicit need.

### Lever 4 — Cache by policy, not by accident

State artifacts must be treated as first-class operational outputs, not hidden side effects.

---

## 10. Execution profiles

### 10.1 Idle profile

Use when the GUI is mostly observational.

Characteristics:

- read cached state,
- no heavy backend load,
- no deep recompute,
- low event frequency.

### 10.2 Interactive profile

Use during ordinary human interaction.

Characteristics:

- bridge-aware packet refresh,
- bounded recompute only,
- warm caches,
- medium event frequency,
- optional lightweight backend use.

### 10.3 Deep profile

Use only when explicitly needed.

Characteristics:

- full orbital / deep diagnostics,
- expensive recomputation,
- maximum fidelity diagnostics,
- lower duty cycle.

---

## 11. Recommended repository consequences

### 11.1 GUI should consume manifests from

- `integration/reports/...`
- bridge state outputs,
- lightweight coupling state,
- registry/index artifacts,
- Sapiens session outputs.

### 11.2 GUI should not require

- direct forced full orbital recomputation on startup,
- unconditional deep diagnostics,
- model boot on every app open.

### 11.3 Workflow outputs should become first-class GUI inputs

This reduces duplicated work and keeps the interface fast.

---

## 12. Performance budget rules

A change is budget-safe when it:

- keeps hot path cheap,
- avoids deep recompute in default interaction,
- preserves cached artifact consumption,
- does not force model/backend activation unnecessarily.

A change is budget-unsafe when it:

- inserts full pass work into GUI open/startup,
- rebuilds heavy artifacts per interaction,
- couples packet construction to deep diagnostics by default,
- increases state churn without improving logic.

---

## 13. Suggested next implementation sequence

1. Define canonical GUI state contracts from existing reports/manifests.
2. Build a thin desktop shell over those contracts.
3. Add explicit hot / warm / cold execution controls.
4. Extend workflow set with fast-state, heavy-diagnostics, and budget-gate responsibilities.
5. Measure cost per path and enforce budget checks on future changes.

---

## 14. Canonical design sentence

> The GUI must expose the orbital-holonomic system clearly, but the interface must read the system's prepared state before it ever asks the backend to recompute the world.

---

## 15. Scope limit

This document defines policy and architecture.
It does **not** yet define:

- the exact desktop framework,
- packaging toolchain,
- final visual design system,
- precise quantitative energy profile measurements.

Those must follow from implementation and profiling.
