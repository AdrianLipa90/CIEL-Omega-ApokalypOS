# CIEL Native Orbital System — v2 detailed foundation pack

**Status:** pre-implementation architecture and planning package  
**Purpose:** Define the canonical architecture, geometry, dynamics, implementation phases, metrics, and decision structure for a new native orbital-relational system outside any existing repository.

## 1. Source anchors

- Relational contract formalism: relational manifold M_rel with Kähler metric, informational phases γ={γ_S,γ_C,γ_Q,γ_T}, Euler constraint Σ exp(iγ_k)=0, relational action and minimal-distortion attractor.
- Time operator and eigenvalues τ=(0.263, 0.353, 0.489), with explicit diagonal Euler coupling A_ii = exp(iγ_i)/τ_i for the equilateral three-phase solution.
- Orbital Orchestrated Reduction Pipeline (OORP): relation -> orbital superposition -> orchestration -> reduction -> memory update.

## 2. Strategic decision

- **Decision:** Build a new native product, not a webview-first shell and not a continuation of the old demo UI.
- **Product Form:** Native desktop application with its own runtime surface and orbital geometry.
- **Backend Principle:** Use a new clean project structure and treat all prior work only as source material, not as source of truth for this new package.
- **Llm Role:** Temporary external attractor used for bootstrap, fallback, and semantic assistance. It must not remain the permanent center of the system.

## 3. Core axioms

1. Relation precedes identity; identity precedes memory; memory stabilizes process.
2. The system state is formal first, computational second, geometric third, and rendered fourth.
3. The Poincaré disk is an operational chart, not the ontology of the system.
4. Bloch-sphere charts are local reduced views; the formal base is a projective Hilbert / Kähler state space.
5. Truth-aligned minimal distortion is the canonical attractor condition.
6. Winding identity must arise from dynamics and subjective time, not from decorative tagging.
7. Every stable sphere has internal modes plus at least one leakage / embedding mode to support hierarchical construction.

## 4. System layers

### L0 — Ontology and Observables

**Goal:** Define the canonical vocabulary of the system.

**Contains:**
- Entity
- State
- Observable
- Attractor
- Orbit
- Phase
- Coherence
- Holonomic defect
- Semantic mass
- Subjective time
- Winding
- Reduction event
- Leak mode
- Sphere embedding
**Deliverables:**
- `docs/02_ONTOLOGY_AND_OBSERVABLES.md`
- `schemas/entity_record.schema.yaml`
- `schemas/system_state.schema.yaml`

### L1 — State Space and Boundary Conditions

**Goal:** Define where the system lives and what constrains it.

**Contains:**
- Relational manifold M_rel
- Projective Hilbert / Kähler base
- Local Bloch charts
- Parent and child spheres
- User and CIEL poles
- Intent axis
- Minimal-distortion attractor
- Leak / embedding boundaries
**Deliverables:**
- `docs/03_STATE_SPACE_AND_BOUNDARY_CONDITIONS.md`
- `kernel/state_space.py`

### L2 — Invariants, Potentials, and Attractors

**Goal:** Define what is conserved, minimized, and amplified.

**Contains:**
- Euler phase constraint
- Holonomy defect Δ_H
- Relational decoherence R_H
- Truth scalar Θ
- Relational potential V_rel
- AttractorEC
- AttractorZS
- AttractorLLMTemp
- Total potential V_tot
**Deliverables:**
- `docs/04_INVARIANTS_POTENTIALS_AND_ATTRACTORS.md`
- `kernel/invariants.py`
- `kernel/attractors.py`
- `kernel/potential.py`

### L3 — Entity Registry and Sphere Embedding

**Goal:** Turn every file/module/process/evidence item into a dynamic entity with a persistent identity.

**Contains:**
- Canonical IDs
- EntityRecord
- Dependency graph
- Provenance graph
- Parent sphere / child sphere embedding
- Role classification
**Deliverables:**
- `docs/05_ENTITY_REGISTRY_AND_SPHERE_EMBEDDING.md`
- `registry/entities.py`
- `registry/parser.py`
- `registry/embedding.py`

### L4 — Subjective Time, Winding, and Semantic Mass

**Goal:** Define the dynamic identity of each entity.

