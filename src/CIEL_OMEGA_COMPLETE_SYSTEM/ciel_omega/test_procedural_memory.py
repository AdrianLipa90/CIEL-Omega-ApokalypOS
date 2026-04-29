"""CIEL/Ω M4 Procedural Memory - Core Acceptance Tests 1,2,4,5,7"""

from memory import IdentityField, ProceduralMemory, EpisodicMemory, IdentityMemory


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


def test_1_repeated_success_creates_candidate():
    identity = IdentityField(initial_phase=0.5)
    m4 = ProceduralMemory(identity)
    for i in range(3):
        ep = _episode('Run diagnostic to solve issue', i, phase=0.5 + 0.01 * i)
        trace = m4.observe_episode(ep)
    cand = m4.check_candidate_creation(trace.procedure_key)
    assert cand is not None and cand.trace_support_count >= 3


def test_2_single_episode_no_item():
    identity = IdentityField(initial_phase=0.5)
    m4 = ProceduralMemory(identity)
    ep = _episode('Run diagnostic once', 0)
    trace = m4.observe_episode(ep)
    m4.check_candidate_creation(trace.procedure_key)
    item = m4.consolidate_candidate(trace.procedure_key, 1.0)
    assert item is None and len(m4.items) == 0


def test_4_surface_duplicates_same_key():
    identity = IdentityField(initial_phase=0.5)
    m4 = ProceduralMemory(identity)
    e1 = _episode('Run diagnostic', 0, action='Run Diagnostic!')
    e2 = _episode('run diagnostic', 1, action='run   diagnostic')
    t1 = m4.observe_episode(e1)
    t2 = m4.observe_episode(e2)
    assert t1.procedure_key == t2.procedure_key


def test_5_retrieval_returns_best_procedure():
    identity = IdentityField(initial_phase=0.5)
    m4 = ProceduralMemory(identity)
    # strong procedure
    key = None
    for i in range(4):
        ep = _episode('Run diagnostic to solve issue', i, goal='solve issue', action='run diagnostic', success=True, phase=0.5 + 0.005 * i, salience=0.92, impact=0.9)
        tr = m4.observe_episode(ep)
        key = tr.procedure_key
    for _ in range(2):
        m4.check_candidate_creation(key)
    m4.consolidate_candidate(key, 10.0)

    # weaker procedure
    weak_key = None
    for i in range(4,7):
        ep = _episode('Inspect logs', i, goal='solve issue', action='inspect logs', success=True, phase=1.6, salience=0.6, impact=0.55)
        tr = m4.observe_episode(ep)
        weak_key = tr.procedure_key
    m4.check_candidate_creation(weak_key)

    results = m4.retrieve('solve issue')
    assert len(results) > 0 and results[0]['item'].procedure_key == key


def test_7_no_direct_path_to_identity_or_m6():
    identity = IdentityField(initial_phase=0.5)
    identity.anchors = ['anchor:a']
    phase_before = identity.phase
    anchors_before = list(identity.anchors)
    m6 = IdentityMemory(identity)
    m4 = ProceduralMemory(identity)
    for i in range(3):
        ep = _episode('Run diagnostic to solve issue', i, phase=0.52)
        tr = m4.observe_episode(ep)
    m4.check_candidate_creation(tr.procedure_key)
    m4.consolidate_candidate(tr.procedure_key, 5.0)
    unchanged_identity = identity.phase == phase_before and identity.anchors == anchors_before
    unchanged_m6 = len(m6.traces) == 0 and len(m6.anchor_candidates) == 0
    assert unchanged_identity and unchanged_m6



def _run_test(fn):
    try:
        fn()
        return True
    except AssertionError:
        return False

def main():
    tests = [
        ('T1 repeated success creates candidate', test_1_repeated_success_creates_candidate),
        ('T2 single episode no item', test_2_single_episode_no_item),
        ('T4 surface duplicates same key', test_4_surface_duplicates_same_key),
        ('T5 retrieval returns best procedure', test_5_retrieval_returns_best_procedure),
        ('T7 no direct path to identity/M6', test_7_no_direct_path_to_identity_or_m6),
    ]
    passed = 0
    for name, fn in tests:
        ok = _run_test(fn)
        print(name, 'PASS' if ok else 'FAIL')
        passed += int(ok)
    print(f"\nCORE TESTS PASSED: {passed}/{len(tests)}")
    raise SystemExit(0 if passed == len(tests) else 1)


if __name__ == '__main__':
    main()
