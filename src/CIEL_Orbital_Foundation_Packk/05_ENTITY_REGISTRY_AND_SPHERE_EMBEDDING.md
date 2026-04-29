# Entity Registry and Sphere Embedding

## Goal

Convert all relevant objects into orbital entities.

## Supported object classes

- file
- module
- operator
- memory
- process
- session
- artifact
- evidence source
- contract / axiom / postulate
- model
- simulation run

## Canonical registry flow

1. scan source material
2. classify object type
3. assign sector
4. assign sphere
5. compute provenance links
6. compute dependency links
7. compute initial semantic mass inputs
8. assign initial orbit band
9. assign initial attractor weights
10. emit EntityRecord

## Sphere embedding model

Each entity belongs to exactly one local sphere at a given time.
Each sphere may belong to one parent sphere.
Promotion rules:
- if leak mode exceeds threshold, emit parent-sphere contribution
- if child sphere stabilizes, merge summary into parent sphere
- if coherence collapses, allow split or demotion

## Initial sectors

Recommended initial sectors:
- axioms_and_contracts
- formal_physics
- attractors_and_potentials
- registry_and_identity
- memory
- evidence_and_provenance
- autonomy
- geometry_engine
- native_surface
- experiments_and_simulations

## Practical identity rule

A file is not the final unit of identity.
A file is the first observable container from which one or more entities may be extracted.
This avoids forcing one file = one ontology item.
