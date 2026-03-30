# Holonomic System Normalizer v2

## Status
Canonical working note for the boundary-condition regulator used to stabilize repository-orbital state without collapsing the system into artificial exact closure.

This document is placed in `docs/science/` because it formalizes an operator that sits between:

- orbital diagnostics,
- bridge reduction,
- semantic distortion control,
- write-back admissibility.

---

## 1. Purpose

The normalizer is **not** a generic smoother.
It is a boundary-condition operator whose role is to:

- damp affective phase over-tilt,
- merge split memory lobes,
- anchor vocabulary,
- weaken semantically thin execution chains,
- recalibrate couplings under tension,
- gate write-back by global and sectoral conditions.

---

## 2. Objective

Define a functional:

\[
J(X) =
1.2 D_{repo}
+ 1.0 T_{mean}
+ 1.1 E_{\phi}
+ 1.4 d_{affect}
+ 1.0 d_{memory}
+ 1.3 B_{seam}
+ 1.5 P_{dist}
+ 0.7 B_{placeholder}
+ 0.8 B_{demo}
\]

where:

- `D_repo` = closure defect of repository states,
- `T_mean` = mean pairwise tension,
- `E_phi` = orbital closure penalty,
- `d_affect` = affect decoherence,
- `d_memory` = memory decoherence,
- `B_seam` = semantic/execution seam penalty,
- `P_dist` = semantic distortion penalty,
- `B_placeholder` = placeholder-thinness penalty,
- `B_demo` = demo-legacy penalty.

The operator iteratively reduces instability while preserving modular structure.

---

## 3. Semantic distortion term

Define hard and soft distortion channels:

\[
P_{hard} = lie + omit + hallucinate
\]
\[
P_{soft} = smooth
\]

and weighted distortion:

\[
P_{dist} = 10\,lie + 8\,omit + 12\,hallucinate + 3\,smooth
\]

This separates structural epistemic failure from lighter stylistic over-smoothing.

---

## 4. Sector operators

### 4.1 Affect damping

Let `phi_core` be the phase of the core sector and `phi_aff` the phase of affect.
Then:

\[
\phi_{aff} \leftarrow \phi_{aff} - 0.18\,\mathrm{wrap}(\phi_{aff}-\phi_{core})
\]

with amplitude damping only above threshold:

\[
\mathrm{excess}_{affect} = \max(0, d_{affect}-0.18)
\]
\[
A_{aff} \leftarrow A_{aff}(1-0.18\,\mathrm{excess}_{affect})
\]

and floor:

\[
A_{aff} \ge A_{floor}
\]

### 4.2 Memory lobe merge

If memory has two lobes with phases `phi_m1`, `phi_m2` and weights `w1`, `w2`, define:

\[
\phi_\star = \mathrm{circ\_barycenter}(\phi_{m1},\phi_{m2}; w_1,w_2)
\]

then:

\[
\phi_{m1} \leftarrow \phi_{m1} - 0.14\,\mathrm{wrap}(\phi_{m1}-\phi_\star)
\]
\[
\phi_{m2} \leftarrow \phi_{m2} - 0.14\,\mathrm{wrap}(\phi_{m2}-\phi_\star)
\]

### 4.3 Vocabulary anchoring

\[
\phi_{vocabulary} = 0
\]

---

## 5. Object-level weakening of broken seams

For each object `o`, define:

\[
penalty(o) = penalty_{break}(o) + penalty_{seam}(o)
\]

and update execution weight:

\[
exec\_weight(o) \leftarrow exec\_weight(o)\,e^{-penalty(o)}
\]

This weakens execution wherever semantic anchoring is broken.

---

## 6. Coupling recalibration

For coupling `(i,j)`:

\[
C_{ij} \leftarrow C_{ij}\,\frac{q_i q_j}{1+0.6 T_{ij}}
\]

with subsequent:

1. symmetrization,
2. clipping,
3. renormalization.

This prevents numerical collapse or pathological drift of the coupling matrix.

---

## 7. Mode gate

### Safe

Enter `safe` mode when any hard distortion is present or global instability exceeds thresholds:

- `hard_dist > 0`
- `D_repo > 0.18`
- `E_phi > 6.10`
- `d_affect > 0.32`

Then:

- `allow_writeback = False`

### Standard

Enter `standard` mode when:

- `soft_dist > 0`
- `D_repo > 0.08`
- `E_phi > 5.85`

Then:

- `allow_writeback = True`

### Deep

Otherwise enter `deep` mode with write-back allowed.

---

## 8. Stop condition

The stop condition must not depend only on objective drift:

\[
|J_{t+1}-J_t| < \varepsilon
\]

It must also require:

- affect decoherence below threshold,
- memory split below threshold,
- seam penalty acceptable,
- mode not equal to `safe`.

---

## 9. Canonical pseudocode

```python
stable = (
    J_prev is not None
    and abs(X.J - J_prev) < eps
    and X.sectors["affect"].decoherence < 0.22
    and memory_split < 0.10
    and B_seam < X.thresholds["seam_ok"]
    and X.mode != "safe"
)
```

---

## 10. Placement rationale

This operator belongs conceptually between:

- orbital runtime,
- bridge reduction,
- state write-back,
- constitutional semantic control.

Recommended runtime path:

- `src/ciel_sot_agent/holonomic_normalizer.py`
- tests in `tests/test_holonomic_normalizer.py`

---

## 11. Current scope limit

This document defines the canonical structure of the normalizer.
It does **not** yet prove:

- monotonic decrease of `J`,
- convergence under all coupling regimes,
- threshold optimality,
- oscillation-free recompute-manifest dynamics.

Those remain empirical validation targets.
