# Global Orbital Coherence Pass

Read-only orbital coherence pass over the canonical repository structure.

- pass_label: orbital_smoke
- engine: global_orbital_coherence_pass_v64_runtime_bridge

## Initial
- R_H: 0.002299
- T_glob: 2.457617
- Lambda_glob: 0.000000
- closure_penalty: 5.969785
- V_rel_total: 6.340727
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.336694
- spectral_gap_A: 0.594932
- fiedler_L: 0.230336
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006742
- zeta_coupling_norm_raw: 0.847289
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 0.013824
- T_glob: 2.338580
- Lambda_glob: 0.196891
- closure_penalty: 5.878504
- V_rel_total: 6.243116
- radial_spread: 0.182785
- mean_spin: -0.052735
- spectral_radius_A: 1.206891
- spectral_gap_A: 0.461999
- fiedler_L: 0.269231
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000148
- zeta_coupling_norm: 0.006250
- zeta_coupling_norm_raw: 0.784372
- zeta_spin: -0.052735
- zeta_rho: 0.449908
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- The pass is read-only with respect to repository content; only reports/manifests are refreshed.
- Runtime policy is expected to consume R_H, closure_penalty, spectral observables, and zeta terms.