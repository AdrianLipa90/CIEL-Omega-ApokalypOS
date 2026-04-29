# Global Orbital Coherence Pass

Read-only diagnostic pass over the canonical repository structure.

## Initial
- R_H: 0.012863
- T_glob: 1.590042
- Lambda_glob: 0.000000
- closure_penalty: 5.035071
- V_rel_total: 5.286440
- radial_spread: 0.181309
- mean_spin: 0.000000
- spectral_radius_A: 1.579819
- spectral_gap_A: 0.338432
- fiedler_L: 0.016196
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.007300
- zeta_coupling_norm_raw: 0.920782
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.004721
- nonlocal_phi_berry_mean: -0.102608
- nonlocal_eba_defect_mean: 0.048157
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.549020
- euler_bridge_target_phase: 0.105135

## Final
- R_H: 0.001694
- T_glob: 1.142257
- Lambda_glob: 0.155117
- closure_penalty: 4.779719
- V_rel_total: 4.952752
- radial_spread: 0.193353
- mean_spin: 0.062823
- spectral_radius_A: 1.209563
- spectral_gap_A: 0.295169
- fiedler_L: 0.041530
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: -0.004484
- zeta_coupling_norm: 0.007910
- zeta_coupling_norm_raw: 0.995378
- zeta_spin: 0.062823
- zeta_rho: 0.447153
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.004721
- nonlocal_phi_berry_mean: -0.102608
- nonlocal_eba_defect_mean: 0.048157
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.549020
- euler_bridge_target_phase: 0.105135

## Nonlocal Cards
- registry_present: True
- card_count: 5
- active_statuses: ACTIVE_CANONICAL_COUPLING_OPTIMIZER, ACTIVE_CANONICAL_NONLOCAL_BRIDGE, ACTIVE_CANONICAL_NONLOCAL_CARD_SET, ACTIVE_CANONICAL_NONLOCAL_RUNTIME, ACTIVE_CANONICAL_PHASE_RUNTIME
- eba_ready: True
- phase_ready: True
- bridge_ready: True

## Nonlocal / Euler Observables
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.004721
- nonlocal_phi_berry_mean: -0.102608
- nonlocal_eba_defect_mean: 0.048157
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.549020
- euler_bridge_target_phase: 0.105135

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- v6.3 uses Euler-rotated homology leak with D_f-dependent radial/angular split.
- When enabled, Orbital Law v0 adds effective attractor strength, orbital period, winding, and phase-slip tracking.
- This pass is diagnostic only; it does not mutate repo content.