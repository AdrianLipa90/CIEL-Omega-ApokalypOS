# Invariants, Potentials, and Attractors

## Formal anchors

Use the following as canonical anchors:
- Euler phase constraint
- holonomic defect
- truth scalar
- relational Lagrangian
- minimal-distortion attractor

## Invariants and monitored quantities

### Euler phase constraint
`Σ_k exp(i γ_k) = 0`

### Holonomic defect
`Δ_H = Σ_k exp(i γ_k)`

### Relational decoherence
`R_H = |Δ_H|^2`

### Truth scalar
`Θ = 1 - (1/|F|) Σ_f [δ_false(f) + δ_unmarked(f)]`

## Total potential

Use:
`V_tot = V_EC + V_ZS + V_rel + V_mem + V_def + V_ext`

### V_EC
Iterative-topological potential.
Captures:
- closure rhythm
- parity compatibility
- seed regularity
- Collatz / iterative basin structure

### V_ZS
Spectral-resonant potential.
Captures:
- mode locking
- spectral compatibility
- harmonic stability
- resonance basin structure

### V_rel
Relational potential.
Captures:
- coherence with user intent
- internal consistency
- anti-dead-closure information cost
- semantic distortion cost

### V_mem
Memory stabilization potential.
Captures:
- retention pressure
- identity continuity
- consolidation resistance

### V_def
Defect potential.
Captures:
- unresolved contradiction
- semantic drift
- incoherent orbit assignments

### V_ext
External potential.
Captures:
- explicit user forcing
- environment forcing
- temporary LLM bootstrap forcing

## Attractor classes

### AttractorEC
Use for:
- iterative identity
- seed rhythm
- closure structure

### AttractorZS
Use for:
- spectral identity
- resonance profile
- harmonic stabilization

### AttractorLLMTemp
Use only for:
- bootstrap
- fallback
- semantic assistance during early phases

Constraint:
its control share must decay.

## Initial implementation rule

Implement attractors as explicit classes returning:
- compatibility score
- force contribution
- attractor weight
- diagnostic report
