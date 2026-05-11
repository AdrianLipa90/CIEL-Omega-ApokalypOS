# Global Orbital Coherence Pass

Read-only orbital coherence pass over the canonical repository structure.

- pass_label: dialogue
- engine: global_orbital_coherence_pass_v64_runtime_bridge

## Initial
- R_H: 0.002299
- T_glob: 2.720063
- Lambda_glob: 0.000000
- closure_penalty: 6.069734
- V_rel_total: 6.480043
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.479949
- spectral_gap_A: 0.658692
- fiedler_L: 0.255021
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006752
- zeta_coupling_norm_raw: 0.848661
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 0.044026
- T_glob: 2.549089
- Lambda_glob: 0.247713
- closure_penalty: 5.981790
- V_rel_total: 6.408179
- radial_spread: 0.183211
- mean_spin: -0.062402
- spectral_radius_A: 1.307953
- spectral_gap_A: 0.484410
- fiedler_L: 0.295467
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000192
- zeta_coupling_norm: 0.006241
- zeta_coupling_norm_raw: 0.783262
- zeta_spin: -0.062402
- zeta_rho: 0.449880
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- The pass is read-only with respect to repository content; only reports/manifests are refreshed.
- Runtime policy is expected to consume R_H, closure_penalty, spectral observables, and zeta terms.