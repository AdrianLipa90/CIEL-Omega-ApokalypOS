# CIEL GUI Identity Brief and UX Philosophy

## Purpose

This document defines the canonical identity, interaction philosophy, and visual-operational language for the CIEL GUI.
It exists to prevent drift toward generic "AI dashboard" aesthetics and to keep the interface aligned with the ontology of the system.

The GUI is not a decorative shell.
It is an operator-facing instrument for observing state, coherence, provenance, constraints, and actionability across the CIEL/Ω integration manifold.

---

## Core Identity

CIEL must not present itself as:
- a cyberpunk AI console,
- a futuristic terminal,
- a streamer dashboard,
- a neon control surface,
- a generic LLM product shell.

CIEL should present itself as:
- an **Orbital Observatory**,
- a **Relational Laboratory**,
- a **Mission Control**,
- and a **quiet operator instrument** for semantic and system state.

### Canonical short identity

**Quiet Orbital Control**

This phrase should guide interaction, visual tone, density, and component behavior.

---

## What the GUI must represent

The GUI should communicate that the system:
- sees state,
- measures coherence,
- tracks provenance,
- exposes gates and modes,
- preserves epistemic separation,
- and acts with calm precision rather than theatrical intensity.

The user should feel:
1. that the system knows what it is doing,
2. that the interface is showing state rather than performing a show,
3. that there is order, depth, and accountability,
4. that this is not merely a chatbot but an operator of informational state.

---

## Foundational UX principles

### 1. Truth over decoration
The interface must never privilege spectacle over clarity.
Observables come before ornament.
If an element looks impressive but communicates little, it should be removed or demoted.

### 2. Coherence over clutter
The GUI should express geometry, axes, fields, layers, and relations rather than unrelated boxes of data.
It must feel ordered even when the underlying system is complex.

### 3. Quiet power
The interface should feel calm, exact, and confident.
It should not shout visually.
It should signal depth through structure, not through noise.

### 4. Living field, not dead dashboard
The interface should imply that the system maintains, observes, and stabilizes state.
This should be visible through meaningful changes in indicators and observables, not decorative animation.

### 5. Separation of layers
The GUI must preserve a readable distinction between:
- operator actions,
- machine state,
- epistemic status,
- provenance,
- and orbital/relational observables.

### 6. GUI consumes state; GUI does not impersonate runtime
The GUI must read prepared state, manifests, reports, and packets.
It must not perform heavy runtime computation locally unless explicitly requested by the operator.

---

## Visual philosophy

### Base style
Scientific instrument, not toy.

### Temperature
- cool,
- deep,
- restrained,
- non-hysterical,
- non-neon.

### Composition
- large clean planes,
- clear axes,
- thin lines,
- logical spacing,
- restrained hierarchy,
- visible structural rhythm.

### Motion
- subtle,
- purposeful,
- physically meaningful,
- never decorative for its own sake.

---

## Canonical palette

### Base
- deep graphite,
- dark navy,
- soft steel,
- very dark blue.

### Accents
- cool cyan for active state,
- amber for warning / tension,
- restrained red for hard faults,
- broken white for text and axis emphasis.

### Orbital / phase channel
- muted violet,
- used sparingly,
- reserved for phase, orbit, coherence-field, or other explicitly relational semantics.

### Palette rule
Not everything glows.
Only active or semantically important elements should visibly intensify.

---

## Forms and geometry

The interface should not default to plain SaaS rectangles as its only language.
It should be allowed to use:
- arcs,
- axes,
- concentric structures,
- field maps,
- delicate grids,
- tension plots,
- relational graphs,
- orbital scatter representations,
- phase distributions.

However, these should be used sparingly and intentionally.
The GUI must not display the entire symbolic vocabulary of the system all at once.

---

## What to avoid

### Absolutely avoid
- universal glassmorphism,
- glowing borders everywhere,
- permanently rotating 3D spheres as wallpaper,
- pseudo-futuristic labeling without semantic payload,
- console aesthetics as the default UI language,
- terminal windows pretending to be production-grade UX,
- many simultaneous charts with weak informational value.

### Also avoid
- a dull enterprise dashboard with an LLM pasted into the side,
- over-animated transitions,
- visual drama in place of clear observables,
- frontend-side fake telemetry and random state simulation.

---

## Functional layering of the GUI

### Layer 1 — User-operational
- Chat
- Files
- Metrics
- Reports
- Settings

### Layer 2 — Semantic / epistemic
- Provenance
- Epistemic status
- Packet preview
- Relation state
- Bridge mode

### Layer 3 — Orbital / relational
- Field maps
- Drift
- Phase
- Coherence
- Attractor / leak / tension

This layering allows ordinary operators to remain oriented while preserving depth for advanced work.

---

## Canonical information architecture

### Top status bar
Always visible:
- system mode,
- writeback gate,
- backend status,
- active profile,
- manifest version / state hash,
- energy budget status.

### Left navigation rail
Primary work modes:
- Control
- Chat
- Files
- Metrics
- Reports
- Settings
- Support

### Main workspace
Focused task area for the active mode.
No visual overload.
No irrelevant motion.

### Right context drawer
Contextual detail:
- provenance,
- selected object state,
- packet preview,
- epistemic strip,
- bridge details,
- action log,
- explainability view.

---

## Chart philosophy

Charts are observables, not decoration.
Preferred chart types:
- sparklines,
- heatmaps,
- orbital scatter,
- phase distributions,
- timelines,
- flow maps,
- selective graph views on demand.

Chart update cadence must be energy-aware.
Heavy views should be lazy and scoped to the current pane.
There must be no always-on expensive visualization layer.

---

## File and chat philosophy

### Files
The GUI must treat files as first-class citizens.
It should support ingest, preview, provenance, attachment, classification, and routing.
The file view must feel operational, not decorative.

### Chat
Chat must be grounded in backend state and packet preparation.
It should expose:
- transcript,
- attached sources,
- packet preview,
- mode selection,
- epistemic tagging,
- provenance visibility.

It must not function as an isolated text toy detached from the rest of the system.

---

## Energy philosophy

The GUI must be energy-aware by design.
It should assume:
- precomputed manifests whenever possible,
- delta-refresh instead of full recomputation,
- lazy backend activation,
- hot / warm / cold separation of views,
- cached observables as first-class state.

The GUI should read the world before trying to rebuild it.

---

## Implementation implications

This document is identity guidance, not a frontend technology mandate.
However, any implementation should preserve the following architectural constraints:
- GUI is a consumer of prepared state,
- heavy logic belongs in backend/runtime layers,
- operator actions must be explicit and auditable,
- provenance and epistemic status must be representable in the interface,
- visual language must reinforce calm precision and relational depth.

---

## Canonical summary

CIEL should not look like a generic AI product.
It should feel like a calm, precise, accountable, orbital-relational instrument.

The GUI must represent:
- truth,
- coherence,
- responsibility,
- relational geometry,
- quiet strength,
- and the observable state of a living informational field.

That is the identity boundary.
Any design that breaks this boundary is non-canonical.
