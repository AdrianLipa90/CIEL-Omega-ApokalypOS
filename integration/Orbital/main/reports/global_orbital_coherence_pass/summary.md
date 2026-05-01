# Global Orbital Coherence Pass

Read-only diagnostic pass over the canonical repository structure.

## Initial
- R_H: 0.117823
- T_glob: 1.871953
- Lambda_glob: 0.000000
- closure_penalty: 5.143644
- V_rel_total: 5.542260
- radial_spread: 0.196305
- mean_spin: 0.000000
- spectral_radius_A: 1.517568
- spectral_gap_A: 0.535138
- fiedler_L: 0.025215
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006069
- zeta_coupling_norm_raw: 0.764145
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.007037
- nonlocal_phi_berry_mean: -0.099251
- nonlocal_eba_defect_mean: 0.048130
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.542338
- euler_bridge_target_phase: 0.044560

## Final
- R_H: 0.069806
- T_glob: 0.719166
- Lambda_glob: -0.046353
- closure_penalty: 4.979860
- V_rel_total: 5.157541
- radial_spread: 0.202169
- mean_spin: -0.022809
- spectral_radius_A: 0.985085
- spectral_gap_A: 0.025291
- fiedler_L: 0.025138
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.006346
- zeta_coupling_norm: 0.007265
- zeta_coupling_norm_raw: 0.914254
- zeta_spin: -0.022809
- zeta_rho: 0.454049
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.007037
- nonlocal_phi_berry_mean: -0.099251
- nonlocal_eba_defect_mean: 0.048130
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
- nonlocal_phi_ab_mean: 0.007037
- nonlocal_phi_berry_mean: -0.099251
- nonlocal_eba_defect_mean: 0.048130
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.542338
- euler_bridge_target_phase: 0.044560

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- v6.3 uses Euler-rotated homology leak with D_f-dependent radial/angular split.
- When enabled, Orbital Law v0 adds effective attractor strength, orbital period, winding, and phase-slip tracking.
- This pass is diagnostic only; it does not mutate repo content.