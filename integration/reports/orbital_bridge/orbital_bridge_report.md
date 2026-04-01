# Orbital Bridge Report

## Source
- source_report: integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json
- engine: global_orbital_coherence_pass_minimal
- steps: 20

## State Manifest
- coherence_index: 0.9309893333230331
- topological_charge_global: 0.048498965690035194
- phase_lock_error: 1.6215131395780191
- beat_frequency_target_hz: 7.83
- spectral_radius_A: 2.030364349344266
- fiedler_L: 0.00042326407671338545
- zeta_enabled: True
- timestamp: 2026-04-01T13:26:35.727091+00:00

## Health Manifest
- system_health: 0.801091322740472
- risk_level: low
- closure_penalty: 1.6215131395780191
- R_H: 0.06901066667696684
- T_glob: 0.6905238062549859
- Lambda_glob: 0.048498965690035194
- recommended_action: deep diagnostics allowed

## Recommended Control
- mode: standard
- phase_lock_enable: True
- target_phase_shift: -2.220446049250313e-16
- dt_override: 0.0205
- zeta_coupling_scale: 0.35
- mu_phi: 0.18
- epsilon_hom: 0.22
- notes: Coherence is strong but closure still needs supervision; allow controlled execution.

## Bridge Metrics
- orbital_R_H: 0.06901066667696684
- orbital_closure_penalty: 1.6215131395780191
- integration_closure_defect_proxy: 0.9309893333230331
- topological_charge_global: 0.048498965690035194