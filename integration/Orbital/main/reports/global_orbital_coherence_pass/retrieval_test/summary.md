# Global Orbital Coherence Pass

Read-only orbital coherence pass over the canonical repository structure.

- pass_label: retrieval_test
- engine: global_orbital_coherence_pass_v64_runtime_bridge

## Initial
- R_H: 0.002299
- T_glob: 2.560711
- Lambda_glob: 0.000000
- closure_penalty: 6.006616
- V_rel_total: 6.393022
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.392763
- spectral_gap_A: 0.619888
- fiedler_L: 0.239998
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.007029
- zeta_coupling_norm_raw: 0.884867
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Final
- R_H: 0.019022
- T_glob: 2.422318
- Lambda_glob: 0.201839
- closure_penalty: 5.912115
- V_rel_total: 6.294485
- radial_spread: 0.182857
- mean_spin: -0.059555
- spectral_radius_A: 1.247508
- spectral_gap_A: 0.472231
- fiedler_L: 0.279852
- zeta_enabled: True
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.000161
- zeta_coupling_norm: 0.006509
- zeta_coupling_norm_raw: 0.818181
- zeta_spin: -0.059555
- zeta_rho: 0.449899
- D_f: 2.570000
- euler_leak_angle: 0.895354

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- The pass is read-only with respect to repository content; only reports/manifests are refreshed.
- Runtime policy is expected to consume R_H, closure_penalty, spectral observables, and zeta terms.