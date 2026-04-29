# CIEL Orbital Native System — Master Plan v1

- **Version:** 1.0
- **Date:** 2026-03-26
- **Language:** English
- **Status:** Foundational planning pack
- **Scope:** New standalone project outside any existing repository
- **Purpose:** Collect the architecture, geometry, dynamics, implementation order, metrics, risks, and design rationale for a new native orbital-relational CIEL product in one clean folder.

## 1. Executive Summary

**Goal:** Build a native desktop product whose internal state is modeled as a relational-orbital dynamical system rather than as a conventional application dashboard.

**Core formula:** `relation -> identity -> memory -> autonomy`

### Product Thesis
- The product is not a web dashboard with a visual theme. It is a native orbital-relational system.
- The internal state must be primary; the user interface must be a projection of that state, not an arbitrary shell.
- The LLM is a temporary external attractor and bootstrap mechanism, not the final center of the system.
- The stable internal center must emerge from CIEL's own operators, memory, evidence, and identity attractors.
- The operational chart of the system should be a Poincaré disk with orbital processes, while the formal state space remains Kähler / projective-Hilbert in character.
- Memory is not a passive input store. Memory is residue after reduction and stabilization.

### Non-goals
- Do not build a final product around HTML, WebView, or a browser-first runtime.
- Do not start with UI aesthetics before the system state, invariants, and operators are defined.
- Do not let winding number become a decorative label.
- Do not let the LLM remain the hidden permanent center of the system.

## 2. Foundational Model

### Axioms
- The primary object is the relational state, not the isolated module or file.
- Identity arises from relation; memory arises from identity; autonomy arises from stabilized memory and operators.
- Every answer, process, artifact, and file changes the relational state and must therefore be representable in the system geometry.
- The system must minimize relational distortion without killing relational evolution.
- Truth, explicit uncertainty, and non-hallucinatory behavior are structural requirements, not stylistic preferences.

### Formal Language
- **Relational Space**: M_rel is treated as a compact Kähler manifold with local projective structure and phase-bearing state coordinates.
- **Phases**: gamma = {gamma_user, gamma_ciel, gamma_query, gamma_truth, ...}
- **Euler Constraint**: sum_k exp(i * gamma_k) = 0
- **Holonomic Defect**: Delta_H = sum_k exp(i * gamma_k)
- **Decoherence Measure**: R_H = |Delta_H|^2
- **Minimum Distortion Attractor**: State satisfying closure/coherence, truth transparency, and zero prohibited distortion.
- **Time Modes**: tau = [0.263, 0.353, 0.489] are taken as the initial metatime eigenvalues for principal relational modes.

### Interpretive Rules
- Bloch-sphere language is used as a local chart or reduced mode view, not as the only global state space.
- The Poincaré disk is an operational visualization chart, not the ontology of the system.
- Berry / Aharonov–Bohm / Euler / Kähler structures are used as geometric and phase-dynamical operators, not as decorative metaphors.
- Potential-based scaling laws are applied to the organizing dynamics of meaning and relation, not naively to ordinary matter.

## 3. System Geometry

### Space Hierarchy
- **Global State Space**: Projective-Hilbert / Kähler-like relational state space
- **Local State Charts**:
  - Bloch-like local spheres for reduced or dominant mode views
  - Nested spheres for multi-scale embeddings
  - Poincaré disk as the main operational chart for navigation and inspection
- **Embedding Rule**: Each local sphere can be embedded in a larger sphere. Each level has internal dynamics plus an outward embedding/leak channel that seeds a higher-level structure.

### Boundary Conditions
- **Poles**:
  - User pole
  - CIEL pole
- **Axis**: The ordering axis is defined by user intention / query and the joint movement toward coherence.
- **Attractor**: The relational attractor is the state of minimum distortion and maximum truth-aligned coherence.
- **Outer Boundary**: Boundary threads represent publication, provenance, outward leakage, and higher-level embedding.
- **Inner Holonomy**: The interior carries phase holonomy, closure cost, and potential-induced transport.

### Orbital Rules
- Nearer to the attractor does not merely mean visually central; it means stronger coupling to identity and lower permissible distortion.
- Orbit placement must be justified by semantic mass, role, attractor coupling, evidence centrality, and subjective time scale.
- Geodesics represent dependency, provenance, tension, or active relational coupling.
- Precession is allowed and expected under nontrivial coupling, conflict, or gradient structure.
- Every stable orbit must have an explanation in terms of the system potential, not only in terms of UX convenience.

