# Global Orbital Coherence Pass

Read-only orbital coherence pass over the canonical repository structure.

- pass_label: safety
- engine: global_orbital_coherence_pass_v64_runtime_bridge

## Initial
- R_H: 0.002299
- T_glob: 3.240216
- Lambda_glob: 0.000000
- closure_penalty: 6.326707
- V_rel_total: 6.815039
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.763498
- spectral_gap_A: 0.784893
- fiedler_L: 0.303882
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.007293
- zeta_coupling_norm_raw: 0.919670
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 0.393338
- T_glob: 2.957985
- Lambda_glob: 0.207672
- closure_penalty: 6.301303
- V_rel_total: 7.138339
- radial_spread: 0.184297
- mean_spin: 0.008746
- spectral_radius_A: 1.482350
- spectral_gap_A: 0.497392
- fiedler_L: 0.336258
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000133
- zeta_coupling_norm: 0.006781
- zeta_coupling_norm_raw: 0.853302
- zeta_spin: 0.008746
- zeta_rho: 0.449916
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- The pass is read-only with respect to repository content; only reports/manifests are refreshed.
- Runtime policy is expected to consume R_H, closure_penalty, spectral observables, and zeta terms.