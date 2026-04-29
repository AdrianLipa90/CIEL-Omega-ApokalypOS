# Toy-Model White-Thread Matrix F_ij — Next Steps Pipeline

This repository extends the toy-model F_ij computation for the 12 Standard Model fermions on a Kähler sphere (S²) into a full exploratory pipeline including:

1. **β-Calibration**: Fit global scale factor β to match experimental F_i from PDG.
2. **Berry Monopole Holonomy**: Introduce monopole Berry connection A on S² for true topological holonomy.
3. **Extension to Hadron/ Meson F_ij**: Compute baryon and meson topological factors based on quark F_ij.

---

## Module 1: β-Calibration

**Purpose:** Scale the toy-model F_ij matrix so that it aligns with experimental amplitudes F_i.

**Approach:**

- Compute directional F_ij: `F_ij = exp(β*(θ_j - θ_i))`.
- Define a loss function comparing column averages or row sums with experimental F_i.
- Use optimization (e.g., `scipy.optimize.minimize`) to find β_opt that minimizes the discrepancy.

**Input:**

- θ_i: cycle angles for 12 fermions
- F_exp: experimental F_i values
- Initial I₀ guess

**Output:**

- Optimized F_ij matrix (`F_calibrated.csv`)
- Optimal β value

---

## Module 2: Berry Monopole Holonomy

**Purpose:** Replace simple Δθ differences with **true Berry monopole holonomy**, capturing the geometric phase of cycles on S².

**Key Components:**

- Spherical coordinates (θ, φ) for each fermion cycle
- Monopole Dirac field: `A_phi = g * (1 - cos θ)`  
- Approximate path integrals: `W_ij = exp(i ∮ A · dl)`

**Variants:**

- Directional: `F_ij = exp(I₀ * Re(log(W_ij)))`  
- Symmetric: `F_ij = |W_ij|` or other symmetrization

**Output:**

- Holonomy-based F_ij matrices (`F_holonomy_directional.csv`, `F_holonomy_sym.csv`)
- Heatmaps for visual inspection of topological effects

---

## Module 3: Extend to Full SM — Baryons & Mesons

**Purpose:** Generate composite F_ij for hadrons based on quark-level F_ij.

**Baryons:**

- Composed of three quarks `(q1, q2, q3)`
- Compute geometric mean of pairwise F_ij:  
  `F_baryon = (F_q1q2 * F_q1q3 * F_q2q3)^(2/3)`

**Mesons:**

- Composed of quark-antiquark pair `(q1, anti-q2)`
- F_meson = F_q1q2

**Output:**

- F_ij matrices for baryons/mesons (`F_baryons.csv`, `F_mesons.csv`)
- Block statistics for generational hierarchies
- Heatmaps and top deviations

---

## Workflow

1. **Step 1:** Run β-calibration to obtain realistic F_ij for fermions.
2. **Step 2:** Replace Δθ with Berry monopole holonomy for topologically accurate matrices.
3. **Step 3:** Extend F_ij to hadrons and mesons for full SM analysis.
4. **Step 4:** Generate CSVs, heatmaps, block statistics, and top deviation lists for interpretation.

---

## Requirements

- Python 3.x
- Packages: `numpy`, `scipy`, `pandas`, `matplotlib`

---

## References

- [Geometria.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/155418183/03175cba-a283-42d4-9c03-d044bb64cda0/Geometria.txt)  
- [Formal_SM.pdf](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_2b2a0a80-47ee-4fba-b46c-ac83141a80a7/3fbac86f-c599-4c88-9086-0b0b750d539f/Formal_SM.pdf)  
- [White_threads.pdf](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_2b2a0a80-47ee-4fba-b46c-ac83141a80a7/b37e2e2a-74a2-4dbd-bb4f-28aaef49f38d/White_threads.pdf)

---

## Next Steps

- Calibrate β using PDG F_i for u/d/s quarks and neutrinos.  
- Implement full monopole Berry connection along chosen paths on S².  
- Extend analysis to full SM baryons and mesons for generational topology studies.

