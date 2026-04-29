# Ontology and Observables

## Purpose

This document freezes the canonical vocabulary of the new project. Nothing else should be implemented before these definitions are stable.

## Primary object classes

### Entity
A persistent system object with identity, location in the orbital model, provenance, and dynamic state.

### State
A structured snapshot of the system at a discrete step. A state is not a UI frame; it is the formal object from which simulation and rendering are derived.

### Observable
A quantity that can be computed from the state and used for validation, routing, or reduction. Examples:
- closure defect
- truth scalar
- global coherence
- semantic mass
- orbit index
- winding
- subjective time scale

### Attractor
A structured basin of convergence that shapes state evolution.
Required attractor classes:
- AttractorEC
- AttractorZS
- AttractorLLMTemp

### Orbit
A stable or metastable trajectory class around an attractor inside a sphere.

### Sphere
A local state container embedded inside a larger state container.
Every sphere has:
- internal modes
- leak / embedding mode
- parent sphere reference or null
- child sphere references

### Leak mode
A non-local embedding channel that carries unresolved closure, surplus coherence, or structural residue into a parent sphere.

### Reduction event
A discrete selection act that maps a metastable multi-orbital state to a selected state and updates memory.

## Required data structures

### EntityRecord
Required fields:
- canonical_id
- object_type
- source_path
- sector
- sphere_id
- parent_sphere_id
- orbit_index
- phase
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

### SystemState
Required fields:
- tick
- global_phase_set
- euler_constraint_state
- holonomic_defect
- truth_scalar
- active_spheres
- active_entities
- attractor_field
- reduction_readiness
- memory_state
- autonomy_state
- geometry_projection_state

## Observables to compute first

- closure_defect
- truth_scalar
- global_coherence
- semantic_mass_per_entity
- effective_attractor_weight_per_sphere
- subjective_time_scale_per_entity
- winding_per_entity
- reduction_readiness
- llm_dependency_ratio

## Non-negotiable distinctions

Do not mix:
- formal state vs rendered view
- sphere vs orbit
- attractor vs entity
- semantic mass vs file size or code length
- winding vs revision count
- memory vs raw storage
