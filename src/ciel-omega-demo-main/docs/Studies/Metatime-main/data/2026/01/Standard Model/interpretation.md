# Toy-Model White-Thread Matrix F_ij on S²

**Toy-Model Construction**: 12 SM fermions assigned to cycles on Kähler sphere S² via polar angles θ_i.  
**Intention Operator**: I₀ = 0.009 (subtle topological corrections). [Geometria.txt]  
**Generated**: 3 matrices (directional + 2 symmetric), block stats, top deviations, full analysis. [code_file:77..87]

## Model Specification

| Fermion | Generation | Cycle θ_i (rad) |
|---------|------------|-----------------|
| e       | 1          | π/6 ≈ 0.5236   |
| μ       | 2          | π/4 ≈ 0.7854   |
| τ       | 3          | π/3 ≈ 1.0472   |
| u       | 1          | π/8 ≈ 0.3927   |
| d       | 1          | π/10 ≈ 0.3142  |
| s       | 2          | π/5 ≈ 0.6283   |
| c       | 2          | π/2 ≈ 1.5708   |
| b       | 3          | 2π/3 ≈ 2.0944  |
| t       | 3          | 5π/6 ≈ 2.6180  |
| ν₁      | 1          | π/12 ≈ 0.2618  |
| ν₂      | 2          | π/6 ≈ 0.5236   |
| ν₃      | 3          | π/4 ≈ 0.7854   |

**Matrix Variants**:
1. **Directional**: F_ij = exp(I₀ (θ_j - θ_i)) → F_ji = 1/F_ij (asymmetric)
2. **Symmetric Abs**: F_ij = exp(I₀ |θ_j - θ_i|) → ≥1, distance-like
3. **Symmetric Cos**: F_ij = exp(I₀ cos(θ_j - θ_i)) → oscillatory

## Summary Statistics

| Variant      | Min     | Max     | Mean   | Std     |
|--------------|---------|---------|--------|---------|
| Directional | 0.9790 | 1.0214 | ~1.000 | 0.0065 |
| Sym Abs     | 1.0000 | 1.0214 | 1.0032 | 0.0048 |
| Sym Cos     | 0.9937 | 1.0090 | 1.0000 | 0.0037 |

**Key Insight**: All effects **subtle** (promille scale), as expected from small I₀. [code_file:84]

## Inter-Generation Block Averages (Directional)

| Gen i → Gen j | Mean F_ij |
|---------------|-----------|
| 1 → 1         | 1.000001 |
| 1 → 2         | 1.004553 |
| 1 → 3         | 1.011457 |
| 2 → 1         | 0.995482 |
| 2 → 2         | 1.000014 |
| 2 → 3         | 1.006903 |
| 3 → 1         | 0.988589 |
| 3 → 2         | 0.993133 |
| 3 → 3         | 1.000000 |

**Asymmetry**: 1→3 (1.0115) vs 3→1 (0.9886); mutual inverses. [code_file:80]

## Sample Pairwise Values

| Pair     | F_dir   | F_abs   | F_cos   |
|----------|---------|---------|---------|
| e → μ    | 1.0024  | 1.0024  | 1.0089 |
| μ → e    | 0.9976  | 1.0024  | 1.0089 |
| e → τ    | 1.0047  | 1.0047  | 1.0073 |
| τ → e    | 0.9953  | 1.0047  | 1.0073 |
| ν₁ → ν₃  | 1.0090  | 1.0090  | 1.0090 |
| ν₃ → ν₁  | 0.9911  | 1.0090  | 1.0090 |
| d → t    | 1.0214  | 1.0214  | 0.9937 |
| t → d    | 0.9790  | 1.0214  | 0.9937 |

**Neutrino hierarchy**: ν₁→ν₃ stronger than inverse (directional). [code_file:83]

## Top Deviations from 1 (|F_ij - 1| > 0, excluding diagonal)

**Directional** (largest): t→d (0.9790, Δ=-0.0214), d→t (1.0214, Δ=+0.0214), b→ν₁ (0.9805), ...  
**Sym Abs** (largest): t↔d (1.0214), b↔ν₁ (1.0209), ...  
**Sym Cos** (largest): t↔d (0.9937), ν₁↔t (0.9937), ... [code_file:85][code_file:86][code_file:87]

## Physical Interpretation

1. **Directional**: Models **oriented transport** (holonomy-like). Generations 1→3 amplified (1.01), 3→1 suppressed (0.99). Matches CP-asymmetry intuition.
2. **Sym Abs**: Pure **topological distance**. Larger |Δθ| → larger F_ij ≥1. Intra-gen closer, inter-gen farther.
3. **Sym Cos**: **Phase alignment**. Aligned cycles (small Δθ) amplified, anti-aligned suppressed.

**Toy-Model Strength**: Captures generational hierarchy via θ_i geometry.  
**Limitation**: Effects too small (~2%) vs real F_i (e.g. d-quark F_d=0.783). Scale I₀ or add β factor for calibration. [Formal_SM.pdf]

## Files Generated

| File | Description |
|------|-------------|
| `analysis_F_directional_full.csv` | Full 12×12 F_dir [code_file:77] |
| `analysis_F_sym_abs_full.csv` | Full 12×12 F_abs [code_file:78] |
| `analysis_F_sym_cos_full.csv` | Full 12×12 F_cos [code_file:79] |
| `analysis_blocks_*.csv` | 3×3 gen blocks (3 files) [code_file:80..82] |
| `analysis_sample_pairs.csv` | 8 example pairs [code_file:83] |
| `analysis_summary_variants.csv` | Min/max/mean/std [code_file:84] |
| `analysis_top_deviations_*.csv` | Top |Δ| pairs (3 files) [code_file:85..87] |

**Next Steps**:  
- Calibrate β to match PDG F_i (u/d/s/neutrinos).  
- Add monopole Berry A on S² for true holonomy.  
- Extend to full SM (baryons/mesons via quark F_ij).
