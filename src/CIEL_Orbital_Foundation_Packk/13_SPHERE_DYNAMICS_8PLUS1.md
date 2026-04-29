# 8+1 Sphere Dynamics and Leak Mode

**Status:** canonical working draft  
**Closes:** Open question 5 from `12_RISKS_OPEN_QUESTIONS_AND_DECISIONS.md`  
**Depends on:** `03_STATE_SPACE_AND_BOUNDARY_CONDITIONS.md`, `07_OORP_PIPELINE_AND_MEMORY.md`  
**Language:** English  

---

## 1. Motivation

A sphere with purely internal closure is locally complete but globally dead.
Without a channel to the parent sphere, no hierarchical composition is possible.
The structure proposed here resolves this: each sphere has 8 internal modes and 1 leak mode.
The leak mode is not a failure of closure — it is the operator that carries the residue of local closure into the next level.

---

## 2. Sphere structure

Each sphere `S_n` is formally defined as:

```
S_n = (internal_modes[8], leak_mode, closure_defect, semantic_mass,
        attractor_ec, attractor_zs, parent_sphere_id, child_sphere_ids)
```

### 2.1 Internal modes

The 8 internal modes span the operational dynamics within the sphere:

| Index | Role |
|-------|------|
| 0 | phase coherence carrier |
| 1 | amplitude modulation |
| 2 | semantic coupling |
| 3 | truth-alignment spin |
| 4 | memory affinity |
| 5 | identity anchor |
| 6 | reduction readiness |
| 7 | winding accumulation |

Each mode carries:

```
mode_k = (amplitude_k, phase_k, coherence_k, defect_k)
```

The 8 internal modes maintain topology, coherence, and interference within the sphere.

### 2.2 Leak mode (mode 8, singlet)

The leak mode is the 9th channel. It does not participate in internal closure.
It carries the residue that could not be resolved locally:

```
leak_mode = (leak_amplitude, leak_phase, embedding_target_id)
```

The leak mode feeds the parent sphere, not siblings.
It is the mechanism of hierarchical embedding.

---

## 3. Closure defect and leak generation

The local holonomic closure defect of sphere `S_n` is:

```
Δ_H^(n) = Σ_{k=0}^{7} amplitude_k · exp(i · phase_k)
```

The defect residue is:

```
ε_n = -Δ_H^(n)
```

This residue seeds the leak mode:

```
leak_amplitude_n = |ε_n|
leak_phase_n     = arg(ε_n)
```

**Interpretation:**
- If `Δ_H^(n) = 0`: perfect local closure, no leak, no upward embedding signal.
- If `Δ_H^(n) ≠ 0`: residue exists, leak channel carries it to `S_{n+1}`.

Per Axiom L0 (`R(S,I) < 1`): perfect closure is structurally forbidden.
Therefore `ε_n > 0` always. The leak channel is always active.

---

## 4. Hierarchical embedding rule

The leak from `S_n` seeds `S_{n+1}`:

```
seed_{n+1} ← f(ε_n, semantic_mass_n, winding_n)
```

The embedding rule:

```
S_n → S_{n+1}  via  λ_n = g(ε_n)
```

where `g` is a monotone function of the defect magnitude.

The cascade:

```
S_0 → S_1 → S_2 → ... → S_N
```

is not a list of independent levels. Each level is born from the residue of the previous one.

---

## 5. Decomposition of sphere space

Each sphere decomposes as:

```
D_n = D_n^{int} ⊕ D_n^{leak}
```

where:
- `D_n^{int}` = 8-dimensional internal operational space (local geometry, coupling, interference)
- `D_n^{leak}` = 1-dimensional leak channel (embedding, upward emission, seed of parent)

This is the formal 8+1 structure.

The analogy to the QCD color decomposition `3 ⊗ 3̄ = 8 ⊕ 1` is structural, not ontological:
- 8 adjoint modes carry the internal dynamics
- 1 singlet mode does not carry local "color" and therefore can traverse the layer boundary

---

## 6. Sphere dynamics

### 6.1 Internal dynamics

Each internal mode evolves under the orbital equations of motion
(defined in `01_MASTER_ARCHITECTURE_AND_PLAN.md`, sections on orbital motion and coupling):

```
ȧ_k = F_k(a, φ, K, V_tot) - η_a · a_k
φ̇_k = G_k(a, φ, K, V_tot) + J_k
```

