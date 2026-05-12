# Global Orbital Coherence Pass

Read-only orbital coherence pass over the canonical repository structure.

- pass_label: runtime
- engine: global_orbital_coherence_pass_v64_runtime_bridge

## Initial
- R_H: 0.002299
- T_glob: 2.599250
- Lambda_glob: 0.000000
- closure_penalty: 6.021256
- V_rel_total: 6.413443
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.414065
- spectral_gap_A: 0.629369
- fiedler_L: 0.243668
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006662
- zeta_coupling_norm_raw: 0.836899
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 0.028529
- T_glob: 2.453059
- Lambda_glob: 0.225837
- closure_penalty: 5.933172
- V_rel_total: 6.329660
- radial_spread: 0.183102
- mean_spin: -0.059373
- spectral_radius_A: 1.262375
- spectral_gap_A: 0.474963
- fiedler_L: 0.283643
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000183
- zeta_coupling_norm: 0.006167
- zeta_coupling_norm_raw: 0.773654
- zeta_spin: -0.059373
- zeta_rho: 0.449886
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- The pass is read-only with respect to repository content; only reports/manifests are refreshed.
- Runtime policy is expected to consume R_H, closure_penalty, spectral observables, and zeta terms.