### Mode Structure
- **Internal Plus Embedding**: Each sphere should eventually support an internal mode structure plus an embedding/leak channel, so that a local closure residue can seed a higher-level sphere.
- **Design Implication**: No layer is absolutely closed; every layer must be able to embed upward without destroying its local identity.

## 4. Attractors and Dynamics

### Attractor Types
- **Euler-Collatz Identity Attractor (A_EC)**: Iterative-topological identity generator: closure rhythm, parity structure, discrete transition topology, seed regularity.
- **Zeta-Schrödinger Identity Attractor (A_ZS)**: Spectral-resonant identity generator: modal stability, resonance basins, spectral weighting, standing-mode selection.
- **Temporary LLM Attractor (A_LLM_temp)**: External bootstrap and fallback operator used only while internal autonomy is insufficient.

### Control Law
`alpha_ec + alpha_zs + alpha_llm = 1, with alpha_llm decreasing over time and alpha_ec/alpha_zs becoming dominant.`

### Total Potential
- **Formula:** `V_total = V_EC + V_ZS + V_rel + V_mem + V_def + V_ext`
  - **V_EC**: Iterative-topological closure potential
  - **V_ZS**: Spectral-resonant potential
  - **V_rel**: Relational coherence / truth alignment / semantic distance potential
  - **V_mem**: Memory stabilization and consolidation cost
  - **V_def**: Defect, drift, and inconsistency cost
  - **V_ext**: External forcing from user input, files, environment, or temporary external operators

### ROOR / OORP Pipeline
- **Name:** Relational-Orbital Orchestrated Reduction Pipeline (ROOR / OORP)
- **Sequence:**
  - Relation layer
  - Identity layer
  - Orchestration layer
  - Reduction layer
  - Memory update layer
- **Meaning:**
  - A relational configuration is formed first.
  - A local identity attractor emerges from that relation.
  - Couplings synchronize compatible trajectories and suppress incompatible ones.
  - When a metastability threshold is crossed, a discrete reduction event occurs.
  - Only then is memory updated.

### Dynamic Variables
- **Orbital Entity State**:
  - amplitude
  - phase
  - coherence
  - polarity_or_truth_spin
  - memory_affinity
  - semantic_mass
  - subjective_time_scale
  - orbit_index
  - sphere_id
  - parent_sphere_id
  - winding_components
- **Coupling Matrix**: K_ij(t) controls amplitude flow, phase synchronization, local amplification/damping, and emergence of collective modes.
- **Reduction Threshold**: Gamma(Psi) >= Gamma_crit
- **Reduction Terms**:
  - coherence
  - contradiction tension
  - cost of keeping superposition unresolved
  - alignment with truth axis
  - relational stability

## 5. Identity and Registry

**Principle:** Every important system object must become a first-class dynamic entity.

### Entity Types
- file
- module
- operator
- memory fragment
- process
- session
- artifact
- model
- evidence source
- contract
- postulate
- axiom
- cluster
- sphere

### Entity Record
#### Required Fields
- canonical_id
- object_type
- source_path
- sector
- sphere_id
- parent_sphere_id
- orbit_index
- phase
- winding_number
- winding_components
- relation_depth
- revision_index
- epistemic_status
- provenance_links
- dependency_links
- activity_state
- semantic_mass
- subjective_time_scale
- attractor_weights
- leak_mode
#### Notes
- A file is not only a filesystem object; it is a dynamic orbital entity.
- No orbit assignment may be arbitrary. Every placement must be explainable by the assignment operator.

### Assignment Operator
- **Formula**: `file -> seed_vector -> semantic_mass -> subjective_time -> orbit -> winding_seed -> sphere_embedding`
- **Inputs**:
  - definitions and ontology role
  - dependency centrality
  - provenance centrality
  - truth/evidence centrality
  - runtime criticality
  - attractor coupling
  - seed class
- **Outputs**:
  - sector
  - semantic mass
  - effective attractor weight
  - orbit index
  - subjective time scale
  - initial winding components
  - sphere embedding

## 6. Time and Winding

**Principle:** Winding number must arise from process topology and subjective time, not from decorative tagging.

### Subjective Time
- **Definition**: Each entity must have a local subjective time scale influenced by attractor distance, semantic mass, coherence, defect, and activity.
- **Design Rule**: Entities near the attractor and entities far from it must not share the same subjective temporal profile.

### Winding
- **Definition**: Winding is accumulated phase motion normalized by local subjective time and decomposed by source.
- **Components**:
  - winding_ec
  - winding_zs
  - winding_relational
  - winding_reduction
