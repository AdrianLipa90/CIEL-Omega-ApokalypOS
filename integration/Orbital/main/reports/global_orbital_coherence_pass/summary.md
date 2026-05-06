# Global Orbital Coherence Pass

Read-only diagnostic pass over the canonical repository structure.

## Initial
- R_H: 0.000700
- T_glob: 1.778174
- Lambda_glob: 0.000000
- closure_penalty: 4.522866
- V_rel_total: 4.790291
- radial_spread: 0.196305
- mean_spin: 0.000000
- spectral_radius_A: 1.515167
- spectral_gap_A: 0.559229
- fiedler_L: 0.025215
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000000
- zeta_coupling_norm: 0.006049
- zeta_coupling_norm_raw: 0.761803
- zeta_spin: 0.000000
- zeta_rho: 0.450000
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.007661
- nonlocal_phi_berry_mean: -0.098178
- nonlocal_eba_defect_mean: 0.050958
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.534675
- euler_bridge_target_phase: 0.031229

## Final
- R_H: 0.000454
- T_glob: 0.773908
- Lambda_glob: -0.003718
- closure_penalty: 5.424057
- V_rel_total: 5.540597
- radial_spread: 0.192600
- mean_spin: 0.027101
- spectral_radius_A: 0.606497
- spectral_gap_A: 0.016437
- fiedler_L: 0.028262
- zeta_enabled: True
- orbital_law_v0_enabled: False
- zeta_tetra_defect: 0.000000
- zeta_effective_tau: 0.364500
- zeta_effective_phase: 0.000186
- zeta_coupling_norm: 0.006715
- zeta_coupling_norm_raw: 0.843845
- zeta_spin: 0.027101
- zeta_rho: 0.450115
- D_f: 2.570000
- euler_leak_angle: 0.895354
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.007661
- nonlocal_phi_berry_mean: -0.098178
- nonlocal_eba_defect_mean: 0.050958
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.534675
- euler_bridge_target_phase: 0.031229

## Nonlocal Cards
- registry_present: True
- card_count: 6
- active_statuses: ACTIVE_CANONICAL, ACTIVE_CANONICAL_COUPLING_OPTIMIZER, ACTIVE_CANONICAL_NONLOCAL_BRIDGE, ACTIVE_CANONICAL_NONLOCAL_CARD_SET, ACTIVE_CANONICAL_NONLOCAL_RUNTIME, ACTIVE_CANONICAL_PHASE_RUNTIME
- eba_ready: True
- phase_ready: True
- bridge_ready: True

## Nonlocal / Euler Observables
- nonlocal_observables_present: True
- nonlocal_phi_ab_mean: 0.007661
- nonlocal_phi_berry_mean: -0.098178
- nonlocal_eba_defect_mean: 0.050958
- nonlocal_coherent_fraction: 1.000000
- euler_bridge_closure_score: 0.534675
- euler_bridge_target_phase: 0.031229

## Notes
- Geometry derived from imports + README mesh + AGENT mesh + manifests.
- v6.3 uses Euler-rotated homology leak with D_f-dependent radial/angular split.
- When enabled, Orbital Law v0 adds effective attractor strength, orbital period, winding, and phase-slip tracking.
- This pass is diagnostic only; it does not mutate repo content.