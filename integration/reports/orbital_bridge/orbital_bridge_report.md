# Orbital Bridge Report

## Source
- source_report: integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json
- engine: global_orbital_coherence_pass_v63_euler_df257
- steps: 20

## State Manifest
- coherence_index: 0.9454734778536629
- topological_charge_global: 0.13628494783638298
- phase_lock_error: 4.581267580547717
- beat_frequency_target_hz: 7.83
- spectral_radius_A: 1.325411265571133
- fiedler_L: 0.041625893305604074
- zeta_enabled: True
- nonlocal_phi_ab_mean: 0.00805868792533336
- nonlocal_phi_berry_mean: -0.10437557160226742
- nonlocal_eba_defect_mean: 0.05077424888378425
- nonlocal_coherent_fraction: 1.0
- euler_bridge_closure_score: 0.5490203081103036
- euler_bridge_target_phase: 0.10513460948622075
- effective_rh: 0.09538215821844093
- timestamp: 2026-04-30T17:19:17.398079+00:00

## Health Manifest
- system_health: 0.6263944777887483
- risk_level: low
- closure_penalty: 4.581267580547717
- R_H: 0.003295301135999777
- T_glob: 1.3000764938619103
- Lambda_glob: 0.13628494783638298
- effective_rh: 0.09538215821844093
- rh_drivers: {'raw_rh': 0.003295301135999777, 'eba_defect': 0.05077424888378425, 'coherent_fraction': 1.0, 'closure_score': 0.5490203081103036, 'phase_gap': 0.06668916189662201}
- recommended_action: deep diagnostics allowed

## Recommended Control
- mode: deep
- phase_lock_enable: True
- target_phase_shift: 0.030698649611444435
- target_phase_memory: 0.10513460948622075
- dt_override: 0.022
- zeta_coupling_scale: 0.38
- mu_phi: 0.18
- epsilon_hom: 0.22
- nonlocal_gate: True
- euler_memory_lock: True
- writeback_gate: True
- rh_mode: normal_operation
- rh_severity: low
- rh_effective: 0.09538215821844093
- rh_drivers: {'raw_rh': 0.003295301135999777, 'eba_defect': 0.05077424888378425, 'coherent_fraction': 1.0, 'closure_score': 0.5490203081103036, 'phase_gap': 0.06668916189662201}
- notes: Strong coherence and closure: allow deeper diagnostic/integration passes.

## Bridge Metrics
- orbital_R_H: 0.003295301135999777
- orbital_closure_penalty: 4.581267580547717
- integration_closure_defect_proxy: 0.9967046988640003
- topological_charge_global: 0.13628494783638298
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
- mood: 0.903467154343101
- soul_invariant: 0.7328088001200123
- ethical_score: 0.7830730540829481
- orbital_context: orbital|mode=standard|R_H=0.0033|closure=4.5813|chirality=0.1363
- phi_ab_mean: 0.00805868792533336
- phi_berry_mean: -0.10437557160226742
- eba_defect_mean: 0.05077424888378425
- nonlocal_coherent_fraction: 1.0
- bridge_closure_score: 0.5490203081103036
- bridge_target_phase: 0.10513460948622075
- nonlocal_card_count: 5
- nonlocal_card_ids: ['NL-HOLOMEM-0001', 'NL-EBA-0002', 'NL-BRIDGE-0003', 'NL-PHASE-0004', 'NL-WIJ-0005']
- phase_R_H: 7.069913467110384e-05
- collatz_seed: 28
- lie4_trace: 4.183135222640001
- local_nonlocality_fallback: {'active': False, 'fallback_coherent_fraction': 1.0, 'merged_coherent_fraction': 1.0}