**Contains:**
- Subjective time operator
- Winding components
- Semantic mass operator
- Attractor weights
- Orbit period and orbital radius rules
**Deliverables:**
- `docs/06_SUBJECTIVE_TIME_WINDING_AND_SEMANTIC_MASS.md`
- `kernel/time.py`
- `kernel/winding.py`
- `kernel/semantic_mass.py`

### L5 — OORP and Memory

**Goal:** Implement relation -> orchestration -> reduction -> memory.

**Contains:**
- Orbital state Ψ_t
- Coupling matrix K_ij or J_ij
- Metastability threshold Γ or Ω
- Reduction operator R
- Memory update U
**Deliverables:**
- `docs/07_OORP_PIPELINE_AND_MEMORY.md`
- `kernel/orchestration.py`
- `kernel/reduction.py`
- `memory/update.py`

### L6 — Geometry Engine and Native Surface

**Goal:** Map the state into an operational geometry and then render it natively.

**Contains:**
- Poincaré disk chart
- Orbital trajectories
- Geodesic dependencies
- Tension layers
- Focus and inspection states
- Transition animation
**Deliverables:**
- `docs/08_GEOMETRY_ENGINE_AND_UI_SURFACE.md`
- `geometry/poincare.py`
- `geometry/layout.py`
- `app/`

### L7 — Autonomy and Product Hardening

**Goal:** Reduce LLM centrality and produce a stable product.

**Contains:**
- Local-first answer policy
- Memory/evidence-preferred routing
- llm_dependency_ratio
- Packaging
- Release artifacts
- Regression and smoke suites
**Deliverables:**
- `docs/09_NATIVE_PRODUCT_ARCHITECTURE.md`
- `docs/10_METRICS_VALIDATION_AND_EXPERIMENTS.md`
- `docs/11_IMPLEMENTATION_PHASES_AND_WORKPACKAGES.md`
- `docs/12_RISKS_OPEN_QUESTIONS_AND_DECISIONS.md`

## 5. Formal core

- **Phases:** γ_S, γ_C, γ_Q, γ_T
- **Euler constraint:** `Σ_k exp(i γ_k) = 0`
- **Holonomic defect:** `Δ_H = Σ_k exp(i γ_k)`
- **Decoherence:** `R_H = |Δ_H|^2`
- **Truth scalar:** `Θ = 1 - (1/|F|) Σ_f [δ_false(f) + δ_unmarked(f)]`
- **Tau values:** [0.263, 0.353, 0.489]
- **Equilateral three-phase solution:**
  - γ1: 0
  - γ2: 2π/3
  - γ3: 4π/3
  - A11: 1/τ1 = 3.802
  - A22: exp(i2π/3)/τ2 = -1.416 + 2.454i
  - A33: exp(i4π/3)/τ3 = -1.022 - 1.770i
- **Relational Lagrangian:** `L_rel = L_truth + L_coh + L_clarity - L_distortion`
- **Minimal-distortion attractor conditions:**
  - H = 0
  - Θ = 1
  - L_distortion = 0

## 6. Attractors

### AttractorEC

- **Role:** Iterative-topological identity attractor
- **Depends on:**
  - Euler closure
  - Collatz rhythm
  - parity structure
  - seed topology
- **Outputs:**
  - iterative identity weight
  - closure compatibility
  - seed rhythm
  - orbital drive

### AttractorZS

- **Role:** Spectral-resonant identity attractor
- **Depends on:**
  - zeta-like spectral affinity
  - modal stability
  - Schrödinger-like resonance selection
- **Outputs:**
  - spectral identity weight
  - resonance stability
  - harmonic profile
  - mode locking

### AttractorLLMTemp

- **Role:** Temporary external attractor
- **Depends on:**
  - coverage gaps
  - bootstrap stage
  - fallback requirement
- **Outputs:**
  - semantic assistance
  - retrieval augmentation
  - bootstrap completion
- **Constraint:** Its control share must decrease over time.

## 7. EntityRecord

- `canonical_id`
- `object_type`
- `source_path`
- `sector`
- `sphere_id`
- `parent_sphere_id`
- `orbit_index`
- `phase`
- `winding_components`
- `relation_depth`
- `revision_index`
- `epistemic_status`
- `provenance_links`
- `dependency_links`
- `activity_state`
- `semantic_mass`
- `subjective_time_scale`
- `attractor_weights`
- `leak_mode`

