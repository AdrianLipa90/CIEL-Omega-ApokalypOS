from ciel_omega.memory import HolonomicMemoryOrchestrator


def test_strict_governor_blocks_semantic_consolidation():
    orch = HolonomicMemoryOrchestrator()
    strict_governor = {
        "consolidation_gate_threshold": 0.99,
        "require_loop_coherence": True,
        "allowed_consolidations": [],
        "blocked_consolidations": ["semantic", "procedural", "affective"],
        "channel_thresholds": {"semantic": 0.99, "procedural": 0.99, "affective": 0.99},
        "orbital_state": {
            "final": {"zeta_effective_phase": 0.0},
            "control": {"mode": "safe", "target_phase_shift": 0.0},
            "rh_policy": {"severity": "high"},
        },
    }
    for _ in range(5):
        orch.process_input(
            'Adrian prefers rigor',
            {
                'salience': 0.9,
                'confidence': 0.9,
                'memory_governor': strict_governor,
                'phase': 0.0,
            },
        )
    assert 'adrian prefers rigor' not in orch.m3.items
    assert 'adrian prefers rigor' in orch.m3.candidates


def test_default_orchestrator_still_consolidates_without_governor():
    orch = HolonomicMemoryOrchestrator()
    for _ in range(5):
        orch.process_input('Adrian prefers rigor', {'salience': 0.9, 'confidence': 0.9})
    assert 'adrian prefers rigor' in orch.m3.items
