"""CIEL/Ω M5 Affective/Ethical Memory - Consolidation and kernel tests."""

import numpy as np

from memory import IdentityField, AffectiveEthicalMemory, EpisodicMemory, MemoryDynamicsEngine


def _episode(content, t, phase=0.5, salience=0.85, impact=0.85, **ctx):
    episodic = EpisodicMemory()
    episodic.store(content, {
        'timestamp': float(t),
        'salience': salience,
        'identity_impact': impact,
        'context': ctx,
    })
    ep = episodic.episodes[-1]
    ep.phase_at_storage = phase
    return ep


def test_3_contradictions_block_consolidation():
    identity = IdentityField(initial_phase=0.5)
    m5 = AffectiveEthicalMemory(identity)
    episodes = [
        _episode("Operation is safe", 0, 0.50, protective_score=0.92, arousal=0.35),
        _episode("Operation is safe", 1, 0.51, protective_score=0.90, arousal=0.35),
        _episode("Operation is not safe", 2, 0.49, ethical_risk=0.92, arousal=0.75),
        _episode("Operation is not safe", 3, 0.50, ethical_risk=0.95, arousal=0.78),
    ]
    for ep in episodes:
        m5.observe_episode(ep)
    cand = m5.check_candidate_creation("operation is safe")
    item = m5.consolidate_candidate("operation is safe", 5.0)
    # Same semantic root with opposite negation should not consolidate cleanly.
    assert (item is None) or (item.status == 'contested') or (cand and cand.status == 'blocked')


def test_6_kernel_stability_preserved():
    engine = MemoryDynamicsEngine()
    np.random.seed(42)
    initial_phases = np.random.randn(8) * 0.5
    state = engine.initialize_state(initial_phases, initial_identity_phase=0.0)
    V0 = engine.potential.compute_static_potential(state.phases, state.anchor_phases, engine.equilibrium_shifts)['V_static']
    Dm0 = engine.potential.compute_global_memory_defect(state.phases, engine.equilibrium_shifts)
    Di0 = engine.potential.compute_global_identity_defect(state.phases)
    final_state = engine.integrate(200, dt=0.1, input_forces=None)
    Vf = engine.potential.compute_static_potential(final_state.phases, final_state.anchor_phases, engine.equilibrium_shifts)['V_static']
    Dmf = engine.potential.compute_global_memory_defect(final_state.phases, engine.equilibrium_shifts)
    Dif = engine.potential.compute_global_identity_defect(final_state.phases)
    assert Vf < V0 and Dmf < Dm0 and Dif < Di0



def _run_test(fn):
    try:
        fn()
        return True
    except AssertionError:
        return False

def main():
    tests = [
        ("T3 contradiction blocks consolidation", test_3_contradictions_block_consolidation),
        ("T6 kernel stability preserved", test_6_kernel_stability_preserved),
    ]
    passed=0
    for name, fn in tests:
        ok=_run_test(fn)
        print(name, 'PASS' if ok else 'FAIL')
        passed += int(ok)
    print(f"\nCONSOLIDATION TESTS PASSED: {passed}/{len(tests)}")
    raise SystemExit(0 if passed == len(tests) else 1)


if __name__ == '__main__':
    main()
