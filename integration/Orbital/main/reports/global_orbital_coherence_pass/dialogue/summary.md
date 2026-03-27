# Global Orbital Coherence Pass

Read-only orbital coherence pass over the canonical repository structure.

- pass_label: dialogue
- engine: global_orbital_coherence_pass_v64_runtime_bridge

## Initial
- R_H: 0.002299
- T_glob: 2.670852
- Lambda_glob: 0.000000
- closure_penalty: 6.049447
- V_rel_total: 6.452374
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.453004
- spectral_gap_A: 0.646699
- fiedler_L: 0.250378
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006867
- zeta_coupling_norm_raw: 0.863675
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 0.031812
- T_glob: 2.509937
- Lambda_glob: 0.223936
- closure_penalty: 5.956713
- V_rel_total: 6.365016
- radial_spread: 0.183093
- mean_spin: -0.062962
- spectral_radius_A: 1.289718
- spectral_gap_A: 0.481381
- fiedler_L: 0.290816
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000184
- zeta_coupling_norm: 0.006351
- zeta_coupling_norm_raw: 0.797546
- zeta_spin: -0.062962
- zeta_rho: 0.449885
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- The pass is read-only with respect to repository content; only reports/manifests are refreshed.
- Runtime policy is expected to consume R_H, closure_penalty, spectral observables, and zeta terms.