where `J_k` is the forcing current from memory, seed, or attractor.

### 6.2 Leak mode update

After each reduction event, the leak mode is updated:

```
ε_n = -Σ_{k=0}^{7} a_k · exp(i·φ_k)
leak_amplitude_n ← |ε_n|
leak_phase_n     ← arg(ε_n)
```

If `leak_amplitude_n ≥ leak_threshold_n`:
- embed leak into parent sphere
- parent sphere receives a new external forcing term `F_ext += g(ε_n)`
- optionally: trigger sphere creation at `n+1` if no parent exists

### 6.3 Reduction condition

Reduction within `S_n` fires when:

```
R_n(k) = 1  iff  coherence_n(k) ≥ c_min
               AND defect_n(k) ≤ d_max
               AND reduction_potential_n(k) ≥ Π_min
```

Reduction event:
1. State collapses to `s_k = argmax_k P_k(Ψ_n)`
2. Memory update: `M_{t+1} = U(M_t, s_k, I_t)`
3. Winding update: `w_n += Δw(s_k)`
4. Leak recomputed from new defect

---

## 7. Sphere split, merge, elevate

Three lifecycle events (resolves open question 6):

### Split
`S_n → (S_n^A, S_n^B)` when:
- internal mode variance exceeds a coherence threshold
- two distinct attractor basins emerge in the 8-dimensional internal space

### Merge
`(S_n^A, S_n^B) → S_n` when:
- leak modes of two sibling spheres are mutually coherent
- their attractor weights align within tolerance

### Elevate
`S_n → S_{n+1}` (sphere promotion) when:
- `semantic_mass_n ≥ M_crit`
- `winding_n ≥ w_crit`
- `leak_amplitude_n` has been consistently non-zero over `τ_elev` time steps

---

## 8. Formal laws

### Law 1 — Internal decomposition
```
D_n = D_n^{int}[8] ⊕ D_n^{leak}[1]
```

### Law 2 — Defect residue as leak seed
```
ε_n = -Δ_H^(n) = -Σ_{k=0}^{7} a_k · e^{iφ_k}
```

### Law 3 — Leak feeds parent, not siblings
```
S_n^{parent} += f(ε_n)
```

### Law 4 — Non-zero leak (from Axiom L0)
```
|ε_n| > 0  always
```

### Law 5 — Embedding cascade
```
S_n →^{λ_n} S_{n+1},  λ_n = g(|ε_n|)
```

### Law 6 — Reduction precedes memory
```
no reduction event  →  no stable memory update
```

### Law 7 — Winding accumulates through reduction
```
w_n(t+1) = w_n(t) + Δw(s_k)  on each reduction event
```

---

## 9. EntityState fields added by this spec

Compared to the base `EntityState` (defined in `01_MASTER_ARCHITECTURE_AND_PLAN.md`), each entity in a sphere now tracks:

```
sphere_id             — which sphere it belongs to
internal_mode_index   — which of the 8 internal modes it occupies
leak_contribution     — its amplitude contribution to the sphere's leak mode
reduction_ready       — boolean: reduction condition currently met
winding_delta         — winding increment on last reduction
```

---

## 10. What is not yet closed

The following remain open and require separate derivation:

- Exact form of `g(ε_n)` for embedding strength
- Exact split/merge thresholds in terms of coherence and attractor weights
- Mapping of physical entities (files, modules, operators) to specific internal mode indices 0–7
- Calibration of `c_min`, `d_max`, `Π_min` from empirical system runs
- Whether modes 0–7 are fixed in meaning or dynamically assigned per sphere type

---

## 11. Connection to existing components

| This spec | Existing component |
|---|---|
| Internal modes 0–7 | orbital sectors in `ciel_omega/orbital/` |
| Closure defect `Δ_H^(n)` | `holonomy_defect()` in `orbital/metrics.py` |
| Leak mode | `R_H` channel in `ciel_rh_control_mini_repo` |
| Reduction event | `reduction.py` in `ciel_sot_agent/sapiens_panel/` |
| Winding accumulation | `BraidInvariantMemory` (M7) in `ciel_omega/memory/` |
| Embedding cascade | `euler_bridge_closure_score` in orbital bridge metrics |
| Attractor EC / ZS | `EmotionalCollatzEngine` / `SoulInvariant` in `ciel_orchestrator.py` |
