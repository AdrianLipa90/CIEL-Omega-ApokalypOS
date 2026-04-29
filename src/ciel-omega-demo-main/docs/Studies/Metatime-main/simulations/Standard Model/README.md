# Simulation 1 - Toy Model F_ij Generator for 12 Fermions (S²)

This repository contains a Python implementation to compute and analyze **pairwise topological factors F_ij** for the 12 Standard Model fermions in a simple toy model based on a Kähler sphere (S²). It includes directional and symmetric variants of the F matrix and provides basic statistical and visualization outputs.

---

## Overview

We assign each fermion a “cycle angle” θ_i on S²:

| Fermion | Generation | θ_i (rad) |
|---------|------------|-----------|
| e       | 1          | π/6       |
| μ       | 2          | π/4       |
| τ       | 3          | π/3       |
| u       | 1          | π/8       |
| d       | 1          | π/10      |
| s       | 2          | π/5       |
| c       | 2          | π/2       |
| b       | 3          | 2π/3      |
| t       | 3          | 5π/6      |
| ν1      | 1          | π/12      |
| ν2      | 2          | π/6       |
| ν3      | 3          | π/4       |

The pairwise factors are computed using a small **intention operator**:

\[
I_0 = 0.009
\]

---

## F_ij Variants

1. **Directional** (asymmetric)  
\[
F_{ij} = \exp(I_0 (\theta_j - \theta_i))
\]  
- Shows directionality (“i → j” ≠ “j → i”)  
- Values slightly above or below 1 depending on Δθ  

2. **Symmetrized Absolute Difference**  
\[
F_{ij} = \exp(I_0 |\theta_j - \theta_i|)
\]  
- Always ≥1  
- Removes directional asymmetry  

3. **Symmetrized Cosine**  
\[
F_{ij} = \exp(I_0 \cos(\theta_j - \theta_i))
\]  
- Symmetric  
- Small oscillatory deviations around 1  

---

## Outputs

Running the Python script produces:

### CSV Files

- `Fij_toy_S2_directional.csv` — directional F_ij matrix  
- `Fij_toy_S2_sym_abs.csv` — symmetric |Δθ| variant  
- `Fij_toy_S2_sym_cos.csv` — symmetric cos(Δθ) variant  
- `Fij_toy_S2_stats_by_generation.csv` — mean F per generation pair (3×3 blocks)

### Visualizations (PNG)

- `heatmap_F_directional.png` — heatmap of directional F_ij  
- `heatmap_F_sym_abs.png` — heatmap of |Δθ| variant  
- `heatmap_F_sym_cos.png` — heatmap of cos(Δθ) variant

---

## How to Run

1. Clone the repository or copy the Python script locally.
2. Ensure Python 3.x is installed, along with `numpy`, `pandas`, and `matplotlib`.
3. Run the script:

```bash
python generate_Fij_toy_S2.py