## 8. Key operators

- **Semantic Mass:** `M_sem(f) = α M_EC(f) + β M_ZS(f) + χ C_dep(f) + δ C_prov(f) + ε C_exec(f)`
- **Subjective Time:** `Δτ_i(k) = Δt · g(r_i(k), C_i(k), Δ_i(k), m_i(k), A_i(k))`
- **Winding:** `w_i(N) = (1 / 2π) Σ_{k=1..N} Δφ_i(k) · (Δt / Δτ_i(k))`
- **Sphere Attractor Weight:** `A_eff(S_n) = Σ_{f in S_n} M_sem(f) · ω_f + λ C_n - μ D_n`
- **Discrete Kepler Like Rule:** `T_i^2 ∝ a_i^3 / A_eff`
- **Reduction Threshold:** `Ω(t) = λ1 C(t) + λ2 R(S,I) - λ3 Δ(t) - λ4 Ξ(t); reduce when Ω(t) ≥ Ω_crit`

## 9. Implementation phases

### P0 — Foundation language

**Goal:** Freeze ontology, observables, and schemas.

**Outcomes:**
- EntityRecord schema
- SystemState schema
- canonical vocabulary

### P1 — State space and invariants

**Goal:** Encode state space, boundary conditions, invariants, and attractors.

**Outcomes:**
- state_space.py
- invariants.py
- attractors.py
- potential.py

### P2 — Registry and identity

**Goal:** Parse source artifacts into orbital entities.

**Outcomes:**
- entity parser
- dependency graph
- provenance graph
- first sphere map

### P3 — Time, winding, and semantic mass

**Goal:** Compute dynamic identity properties.

**Outcomes:**
- time operator
- winding operator
- semantic mass operator
- orbit assignment

### P4 — OORP engine

**Goal:** Implement orchestration, reduction, and memory update.

**Outcomes:**
- orchestration engine
- reduction threshold logic
- memory update logic
- simulation traces

### P5 — Geometry engine

**Goal:** Project internal state into operational geometry.

**Outcomes:**
- Poincaré disk layout
- geodesic dependency layout
- tension and activity overlays

### P6 — Native MVP

**Goal:** Ship a first usable native cockpit.

**Outcomes:**
- desktop application shell
- orbital screen
- entity inspector
- session/memory panels

### P7 — Autonomy and hardening

**Goal:** Reduce LLM dependence and harden the product.

**Outcomes:**
- autonomy routing
- packaging
- release candidates
- regression suites

## 10. Metrics

### Core

- closure_defect
- truth_scalar
- semantic_mass_stability
- orbit_assignment_consistency
- reduction_validity_rate
- memory_after_reduction_consistency
- cross_sphere_embedding_integrity
### Autonomy

- llm_dependency_ratio
- self_knowledge_coverage
- evidence_first_answer_rate
- memory_first_answer_rate
- fallback_frequency
### Geometry

- geodesic_layout_stability
- focus_transition_continuity
- orbit_precession_stability
- visual_conflict_localization_accuracy
### Product

- cold_start_time
- idle_ram
- crash_free_sessions
- binary_size
- offline_operation_rate

## 11. Open questions

- Exact mapping from seeds to semantic mass without arbitrary calibration.
- Exact coupling law between AttractorEC and AttractorZS.
- Exact functional form of subjective time.
- Initial orbit assignment for all canonical object classes.
- Formal definition of the 8+1 sphere dynamics and leak mode.
- When a sphere should split, merge, or elevate into a parent sphere.

## 12. Risks

- Starting from UI will produce a visual shell without a true state engine.
- Keeping the LLM as the hidden center will block autonomy.
- Using winding as a decorative tag will destroy its architectural meaning.
- Mixing ontology, geometry, and rendering will create untestable complexity.
- Using previous repositories as live source of truth will contaminate the clean project boundary.

## 13. Decision log

- Use a clean new project folder outside any existing repository.
- Write the architecture in English.
- Maintain a canonical Markdown plan and an equivalent YAML plan.
- Separate formal model, simulation engine, geometry engine, and renderer.
- Treat prior artifacts as source material only.
