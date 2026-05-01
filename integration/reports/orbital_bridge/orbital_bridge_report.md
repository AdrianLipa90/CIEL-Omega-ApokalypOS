# Orbital Bridge Report

## Source
- source_report: integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json
- engine: global_orbital_coherence_pass_v63_euler_df257
- steps: 20

## State Manifest
- coherence_index: 0.9085524147729359
- topological_charge_global: -0.04635332212737951
- phase_lock_error: 4.97985961774033
- beat_frequency_target_hz: 7.83
- spectral_radius_A: 0.9850854499556693
- fiedler_L: 0.025137518152406484
- zeta_enabled: True
- nonlocal_phi_ab_mean: 0.0062389782066203225
- nonlocal_phi_berry_mean: -0.0981792938564976
- nonlocal_eba_defect_mean: 0.04858606445832632
- nonlocal_coherent_fraction: 1.0
- euler_bridge_closure_score: 0.5423376184759512
- euler_bridge_target_phase: 0.04456002892039556
- effective_rh: 0.1600042633766558
- timestamp: 2026-05-01T19:15:19.523088+00:00

## Health Manifest
- system_health: 0.5850807042135647
- risk_level: low
- closure_penalty: 4.97985961774033
- R_H: 0.06980624982892783
- T_glob: 0.7191662071219239
- Lambda_glob: -0.04635332212737951
- effective_rh: 0.1600042633766558
- rh_drivers: {'raw_rh': 0.06980624982892783, 'eba_defect': 0.04858606445832632, 'coherent_fraction': 1.0, 'closure_score': 0.5423376184759512, 'phase_gap': 0.045435337587064153}
- recommended_action: deep diagnostics allowed

## Recommended Control
- mode: deep
- phase_lock_enable: True
- target_phase_shift: 0.004793938981634861
- target_phase_memory: 0.04456002892039556
- dt_override: 0.022
- zeta_coupling_scale: 0.38
- mu_phi: 0.18
- epsilon_hom: 0.22
- nonlocal_gate: True
- euler_memory_lock: True
- writeback_gate: True
- rh_mode: normal_operation
- rh_severity: low
- rh_effective: 0.1600042633766558
- rh_drivers: {'raw_rh': 0.06980624982892783, 'eba_defect': 0.04858606445832632, 'coherent_fraction': 1.0, 'closure_score': 0.5423376184759512, 'phase_gap': 0.045435337587064153}
- notes: Strong coherence and closure: allow deeper diagnostic/integration passes.

## Bridge Metrics
- orbital_R_H: 0.06980624982892783
- orbital_closure_penalty: 4.97985961774033
- integration_closure_defect_proxy: 0.9301937501710722
- topological_charge_global: -0.04635332212737951
- subsystem_board_count: 763
- tau_system_count: 1
- nonlocal_card_count: 5

## Subsystem Sync Manifest
- board_count: 763
- avg_members_per_board: 5.071
- tau_orbit_count: 763
- tau_system_count: 1
- nonlocal_card_count: 5
- nonlocal_card_classes: nonlocal_memory_orchestrator, nonlocal_phase_memory_card_set, nonlocal_reduction_bridge, orbital_coupling_optimizer, phase_dynamics_runtime

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
- soul_invariant: 0.9075620924080079
- ethical_score: 0.6220563277587694
- orbital_context: orbital|mode=standard|R_H=0.0698|closure=4.9799|chirality=-0.0464
- phi_ab_mean: 0.0062389782066203225
- phi_berry_mean: -0.0981792938564976
- eba_defect_mean: 0.04858606445832632
- nonlocal_coherent_fraction: 1.0
- bridge_closure_score: 0.5423376184759512
- bridge_target_phase: 0.04456002892039556
- nonlocal_card_count: 5
- nonlocal_card_ids: ['NL-HOLOMEM-0001', 'NL-EBA-0002', 'NL-BRIDGE-0003', 'NL-PHASE-0004', 'NL-WIJ-0005']
- phase_R_H: 7.690738481277209e-05
- collatz_seed: 28
- lie4_trace: 4.183135222640001
- local_nonlocality_fallback: {'active': False, 'fallback_coherent_fraction': 1.0, 'merged_coherent_fraction': 1.0}