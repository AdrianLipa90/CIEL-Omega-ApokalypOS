"""CIEL/Ω M3 Semantic Memory demo."""

from memory import IdentityField, SemanticMemory, EpisodicMemory


def _episode(content, t, phase=0.5, salience=0.85, impact=0.85):
    episodic = EpisodicMemory()
    episodic.store(content, {
        'timestamp': float(t),
        'salience': salience,
        'identity_impact': impact,
    })
    ep = episodic.episodes[-1]
    ep.phase_at_storage = phase
    return ep


def demo_repeated_fact():
    print("\n" + "="*70)
    print("DEMO 1: REPEATED FACT -> CANDIDATE -> CONSOLIDATED ITEM")
    print("="*70)
    identity = IdentityField(initial_phase=0.5)
    m3 = SemanticMemory(identity)
    for i in range(4):
        m3.observe_episode(_episode("Adrian prefers rigor", i, 0.5 + 0.01*i))
        cand = m3.check_semantic_candidate_creation("adrian prefers rigor")
        if cand:
            print(f"cycle {i}: confirmations={cand.candidate_confirmation_count}, score={m3.compute_consolidation_score('adrian prefers rigor').compute_total():.3f}")
    item = m3.consolidate_candidate("adrian prefers rigor", 10.0)
    print("candidate:", m3.candidates.get("adrian prefers rigor"))
    print("item:", item)
    return m3


def demo_contradiction():
    print("\n" + "="*70)
    print("DEMO 2: CONTRADICTION -> NO CONSOLIDATION OR CONTESTED")
    print("="*70)
    identity = IdentityField(initial_phase=0.5)
    m3 = SemanticMemory(identity)
    texts = [
        "Adrian prefers rigor",
        "Adrian prefers rigor",
        "Adrian does not prefer rigor",
        "Adrian does not prefer rigor",
    ]
    for i, text in enumerate(texts):
        m3.observe_episode(_episode(text, i, 0.5))
    cand = m3.check_semantic_candidate_creation("adrian prefers rigor")
    item = m3.consolidate_candidate("adrian prefers rigor", 10.0)
    print("candidate:", cand)
    print("item:", item)
    print("status:", None if item is None else item.status)
    return m3


def demo_retrieval():
    print("\n" + "="*70)
    print("DEMO 3: RETRIEVAL")
    print("="*70)
    identity = IdentityField(initial_phase=0.5)
    m3 = SemanticMemory(identity)
    for i in range(4):
        m3.observe_episode(_episode("Adrian prefers rigor", i, 0.5 + 0.01*i))
    for _ in range(2):
        m3.check_semantic_candidate_creation("adrian prefers rigor")
    m3.consolidate_candidate("adrian prefers rigor", 10.0)

    for i in range(4, 7):
        m3.observe_episode(_episode("Adrian likes speed", i, 1.8, 0.65, 0.55))
    m3.check_semantic_candidate_creation("adrian likes speed")

    results = m3.retrieve("Adrian prefers rigor", identity, top_k=5)
    for idx, r in enumerate(results, 1):
        item = r['item']
        print(f"{idx}. key={item.semantic_key} score={r['score']:.3f} conf={r['confidence']:.3f} align={r['alignment']:.3f} status={r['status']}")
    return m3


def main():
    demo_repeated_fact()
    demo_contradiction()
    demo_retrieval()


if __name__ == '__main__':
    main()
