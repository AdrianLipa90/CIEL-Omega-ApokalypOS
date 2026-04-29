# Omega Cockpit 1.0

## Purpose

This document defines the first architectural refactor of the current `ciel-omega-demo` UI.
The goal is **not** to replace the working local runtime shell, but to scale it from a flat runtime cockpit into an **attractor-centered system cockpit**.

The current demo is useful, but semantically too flat for Omega-scale work:

- tools are exposed as peer tabs,
- runtime concerns dominate the surface,
- the relation between theory, execution, evidence, and publication boundaries is not shown explicitly,
- epistemic status is not treated as a first-class UI signal.

Omega Cockpit 1.0 changes the organizing principle:

> tools -> layers
>
> flat tabs -> attractor + orbits
>
> launcher UI -> epistemic instrument

---

## Core principle

Omega Cockpit is organized around an **Identity Attractor**.

The center is not chat, kernel, files, or settings.
The center is the current organizing state of the system:

- active identity profile,
- coherence / resonance,
- active canon/export package,
- active operator set,
- active constraints,
- ethics gate state,
- current session phase,
- memory/provenance load,
- publication boundary state.

Everything else is arranged in orbital layers around this center.

---

## Orbital model

### Orbit 0 — Identity Attractor

Central system state.

Fields:
- identity_state
- coherence_scalar
- resonance_scalar
- ethics_gate
- active_contract
- active_canon_export
- active_operator_set
- memory_load
- session_phase
- publication_boundary_status
- critical_warnings

### Orbit 1 — Constitutive layers

What defines what Omega is.

Modules:
- Theory
- Operators
- Constants
- Constraints
- Memory Topology

Each object in this orbit should expose:
- Role
- Definition
- Derivation
- Implementation
- Test
- Status
- Interpretation

### Orbit 2 — Dynamic layers

What executes motion.

Modules:
- Kernel
- Execution
- Planner
- Session Dynamics
- Command Routing

Execution chain must be explicit:

Theory Export -> Runtime Config -> Kernel Execution -> Agent Consumption -> Evidence

### Orbit 3 — Interaction layers

What touches the user and the outside world.

Modules:
- Agent
- Chat
- Dialogue
- Tool Interface
- User Input
- Session Memory
- Files
- Models

`Chat` is not the center of the system.
It is one component inside `Agent`.

### Orbit 4 — Observational layers

What observes, measures, and audits the system.

Modules:
- Observability
- Logs
- Tests
- Audit
- Provenance
- Crossrefs
- Diagnostics

### Orbit 5 — Boundary layers

What separates internal state from external release.

Modules:
- Publication Boundary
- Public/Private Separation
- Export Manifests
- Sanitization
- Release State
- Demo/Runtime Export Visibility

---

## Screen topology

Omega Cockpit 1.0 should use a hybrid layout.

### Left panel — structural navigation

The left side is not a flat list of tools.
It is an orbit-ordered navigation tree:

- Identity Attractor
- Theory
- Execution
- Agent
- Evidence
- Boundary
- Resources
- Settings

### Center — active workspace

The center is the current working surface:

- object card,
- kernel control,
- execution trace,
- chat,
- logs,
- tests,
- artifacts,
- export review.

### Right panel — inspector

The right side remains visible as epistemic and provenance context:

- source of truth,
- active object,
- provenance,
- epistemic status,
- crossrefs,
- warnings,
- publication flags,
- related modules/files.

### Bottom strip — event line

The bottom strip shows live system state:

- active kernel,
- active model,
- active export package,
- ethics warnings/blocks,
- dirty state,
- failing tests,
- recent artifact,
- boundary mode.

---

## Epistemic status badges

Every major object, panel, or artifact should carry a visible status badge.

Initial badge set:
- canonical
- provisional
- draft
- imported
- archived
- runtime-only
- private-only
- public-exported

These badges are mandatory for avoiding semantic collapse between:
- theory,
- runtime,
- archive,
- draft,
- public export.

---

## White threads

White threads represent live dependencies between layers.

Examples:
- Theory <-> Operators
- Operators <-> Kernel
- Kernel <-> Agent
- Agent <-> Memory
- Evidence <-> Publication Boundary

In version 1.0 they do not need to be a full radial animation system.
They may initially exist as structured dependency edges in the inspector/workspace.

White-thread attributes may later encode:
- coupling strength,
- activity,
- freshness,
- canonical agreement,
- provenance confidence.

---

## Mapping from current demo to Omega Cockpit

Current top-level demo tabs:
- Dashboard
- Kernel
- Chat
- Files
- Models
- Observability
- Settings

Target Omega grouping:

- Dashboard -> Identity Attractor + System summary
- Kernel -> Execution
- Chat -> Agent
- Files -> Resources
- Models -> Resources
- Observability -> Evidence
- Settings -> Settings

This means the current demo is not discarded.
It is reclassified and reorganized.

---

## Refactor phases

### Phase 1 — non-destructive modularization

Goal:
- split the monolithic UI file into coherent modules,
- preserve current runtime behavior.

Target modules:
- identity_panel
- theory_panel
- execution_panel
- agent_panel
- evidence_panel
- resources_panel
- boundary_panel
- settings_panel
- shared inspector/event components

### Phase 2 — orbital navigation

Goal:
- replace flat top-level tabs with orbit-oriented navigation,
- keep a classical workspace for usability.

### Phase 3 — epistemic object cards

Goal:
- represent every major theory/runtime object through:
  Role / Definition / Derivation / Implementation / Test / Status / Interpretation.

### Phase 4 — publication boundary

Goal:
- expose private/public/demo/runtime separation directly in UI,
- track dirty manifests and sanitization state.

### Phase 5 — white-thread visualization

Goal:
- show active dependencies and canonical coupling across system layers.

---

## Immediate implementation rule

Omega Cockpit 1.0 must prefer:
- semantic clarity over visual novelty,
- structural truth over decorative radiality,
- explicit provenance over implied meaning,
- stable modularity over fast but opaque coupling.

The cockpit should feel orbital because the architecture is orbital,
not because the interface is merely drawn as circles.
