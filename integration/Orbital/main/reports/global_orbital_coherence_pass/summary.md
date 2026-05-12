# Global Orbital Coherence Pass

Read-only diagnostic pass over the canonical repository structure.

## Initial
- R_H: 53.565317
- T_glob: 4.855823
- Lambda_glob: 0.000000
- closure_penalty: 1.159861
- V_rel_total: 55.453552
- radial_spread: 0.147426
- n_sectors: 27.000000
- mean_spin: 0.000000
- spectral_radius_A: 4.170724
- spectral_gap_A: 2.677477
- fiedler_L: -0.000000
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.035451
- zeta_coupling_norm_raw: 4.454310
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.008548
- nonlocal_phi_berry_mean: -0.105502
- nonlocal_eba_defect_mean: 0.050851
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.535812
- euler_bridge_target_phase: 0.052739

## Final
- R_H: 25.657300
- T_glob: 3.804490
- Lambda_glob: -0.701858
- closure_penalty: 0.775830
- V_rel_total: 27.003803
- radial_spread: 0.133362
- n_sectors: 27.000000
- mean_spin: -0.121976
- spectral_radius_A: 3.590383
- spectral_gap_A: 1.777901
- fiedler_L: 0.000000
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000832
- zeta_coupling_norm: 0.014140
- zeta_coupling_norm_raw: 1.773525
- zeta_spin: -0.121976
- zeta_rho: 0.450549
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.008548
- nonlocal_phi_berry_mean: -0.105502
- nonlocal_eba_defect_mean: 0.050851
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.535812
- euler_bridge_target_phase: 0.052739

## Nonlocal Cards
- registry_present: True
- card_count: 6
- active_statuses: ACTIVE_CANONICAL, ACTIVE_CANONICAL_COUPLING_OPTIMIZER, ACTIVE_CANONICAL_NONLOCAL_BRIDGE, ACTIVE_CANONICAL_NONLOCAL_CARD_SET, ACTIVE_CANONICAL_NONLOCAL_RUNTIME, ACTIVE_CANONICAL_PHASE_RUNTIME
- eba_ready: True
- phase_ready: True
- bridge_ready: True

## Nonlocal / Euler Observables
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.008548
- nonlocal_phi_berry_mean: -0.105502
- nonlocal_eba_defect_mean: 0.050851
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.535812
- euler_bridge_target_phase: 0.052739

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- v6.3 uses Euler-rotated homology leak with D_f-dependent radial/angular split.
- When enabled, Orbital Law v0 adds effective attractor strength, orbital period, winding, and phase-slip tracking.
- This pass is diagnostic only; it does not mutate repo content.