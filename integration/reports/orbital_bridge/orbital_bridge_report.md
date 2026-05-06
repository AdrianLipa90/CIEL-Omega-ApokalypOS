# Orbital Bridge Report

## Source
- source_report: integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json
- engine: global_orbital_coherence_pass_v63_euler_df257
- steps: 20

## State Manifest
- coherence_index: 0.9456117823370686
- topological_charge_global: -0.003718153274084362
- phase_lock_error: 5.424056929375785
- psi_mode: 0.156089
- beat_frequency_target_hz: 7.83
- spectral_radius_A: 0.6064973211599354
- fiedler_L: 0.028262290143302476
- zeta_enabled: True
- nonlocal_phi_ab_mean: 0.0076311957498907505
- nonlocal_phi_berry_mean: -0.09829849277020067
- nonlocal_eba_defect_mean: 0.050707762174271934
- nonlocal_coherent_fraction: 1.0
- euler_bridge_closure_score: 0.5346747037629884
- euler_bridge_target_phase: 0.031228850510360562
- effective_rh: 0.09212317406462389
- timestamp: 2026-05-06T16:19:33.847729+00:00

## Health Manifest
- system_health: 0.5955617573679859
- risk_level: low
- closure_penalty: 5.424056929375785
- R_H: 0.00045367947834456536
- T_glob: 0.7739080693668933
- Lambda_glob: -0.003718153274084362
- effective_rh: 0.09212317406462389
- rh_drivers: {'raw_rh': 0.00045367947834456536, 'eba_defect': 0.050707762174271934, 'coherent_fraction': 1.0, 'closure_score': 0.5346747037629884, 'phase_gap': 0.041229833897324236}
- recommended_action: deep diagnostics allowed

## Recommended Control
- mode: standard
- psi_mode: 0.156089
- phase_lock_enable: True
- target_phase_shift: 0.007620722254407216
- target_phase_memory: 0.031228850510360562
- dt_override: 0.020216
- zeta_coupling_scale: 0.344322
- mu_phi: 0.18
- epsilon_hom: 0.22
- nonlocal_gate: True
- euler_memory_lock: True
- writeback_gate: True
- rh_mode: normal_operation
- rh_severity: low
- rh_effective: 0.09212317406462389
- rh_drivers: {'raw_rh': 0.00045367947834456536, 'eba_defect': 0.050707762174271934, 'coherent_fraction': 1.0, 'closure_score': 0.5346747037629884, 'phase_gap': 0.041229833897324236}
- notes: Stable but not deep-merge safe.

## Bridge Metrics
- orbital_R_H: 0.00045367947834456536
- orbital_closure_penalty: 5.424056929375785
- integration_closure_defect_proxy: 0.9995463205216555
- topological_charge_global: -0.003718153274084362
- subsystem_board_count: 763
- tau_system_count: 1
- nonlocal_card_count: 6

## Subsystem Sync Manifest
- board_count: 763
- avg_members_per_board: 5.071
- tau_orbit_count: 763
- tau_system_count: 1
- nonlocal_card_count: 6
- nonlocal_card_classes: holonomy_persistence, nonlocal_memory_orchestrator, nonlocal_phase_memory_card_set, nonlocal_reduction_bridge, orbital_coupling_optimizer, phase_dynamics_runtime

## Runtime Gating
- dominant_privacy_constraint: GRADIENT_LIMITED_DISCLOSURE
- dominant_horizon_class: POROUS
- export_boundary_mode: PROJECTED_ONLY
- private_state_export_allowed: False
- board_sync_ready: True
- system_tau_coherent: True
- requires_projection_operator: True

## CIEL Pipeline
- status: ok
- dominant_emotion: love
- mood: 0.8866971661245503
- soul_invariant: 1.0028381328770801
- ethical_score: 0.6220563277587694
- orbital_context: orbital|mode=standard|R_H=0.0005|closure=5.4241|chirality=-0.0037
- phi_ab_mean: 0.0076311957498907505
- phi_berry_mean: -0.09829849277020067
- eba_defect_mean: 0.050707762174271934
- nonlocal_coherent_fraction: 1.0
- bridge_closure_score: 0.5346747037629884
- bridge_target_phase: 0.031228850510360562
- nonlocal_card_count: 6
- nonlocal_card_ids: ['NL-BERRY-ACC-0005', 'NL-BRIDGE-0003', 'NL-EBA-0002', 'NL-HOLOMEM-0001', 'NL-PHASE-0004', 'NL-WIJ-0005']
- phase_R_H: 7.690738481277209e-05
- collatz_seed: 28
- lie4_trace: 4.183135222640001
- local_nonlocality_fallback: {'active': False, 'fallback_coherent_fraction': 1.0, 'merged_coherent_fraction': 1.0}