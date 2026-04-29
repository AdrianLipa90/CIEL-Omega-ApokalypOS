"""CIEL/Ω M0 Perceptual Memory - Core tests."""

from memory import IdentityField, IdentityMemory, PerceptualMemory


def test_1_repeated_exposure_increases_activation():
    identity = IdentityField(initial_phase=0.5)
    m0 = PerceptualMemory(identity)
    m0.observe('flashing red light', 0.0, phase=0.55, salience=0.85, confidence=0.8)
    a0 = m0.items['text:flashing red light'].activation
    m0.observe('flashing red light', 0.2, phase=0.54, salience=0.85, confidence=0.8)
    a1 = m0.items['text:flashing red light'].activation
    assert a1 > a0


def test_2_decay_reduces_activation():
    identity = IdentityField(initial_phase=0.5)
    m0 = PerceptualMemory(identity)
    m0.observe('transient sensor spike', 0.0, phase=0.5, salience=0.8)
    a0 = m0.items['text:transient sensor spike'].activation
    m0.decay(5.0)
    a1 = m0.items['text:transient sensor spike'].activation
    assert a1 < a0


def test_3_surface_duplicates_merge():
    identity = IdentityField(initial_phase=0.5)
    m0 = PerceptualMemory(identity)
    m0.observe('  Flashing RED light. ', 0.0, phase=0.5)
    m0.observe('flashing   red light', 0.1, phase=0.5)
    assert len(m0.items) == 1 and 'text:flashing red light' in m0.items


def test_4_retrieval_returns_dominant_percept():
    identity = IdentityField(initial_phase=0.5)
    m0 = PerceptualMemory(identity)
    m0.observe('flashing red light', 0.0, phase=0.5, salience=0.95, confidence=0.9)
    m0.observe('flashing red light', 0.1, phase=0.5, salience=0.95, confidence=0.9)
    m0.observe('background hum', 0.0, phase=2.0, salience=0.3, confidence=0.5)
    results = m0.retrieve('red light')
    assert len(results) > 0 and results[0]['item'].percept_key == 'text:flashing red light'


def test_5_no_direct_path_to_identity_or_m6():
    identity = IdentityField(initial_phase=0.5)
    identity.anchors = ['anchor:a']
    phase_before = identity.phase
    anchors_before = list(identity.anchors)
    m6 = IdentityMemory(identity)
    m0 = PerceptualMemory(identity)
    m0.observe('flashing red light', 0.0, phase=0.55, salience=0.85)
    m0.observe('flashing red light', 0.2, phase=0.54, salience=0.85)
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
        ('T1 repeated exposure increases activation', test_1_repeated_exposure_increases_activation),
        ('T2 decay reduces activation', test_2_decay_reduces_activation),
        ('T3 surface duplicates merge', test_3_surface_duplicates_merge),
        ('T4 retrieval returns dominant percept', test_4_retrieval_returns_dominant_percept),
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
