# Global Orbital Coherence Pass

Read-only diagnostic pass over the canonical repository structure.

## Initial
- R_H: 0.094074
- T_glob: 1.852025
- Lambda_glob: 0.000000
- closure_penalty: 4.976754
- V_rel_total: 5.348631
- radial_spread: 0.196305
- mean_spin: 0.000000
- spectral_radius_A: 1.518461
- spectral_gap_A: 0.539481
- fiedler_L: 0.025215
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006031
- zeta_coupling_norm_raw: 0.759449
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.007583
- nonlocal_phi_berry_mean: -0.097254
- nonlocal_eba_defect_mean: 0.052367
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.542338
- euler_bridge_target_phase: 0.044560

## Final
- R_H: 0.061144
- T_glob: 0.595830
- Lambda_glob: -0.013278
- closure_penalty: 5.052397
- V_rel_total: 5.202916
- radial_spread: 0.202186
- mean_spin: -0.087726
- spectral_radius_A: 0.940814
- spectral_gap_A: 0.012648
- fiedler_L: 0.026709
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.003954
- zeta_coupling_norm: 0.007028
- zeta_coupling_norm_raw: 0.883668
- zeta_spin: -0.087726
- zeta_rho: 0.452537
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.007583
- nonlocal_phi_berry_mean: -0.097254
- nonlocal_eba_defect_mean: 0.052367
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.542338
- euler_bridge_target_phase: 0.044560

## Nonlocal Cards
- registry_present: True
- card_count: 5
- active_statuses: ACTIVE_CANONICAL_COUPLING_OPTIMIZER, ACTIVE_CANONICAL_NONLOCAL_BRIDGE, ACTIVE_CANONICAL_NONLOCAL_CARD_SET, ACTIVE_CANONICAL_NONLOCAL_RUNTIME, ACTIVE_CANONICAL_PHASE_RUNTIME
- eba_ready: True
- phase_ready: True
- bridge_ready: True

## Nonlocal / Euler Observables
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.007583
- nonlocal_phi_berry_mean: -0.097254
- nonlocal_eba_defect_mean: 0.052367
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.542338
- euler_bridge_target_phase: 0.044560

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- v6.3 uses Euler-rotated homology leak with D_f-dependent radial/angular split.
- When enabled, Orbital Law v0 adds effective attractor strength, orbital period, winding, and phase-slip tracking.
- This pass is diagnostic only; it does not mutate repo content.