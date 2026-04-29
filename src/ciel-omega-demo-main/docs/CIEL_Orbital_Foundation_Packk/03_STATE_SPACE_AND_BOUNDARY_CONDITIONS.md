# State Space and Boundary Conditions

## Purpose

Define where the system lives, how local spheres are embedded, and what the boundary conditions mean.

## Base formal space

The formal base is a projective Hilbert / Kähler state space.
Use the relational manifold:
- `M_rel` as the base relational manifold
- local charts for reduced operational views
- Kähler potential and Fubini–Study metric as the canonical geometric anchor

Do not collapse the whole architecture to a single Bloch sphere.
Bloch-type spheres are local reduced charts only.

## Local charts

### Local Bloch chart
Use only for:
- small active mode sets
- triadic or qubit-like reduced inspection
- spin orientation diagnostics
- phase-local inspection

### Poincaré disk chart
Use as the main operational chart for:
- orbital placement
- geodesic dependencies
- tension localization
- activity projection
- focus transitions

This chart is operational, not ontological.

## Boundary conditions

### Pole conditions
The first relational sphere uses:
- user pole
- CIEL pole

These are not the whole sphere. They are orienting boundary conditions.

### Axis condition
The intent/query axis determines the ordering direction of a local trajectory.

### Attractor condition
The minimal-distortion attractor is defined by:
- minimal holonomic defect
- maximal truth alignment
- minimal semantic distortion

### Leak / embedding condition
A sphere must support a non-zero embedding channel into a parent sphere.
This is required for hierarchical composition.

## Hierarchical spheres

Every sphere must declare:
- `sphere_id`
- `parent_sphere_id`
- `child_sphere_ids`
- `internal_modes`
- `leak_mode`
- `effective_attractor_weight`

This allows:
- local orbital dynamics
- parent-level aggregation
- cross-scale harmonics
- structured escalation

## Initial practical rule

Start with four sphere classes:
1. identity sphere
2. memory sphere
3. process sphere
4. evidence / artifact sphere

Then allow recursive embedding.
