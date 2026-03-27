# Global Orbital Coherence Pass

Read-only orbital coherence pass over the canonical repository structure.

- pass_label: research
- engine: global_orbital_coherence_pass_v64_runtime_bridge

## Initial
- R_H: 0.002299
- T_glob: 2.608548
- Lambda_glob: 0.000000
- closure_penalty: 6.024824
- V_rel_total: 6.418406
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.419086
- spectral_gap_A: 0.631603
- fiedler_L: 0.244533
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006739
- zeta_coupling_norm_raw: 0.846884
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 0.033870
- T_glob: 2.461823
- Lambda_glob: 0.239323
- closure_penalty: 5.940947
- V_rel_total: 6.344091
- radial_spread: 0.182952
- mean_spin: -0.059561
- spectral_radius_A: 1.265664
- spectral_gap_A: 0.475115
- fiedler_L: 0.284434
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000168
- zeta_coupling_norm: 0.006238
- zeta_coupling_norm_raw: 0.782871
- zeta_spin: -0.059561
- zeta_rho: 0.449895
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- The pass is read-only with respect to repository content; only reports/manifests are refreshed.
- Runtime policy is expected to consume R_H, closure_penalty, spectral observables, and zeta terms.