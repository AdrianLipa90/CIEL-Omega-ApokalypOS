# Global Orbital Coherence Pass

Read-only orbital coherence pass over the canonical repository structure.

- pass_label: orbital_test
- engine: global_orbital_coherence_pass_v64_runtime_bridge

## Initial
- R_H: 0.002299
- T_glob: 2.465351
- Lambda_glob: 0.000000
- closure_penalty: 5.972418
- V_rel_total: 6.344520
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.340778
- spectral_gap_A: 0.596750
- fiedler_L: 0.231039
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006934
- zeta_coupling_norm_raw: 0.872383
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 0.012538
- T_glob: 2.345086
- Lambda_glob: 0.190978
- closure_penalty: 5.878691
- V_rel_total: 6.242991
- radial_spread: 0.182703
- mean_spin: -0.053189
- spectral_radius_A: 1.209961
- spectral_gap_A: 0.463023
- fiedler_L: 0.270055
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000141
- zeta_coupling_norm: 0.006427
- zeta_coupling_norm_raw: 0.807462
- zeta_spin: -0.053189
- zeta_rho: 0.449912
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- The pass is read-only with respect to repository content; only reports/manifests are refreshed.
- Runtime policy is expected to consume R_H, closure_penalty, spectral observables, and zeta terms.