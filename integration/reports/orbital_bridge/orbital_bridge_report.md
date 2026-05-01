# Orbital Bridge Report

## Source
- source_report: integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json
- engine: global_orbital_coherence_pass_v63_euler_df257
- steps: 20

## State Manifest
- coherence_index: 0.9126922321131482
- topological_charge_global: -0.013278298661074838
- phase_lock_error: 5.052397322033294
- psi_mode: 0.18204
- beat_frequency_target_hz: 7.83
- spectral_radius_A: 0.9408138156020491
- fiedler_L: 0.026708682569902026
- zeta_enabled: True
- nonlocal_phi_ab_mean: 0.007684738303675589
- nonlocal_phi_berry_mean: -0.09712701508513395
- nonlocal_eba_defect_mean: 0.05274946257235783
- nonlocal_coherent_fraction: 1.0
- euler_bridge_closure_score: 0.5423376184759512
- euler_bridge_target_phase: 0.04456002892039556
- effective_rh: 0.1527655448114867
- timestamp: 2026-05-01T23:16:22.131558+00:00

## Health Manifest
- system_health: 0.5855730488467108
- risk_level: low
- closure_penalty: 5.052397322033294
- R_H: 0.06114383699744232
- T_glob: 0.59583046329804
- Lambda_glob: -0.013278298661074838
- effective_rh: 0.1527655448114867
- rh_drivers: {'raw_rh': 0.06114383699744232, 'eba_defect': 0.05274946257235783, 'coherent_fraction': 1.0, 'closure_score': 0.5423376184759512, 'phase_gap': 0.045100386851117856}
- recommended_action: deep diagnostics allowed

## Recommended Control
- mode: standard
- psi_mode: 0.18204
- phase_lock_enable: True
- target_phase_shift: 0.007186234608721164
- target_phase_memory: 0.04456002892039556
- dt_override: 0.01992
- zeta_coupling_scale: 0.338391
- mu_phi: 0.18
- epsilon_hom: 0.22
- nonlocal_gate: True
- euler_memory_lock: True
- writeback_gate: True
- rh_mode: normal_operation
- rh_severity: low
- rh_effective: 0.1527655448114867
- rh_drivers: {'raw_rh': 0.06114383699744232, 'eba_defect': 0.05274946257235783, 'coherent_fraction': 1.0, 'closure_score': 0.5423376184759512, 'phase_gap': 0.045100386851117856}
- notes: Stable but not deep-merge safe.

## Bridge Metrics
- orbital_R_H: 0.06114383699744232
- orbital_closure_penalty: 5.052397322033294
- integration_closure_defect_proxy: 0.9388561630025577
- topological_charge_global: -0.013278298661074838
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
- soul_invariant: 0.8506214020401736
- ethical_score: 0.6220563277587694
- orbital_context: orbital|mode=standard|R_H=0.0611|closure=5.0524|chirality=-0.0133
- phi_ab_mean: 0.007684738303675589
- phi_berry_mean: -0.09712701508513395
- eba_defect_mean: 0.05274946257235783
- nonlocal_coherent_fraction: 1.0
- bridge_closure_score: 0.5423376184759512
- bridge_target_phase: 0.04456002892039556
- nonlocal_card_count: 5
- nonlocal_card_ids: ['NL-HOLOMEM-0001', 'NL-EBA-0002', 'NL-BRIDGE-0003', 'NL-PHASE-0004', 'NL-WIJ-0005']
- phase_R_H: 7.690738481277209e-05
- collatz_seed: 28
- lie4_trace: 4.183135222640001
- local_nonlocality_fallback: {'active': False, 'fallback_coherent_fraction': 1.0, 'merged_coherent_fraction': 1.0}