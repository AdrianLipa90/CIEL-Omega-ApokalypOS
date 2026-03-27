"""CIEL/Ω M5 Affective/Ethical Memory - Core tests."""

from memory import IdentityField, AffectiveEthicalMemory, EpisodicMemory


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


def test_1_repeated_alerts_create_candidate():
    identity = IdentityField(initial_phase=0.5)
    m5 = AffectiveEthicalMemory(identity)
    for i in range(3):
        ep = _episode("Warning: risk of harm", i, phase=0.5 + 0.01 * i, ethical_risk=0.9, arousal=0.8)
        m5.observe_episode(ep)
    cand = m5.check_candidate_creation("warning risk of harm")
    assert cand is not None and cand.trace_support_count >= 3 and cand.polarity == 'alert'


def test_2_single_episode_no_item():
    identity = IdentityField(initial_phase=0.5)
    m5 = AffectiveEthicalMemory(identity)
    ep = _episode("Warning: risk of harm", 0, ethical_risk=0.9)
    m5.observe_episode(ep)
    m5.check_candidate_creation("warning risk of harm")
    item = m5.consolidate_candidate("warning risk of harm", 1.0)
    assert item is None and len(m5.items) == 0


def test_4_retrieval_prefers_high_salience_alignment():
    identity = IdentityField(initial_phase=0.5)
    m5 = AffectiveEthicalMemory(identity)
    for i in range(4):
        ep = _episode("Warning: risk of harm", i, phase=0.5 + 0.01 * i, ethical_risk=0.95, arousal=0.9)
        m5.observe_episode(ep)
    for _ in range(2):
        m5.check_candidate_creation("warning risk of harm")
    m5.consolidate_candidate("warning risk of harm", 10.0)
    for i in range(4,7):
        ep = _episode("Helpful support available", i, phase=1.7, protective_score=0.6, arousal=0.4)
        m5.observe_episode(ep)
    m5.check_candidate_creation("helpful support available")
    results = m5.retrieve("risk of harm", identity, top_k=2)
    assert len(results) > 0 and results[0]['item'].affective_key == 'warning risk of harm'


def test_5_no_direct_path_to_m6_or_identity_mutation():
    identity = IdentityField(initial_phase=0.5)
    identity.anchors = ['anchor:a']
    m5 = AffectiveEthicalMemory(identity)
    phase_before = identity.phase
    anchors_before = list(identity.anchors)
    for i in range(3):
        ep = _episode("Warning: risk of harm", i, phase=0.52, ethical_risk=0.9)
        m5.observe_episode(ep)
    m5.check_candidate_creation("warning risk of harm")
    m5.consolidate_candidate("warning risk of harm", 5.0)
    assert identity.phase == phase_before and identity.anchors == anchors_before



def _run_test(fn):
    try:
        fn()
        return True
    except AssertionError:
        return False

def main():
    tests = [
        ("T1 repeated alerts -> candidate", test_1_repeated_alerts_create_candidate),
        ("T2 single episode -> no item", test_2_single_episode_no_item),
        ("T4 retrieval prioritizes best item", test_4_retrieval_prefers_high_salience_alignment),
        ("T5 no direct path to M6 / no identity mutation", test_5_no_direct_path_to_m6_or_identity_mutation),
    ]
    passed=0
    for name, fn in tests:
        ok=_run_test(fn)
        print(name, 'PASS' if ok else 'FAIL')
        passed += int(ok)
    print(f"\nCORE TESTS PASSED: {passed}/{len(tests)}")
    raise SystemExit(0 if passed == len(tests) else 1)


if __name__ == '__main__':
    main()