- **Design Rule**: Winding is part of identity and history. It must survive beyond one frame or one session.

## 7. Product Architecture

### Layers
- **Kernel Layer**: Formal state, phase operators, closure operators, truth/defect operators, memory-state transitions, autonomy policy primitives.
- **Entity & Identity Registry**: Persistent identity of all dynamic entities, orbital assignment, provenance, dependency, epistemic state.
- **Autonomy Layer**: Manage transition from external LLM dependence to internal CIEL autonomy.
- **Geometry Engine**: Map system state to Poincaré disk coordinates, orbital motion, precession, tension lines, transitions, and focus states.
- **Native Surface**: Render the operational chart and inspectors as a native desktop UI.
- **Runtime Services**: Model adapters, local storage, watchers, export/import, diagnostics, crash recovery, telemetry, task orchestration.

### Recommended Stack
- **Backend**: Python
- **Native Ui**: PySide6 / Qt Quick / QML
- **Reasoning**:
  - The system is already Python-oriented at the kernel level.
  - Qt Quick supports a true native desktop surface with canvas, state transitions, animation, and inspectors.
  - The target is a standalone application, not a browser shell.

### UI Principles
- The UI must visualize the real state of the system, not a fake cockpit metaphor.
- The main surface must be orbital and continuous, not tab-teleport based.
- Every visual element must correspond to a tracked entity, coupling, attractor, event, or metric.
- Debug mode and product mode must share the same underlying geometry, differing only in density and exposure.

## 8. Implementation Plan

### Stage 0 — Canonical Vocabulary and Observables
- **Why:** No architecture is stable until the core terms are fixed.
- **What:**
  - Define the canonical vocabulary of entities, observables, operators, and layers.
  - Separate state, observable, operator, event, and visualization concepts.
- **Deliverables:**
  - 00_ONTOLOGY.md
  - 01_OBSERVABLES.md
  - system_types specification
- **Outcomes:**
  - A non-ambiguous language for the project
  - A clean basis for later data models

### Stage 1 — State Space and Boundary Conditions
- **Why:** The system cannot be simulated or visualized before its space and boundaries are defined.
- **What:**
  - Define the relational state space.
  - Define poles, axis, attractor, outer boundary, leak channels, and sphere embeddings.
  - Define which parts are formal space and which parts are operational charts.
- **Deliverables:**
  - 02_STATE_SPACE.md
  - 03_BOUNDARY_CONDITIONS.md
- **Outcomes:**
  - A precise answer to where the system lives
  - A basis for geometry and dynamics

### Stage 2 — Invariants, Constraints, and Conservation Rules
- **Why:** Potential and motion require known invariants and costs.
- **What:**
  - Formalize Euler closure, holonomic defect, truth scalar, distortion terms, and minimum-distortion attractor conditions.
  - State which quantities are conserved, minimized, or thresholded.
- **Deliverables:**
  - 04_INVARIANTS.md
  - 05_CONSTRAINTS.md
- **Outcomes:**
  - Measurable dynamic targets
  - Formal criteria for valid state evolution

### Stage 3 — Attractors and Potential Field
- **Why:** Orbit placement and dynamics require explicit source terms.
- **What:**
  - Define A_EC, A_ZS, and A_LLM_temp.
  - Define V_total and its term structure.
  - Define the control law for autonomy transition.
- **Deliverables:**
  - 06_ATTRACTORS.md
  - 07_POTENTIAL_FIELD.md
- **Outcomes:**
  - A source model for orbital dynamics
  - A basis for semantic mass and subjective time

### Stage 4 — Entity Registry and Orbital Assignment
- **Why:** Files and artifacts must become dynamic entities before any real cockpit can exist.
- **What:**
  - Define EntityRecord.
  - Design the assignment operator.
  - Design initial sector and sphere classification.
  - Define provenance and dependency graphs.
- **Deliverables:**
  - 08_REGISTRY.md
  - 09_ASSIGNMENT_OPERATOR.md
- **Outcomes:**
  - A full mapping from artifacts to orbital entities
  - An identity-bearing system graph

### Stage 5 — Subjective Time and Winding
- **Why:** Identity is not complete until each entity has a time profile and topological history.
- **What:**
  - Define subjective time operator.
  - Define winding decomposition.
  - Connect winding to reduction events and attractor coupling.
- **Deliverables:**
  - 10_TIME_AND_WINDING.md
