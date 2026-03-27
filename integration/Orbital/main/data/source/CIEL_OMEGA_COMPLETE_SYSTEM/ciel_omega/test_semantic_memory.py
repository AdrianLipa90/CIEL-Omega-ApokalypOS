"""CIEL/Ω M3 Semantic Memory - Core Acceptance Tests 1,2,4,5,7"""

import numpy as np

from ciel_omega.memory import IdentityField, SemanticMemory, EpisodicMemory


def _episode(content, t, phase=0.4, salience=0.85, impact=0.85):
    episodic = EpisodicMemory()
    episodic.store(content, {
        'timestamp': float(t),
        'salience': salience,
        'identity_impact': impact,
    })
    ep = episodic.episodes[-1]
    ep.phase_at_storage = phase
    return ep


def test_1_repeated_episodes_create_candidate():
    print("\nTEST 1: repeated episodes -> semantic candidate")
    identity = IdentityField(initial_phase=0.5)
    m3 = SemanticMemory(identity)
    for i in range(3):
        ep = _episode("Adrian prefers rigor", i, phase=0.5 + 0.01 * i)
        m3.observe_episode(ep)
    cand = m3.check_semantic_candidate_creation("adrian prefers rigor")
    passed = cand is not None and cand.trace_support_count >= 3
    print("candidate:", cand)
    print("PASS" if passed else "FAIL")
    assert passed


def test_2_single_episode_no_item():
    print("\nTEST 2: single episode -> no semantic item")
    identity = IdentityField(initial_phase=0.5)
    m3 = SemanticMemory(identity)
    ep = _episode("Adrian prefers rigor", 0)
    m3.observe_episode(ep)
    m3.check_semantic_candidate_creation("adrian prefers rigor")
    item = m3.consolidate_candidate("adrian prefers rigor", current_time=1.0)
    passed = item is None and len(m3.items) == 0
    print("items:", len(m3.items))
    print("PASS" if passed else "FAIL")
    assert passed


def test_4_surface_duplicates_same_key():
    print("\nTEST 4: surface duplicates map to one semantic key")
    identity = IdentityField(initial_phase=0.5)
    m3 = SemanticMemory(identity)
    e1 = _episode("Adrian prefers rigor.", 0)
    e2 = _episode("  adrian   prefers   rigor  ", 1)
    t1 = m3.observe_episode(e1)
    t2 = m3.observe_episode(e2)
    passed = t1.semantic_key == t2.semantic_key == "adrian prefers rigor"
    print(t1.semantic_key, t2.semantic_key)
    print("PASS" if passed else "FAIL")
    assert passed


def test_5_retrieval_prefers_high_confidence_alignment():
    print("\nTEST 5: retrieval returns highest confidence and alignment")
    identity = IdentityField(initial_phase=0.5)
    m3 = SemanticMemory(identity)
    # strong item
    for i in range(4):
        ep = _episode("Adrian prefers rigor", i, phase=0.5 + 0.005 * i, salience=0.9, impact=0.9)
        m3.observe_episode(ep)
    for cycle in range(2):
        m3.check_semantic_candidate_creation("adrian prefers rigor")
    m3.consolidate_candidate("adrian prefers rigor", 10.0)

    # weaker item
    for i in range(4, 7):
        ep = _episode("Adrian likes speed", i, phase=1.9, salience=0.6, impact=0.55)
        m3.observe_episode(ep)
    m3.check_semantic_candidate_creation("adrian likes speed")

    results = m3.retrieve("Adrian prefers rigor", identity, top_k=2)
    passed = len(results) > 0 and results[0]['item'].semantic_key == 'adrian prefers rigor'
    print([(r['item'].semantic_key, round(r['score'], 3)) for r in results])
    print("PASS" if passed else "FAIL")
    assert passed


def test_7_no_direct_path_to_m6_or_identity_mutation():
    print("\nTEST 7: M3 does not modify IdentityField or create direct path to M6")
    identity = IdentityField(initial_phase=0.5)
    identity.anchors = ["anchor:a"]
    phase_before = identity.phase
    anchors_before = list(identity.anchors)
    m3 = SemanticMemory(identity)
    for i in range(3):
        ep = _episode("Adrian prefers rigor", i, phase=0.52)
        m3.observe_episode(ep)
    m3.check_semantic_candidate_creation("adrian prefers rigor")
    m3.consolidate_candidate("adrian prefers rigor", 5.0)
    passed = identity.phase == phase_before and identity.anchors == anchors_before
    print("identity phase:", identity.phase, "anchors:", identity.anchors)
    print("PASS" if passed else "FAIL")
    assert passed



def _run_test(fn):
    try:
        fn()
        return True
    except AssertionError:
        return False

def main():
    results = [
        _run_test(test_1_repeated_episodes_create_candidate),
        _run_test(test_2_single_episode_no_item),
        _run_test(test_4_surface_duplicates_same_key),
        _run_test(test_5_retrieval_prefers_high_confidence_alignment),
        _run_test(test_7_no_direct_path_to_m6_or_identity_mutation),
    ]
    print(f"\nCORE TESTS PASSED: {sum(results)}/{len(results)}")
    return all(results)


if __name__ == '__main__':
    ok = main()
    raise SystemExit(0 if ok else 1)
