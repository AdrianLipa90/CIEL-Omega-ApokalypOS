"""CIEL/Ω M1 Working Memory - Core tests."""

from memory import IdentityField, IdentityMemory, WorkingMemory, EpisodicMemory


def _episode(content, t, phase=0.5, salience=0.85, impact=0.6):
    episodic = EpisodicMemory()
    episodic.store(content, {
        'timestamp': float(t),
        'salience': salience,
        'identity_impact': impact,
    })
    ep = episodic.episodes[-1]
    ep.phase_at_storage = phase
    return ep


def test_1_reinforcement_increases_activation():
    identity = IdentityField(initial_phase=0.5)
    m1 = WorkingMemory(identity)
    m1.observe('active task focus', 0.0, phase=0.52, salience=0.8)
    a0 = m1.items['active task focus'].activation
    m1.observe('active task focus', 1.0, phase=0.51, salience=0.8)
    a1 = m1.items['active task focus'].activation
    assert a1 > a0


def test_2_decay_reduces_activation():
    identity = IdentityField(initial_phase=0.5)
    m1 = WorkingMemory(identity)
    m1.observe('transient cue', 0.0, phase=0.5, salience=0.8)
    a0 = m1.items['transient cue'].activation
    m1.decay(12.0)
    a1 = m1.items['transient cue'].activation
    assert a1 < a0


def test_3_surface_duplicates_merge():
    identity = IdentityField(initial_phase=0.5)
    m1 = WorkingMemory(identity)
    m1.observe('  Active TASK focus. ', 0.0, phase=0.5)
    m1.observe('active task   focus', 1.0, phase=0.5)
    assert len(m1.items) == 1 and 'active task focus' in m1.items


def test_4_retrieval_returns_best_item():
    identity = IdentityField(initial_phase=0.5)
    m1 = WorkingMemory(identity)
    m1.observe('active task focus', 0.0, phase=0.5, salience=0.9, confidence=0.9)
    m1.observe('active task focus', 1.0, phase=0.5, salience=0.9, confidence=0.9)
    m1.observe('weak side note', 0.0, phase=2.2, salience=0.4, confidence=0.4)
    results = m1.retrieve('task focus')
    assert len(results) > 0 and results[0]['item'].working_key == 'active task focus'


def test_5_no_direct_path_to_identity_or_m6():
    identity = IdentityField(initial_phase=0.5)
    identity.anchors = ['anchor:a']
    identity_phase = identity.phase
    anchors_before = list(identity.anchors)
    m6 = IdentityMemory(identity)
    m1 = WorkingMemory(identity)
    m1.observe('active task focus', 0.0, phase=0.55, salience=0.8)
    m1.observe('active task focus', 1.0, phase=0.55, salience=0.8)
    unchanged_identity = identity.phase == identity_phase and identity.anchors == anchors_before
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
        ('T1 reinforcement increases activation', test_1_reinforcement_increases_activation),
        ('T2 decay reduces activation', test_2_decay_reduces_activation),
        ('T3 surface duplicates merge', test_3_surface_duplicates_merge),
        ('T4 retrieval returns best item', test_4_retrieval_returns_best_item),
        ('T5 no direct path to identity/M6', test_5_no_direct_path_to_identity_or_m6),
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