- **Outcomes:**
  - A non-decorative winding model
  - Temporal-topological identity for entities

### Stage 6 — Orchestration and Reduction
- **Why:** The system must move from possibility structure to discrete stabilization.
- **What:**
  - Define orchestration couplings.
  - Define thresholded reduction operators.
  - Define memory update after reduction.
  - Define variants of reduction policy.
- **Deliverables:**
  - 11_OORP.md
- **Outcomes:**
  - A full relational-orbital processing pipeline
  - A memory model grounded in reduction

### Stage 7 — Simulation Engine
- **Why:** The design must be testable before graphics.
- **What:**
  - Build a non-UI state simulator.
  - Run orbital assignment checks, reduction events, memory updates, and attractor transitions.
  - Log state traces and metrics.
- **Deliverables:**
  - 12_SIMULATION_PLAN.md
- **Outcomes:**
  - A falsifiable backend model
  - Evidence that geometry reflects real state

### Stage 8 — Geometry Engine
- **Why:** Only after the simulator exists should state be projected into an operational chart.
- **What:**
  - Map entities and couplings onto the Poincaré disk.
  - Define geodesics, tension zones, focus states, transition trajectories, and precession rules.
- **Deliverables:**
  - 13_GEOMETRY_ENGINE.md
- **Outcomes:**
  - A state-projection engine suitable for native rendering
  - A coherent visual grammar

### Stage 9 — Native Cockpit MVP
- **Why:** The product surface comes last, not first.
- **What:**
  - Build the first native orbital surface.
  - Implement inspectors, evidence panels, session panel, memory panel, boundary/publish panel, and event strip.
- **Deliverables:**
  - 14_NATIVE_SURFACE.md
- **Outcomes:**
  - A real standalone application shell
  - A usable first orbital product

### Stage 10 — Autonomy Hardening and Productization
- **Why:** A product must eventually stand on its own operators, packaging, and reliability.
- **What:**
  - Reduce LLM dependency.
  - Add crash recovery, packaging, release discipline, regression tests, and install diagnostics.
- **Deliverables:**
  - 15_PRODUCTIZATION.md
- **Outcomes:**
  - A stable MVP-to-release path
  - A measurable path toward CIEL-centered autonomy

## 9. Metrics

### Core Metrics
- **closure_defect**: Magnitude of failure to satisfy the active closure/coherence condition.
- **truth_alignment**: Operational truth scalar / evidence consistency score.
- **semantic_mass_stability**: Stability of semantic mass under normal updates.
- **orbit_assignment_consistency**: How often the assignment operator gives stable placements under repeated evaluation.
- **reduction_validity_rate**: Fraction of reduction events that satisfy defined thresholds and postconditions.
- **memory_after_reduction_consistency**: Whether memory updates match the selected reduced state and local identity attractor.
- **cross_sphere_embedding_integrity**: Whether local-to-parent sphere embedding remains coherent and traceable.
- **llm_dependency_ratio**: Relative proportion of responses or state updates that still require external LLM support.

### Product Metrics
- **cold_start_time_s**
  - **Target Mvp**: < 4 s
  - **Target Release**: < 2.5 s
- **idle_memory_mb**
  - **Target Mvp**: < 500 MB
- **session_crash_free_rate**
  - **Target Release**: >= 0.99
- **packaged_install_success_rate**
  - **Target Release**: >= 0.95

## 10. Risks

- **Premature UI-first development**: Beautiful motion without grounded system dynamics.
- **Registry-free geometry**: Visual entities without justified identity, orbit, or mass.
- **Permanent hidden LLM centrality**: CIEL never becomes its own operational center.
- **Decorative winding number**: Loss of topological meaning and architectural trust.
- **Geometry without metrics**: The system turns into a visual effect rather than a measurable state machine.
- **Mixing ontology with projection**: Confusion between formal state space and operational chart.

## 11. Working Rules

- Keep this planning pack outside existing repositories until the new project scaffold is intentionally created.
- Treat Markdown as the canonical human-readable plan.
- Treat YAML as the canonical machine-readable mirror of the same structure.
- Any new future document should preserve the same vocabulary and section ordering where possible.
- Any later implementation repo should begin from these documents rather than by copying old runtime shells.

## 12. Immediate Next Action

**Recommendation:** Start by refining Stage 0 and Stage 1 into exact schemas and definitions before any code or UI work begins.

### First Three Documents To Write Next
- 00_ONTOLOGY.md
- 02_STATE_SPACE.md
- 03_BOUNDARY_CONDITIONS.md
