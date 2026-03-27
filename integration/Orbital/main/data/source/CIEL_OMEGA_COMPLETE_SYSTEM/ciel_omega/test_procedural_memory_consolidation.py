"""CIEL/Ω M4 Procedural Memory - Consolidation tests 3 and 6"""

import numpy as np

from ciel_omega.memory import IdentityField, ProceduralMemory, EpisodicMemory, MemoryDynamicsEngine


def _episode(content, t, goal='solve issue', action='run diagnostic', success=True, phase=0.5, salience=0.88, impact=0.80):
    episodic = EpisodicMemory()
    episodic.store(content, {
        'timestamp': float(t),
        'salience': salience,
        'identity_impact': impact,
        'context': {'goal': goal, 'action': action, 'success': success},
        'result': {'success': success},
    })
    ep = episodic.episodes[-1]
    ep.phase_at_storage = phase
    return ep


def test_3_contradiction_blocks_consolidation():
    identity = IdentityField(initial_phase=0.5)
    m4 = ProceduralMemory(identity)
    for i in range(3):
        tr = m4.observe_episode(_episode('Run diagnostic to solve issue', i, goal='solve issue', action='run diagnostic', success=True, phase=0.5 + 0.01*i))
    for i in range(3,6):
        # conflicting successful alternative for same goal should raise contradiction
        m4.observe_episode(_episode('Restart service to solve issue', i, goal='solve issue', action='restart service', success=True, phase=1.8))
    cand = m4.check_candidate_creation(tr.procedure_key)
    cand = m4.check_candidate_creation(tr.procedure_key)
    item = m4.consolidate_candidate(tr.procedure_key, 10.0)
    assert cand is not None and cand.contradiction_score > 0.20 and item is None


def test_6_kernel_stability_preserved():
    identity = IdentityField(initial_phase=0.5)
    engine = MemoryDynamicsEngine(identity)
    rng = np.random.default_rng(7)
    initial_phases = (rng.random(8) * 0.6) + 0.2
    state0 = engine.initialize_state(initial_phases=initial_phases, initial_identity_phase=0.5)
    metrics0 = engine.compute_stability_metrics(state0)
    state1 = engine.integrate(num_steps=50, dt=0.1, input_forces=np.zeros(8), initial_state=state0)
    metrics1 = engine.compute_stability_metrics(state1)
    assert (metrics1['energy']['V_static'] <= metrics0['energy']['V_static'] + 1e-9 and
            metrics1['D_mem'] <= metrics0['D_mem'] + 1e-9 and
            metrics1['D_id'] <= metrics0['D_id'] + 1e-9)



def _run_test(fn):
    try:
        fn()
        return True
    except AssertionError:
        return False

def main():
    tests = [
        ('T3 contradiction blocks consolidation', test_3_contradiction_blocks_consolidation),
        ('T6 kernel stability preserved', test_6_kernel_stability_preserved),
    ]
    passed = 0
    for name, fn in tests:
        ok = _run_test(fn)
        print(name, 'PASS' if ok else 'FAIL')
        passed += int(ok)
    print(f"\nCONSOLIDATION TESTS PASSED: {passed}/{len(tests)}")
    raise SystemExit(0 if passed == len(tests) else 1)


if __name__ == '__main__':
    main()
