# Orbital Bridge Report

## Source
- source_report: integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json
- engine: global_orbital_coherence_pass_v63_euler_df257
- steps: 20

## State Manifest
- coherence_index: 0.9210287158864723
- topological_charge_global: 0.09173654040948012
- phase_lock_error: 6.203753209251693
- beat_frequency_target_hz: 7.83
- spectral_radius_A: 1.5788043476614764
- fiedler_L: 0.17438387493107943
- zeta_enabled: True
- timestamp: 2026-04-08T19:37:07.487312+00:00

## Health Manifest
- system_health: 0.5684045566434583
- risk_level: low
- closure_penalty: 6.203753209251693
- R_H: 0.07897128411352769
- T_glob: 2.603929310583091
- Lambda_glob: 0.09173654040948012
- recommended_action: deep diagnostics allowed

## Recommended Control
- mode: safe
- phase_lock_enable: True
- target_phase_shift: -0.004721919065550805
- dt_override: 0.018
- zeta_coupling_scale: 0.3
- mu_phi: 0.16
- epsilon_hom: 0.18
- notes: Coherence is low or closure defect remains globally unsafe: use conservative execution.

## Bridge Metrics
- orbital_R_H: 0.07897128411352769
- orbital_closure_penalty: 6.203753209251693
- integration_closure_defect_proxy: 0.9210287158864723
- topological_charge_global: 0.09173654040948012
- subsystem_board_count: 0
- tau_system_count: 0

## Subsystem Sync Manifest
- board_count: 0
- avg_members_per_board: 0.0
- tau_orbit_count: 0
- tau_system_count: 0

## Runtime Gating
- dominant_privacy_constraint: UNKNOWN
- dominant_horizon_class: UNKNOWN
- export_boundary_mode: PROJECTED_ONLY
- private_state_export_allowed: False
- board_sync_ready: False
- system_tau_coherent: True
- requires_projection_operator: True

## CIEL Pipeline
- status: ok
- dominant_emotion: love
- mood: 0.900231987496021
- soul_invariant: 0.8197337988610099
- ethical_score: 0.35431562920368376
- orbital_context: orbital|mode=safe|R_H=0.0790|closure=6.2038|chirality=0.0917