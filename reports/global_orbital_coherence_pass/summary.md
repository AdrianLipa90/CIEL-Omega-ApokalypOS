# Global Orbital Coherence Pass

Read-only diagnostic pass over the canonical repository structure.

## Initial
- R_H: 60.810390
- T_glob: 6.110661
- Lambda_glob: 0.000000
- closure_penalty: 1.094501
- V_rel_total: 62.821491
- radial_spread: 0.178734
- mean_spin: 0.000000
- spectral_radius_A: 4.100613
- spectral_gap_A: 2.969807
- fiedler_L: 0.000000
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.035211
- zeta_coupling_norm_raw: 4.422513
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 28.527289
- T_glob: 4.190221
- Lambda_glob: -0.707719
- closure_penalty: 0.787297
- V_rel_total: 29.943120
- radial_spread: 0.169325
- mean_spin: -0.122618
- spectral_radius_A: 3.685080
- spectral_gap_A: 2.558263
- fiedler_L: -0.000000
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000257
- zeta_coupling_norm: 0.011830
- zeta_coupling_norm_raw: 1.480901
- zeta_spin: -0.122618
- zeta_rho: 0.449852
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- v6.3 uses Euler-rotated homology leak with D_f-dependent radial/angular split.
- berry_phase written back to sectors_global.json after each pass for holonomy continuity.