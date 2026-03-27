"""Demo for M5 Affective/Ethical Memory v1."""

from ciel_omega.memory import IdentityField, AffectiveEthicalMemory, EpisodicMemory


def make_episode(content, t, phase=0.5, salience=0.85, impact=0.85, **ctx):
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


def main():
    identity = IdentityField(initial_phase=0.5)
    m5 = AffectiveEthicalMemory(identity)

    print("=== DEMO 1: repeated alert ===")
    for i in range(4):
        ep = make_episode("Warning: risk of harm", i, phase=0.5 + 0.01*i, ethical_risk=0.92, arousal=0.85)
        tr = m5.observe_episode(ep)
        print(f"obs {i}: polarity={tr.polarity} risk={tr.ethical_risk:.2f} align={tr.identity_alignment:.2f}")
    for cycle in range(2):
        cand = m5.check_candidate_creation("warning risk of harm")
        print(f"cycle {cycle}: candidate={cand is not None}, confirmations={cand.candidate_confirmation_count if cand else 0}")
    item = m5.consolidate_candidate("warning risk of harm", current_time=10.0)
    print("consolidated:", item is not None, item)

    print("\n=== DEMO 2: contradiction ===")
    for i in range(4,6):
        ep = make_episode("Operation is safe", i, phase=0.5, protective_score=0.95, arousal=0.3)
        tr = m5.observe_episode(ep)
        print(f"obs {i}: text={tr.content} polarity={tr.polarity} protect={tr.protective_score:.2f}")
    for i in range(6,8):
        ep = make_episode("Operation is not safe", i, phase=0.5, ethical_risk=0.95, arousal=0.8)
        tr = m5.observe_episode(ep)
        print(f"obs {i}: text={tr.content} polarity={tr.polarity} risk={tr.ethical_risk:.2f}")
    cand = m5.check_candidate_creation("operation is safe")
    item = m5.consolidate_candidate("operation is safe", current_time=20.0)
    print("candidate:", cand)
    print("consolidated item:", item)

    print("\n=== DEMO 3: retrieval ===")
    results = m5.retrieve("risk of harm", identity, top_k=3)
    for i, row in enumerate(results, 1):
        item = row['item']
        print(f"{i}. key={item.affective_key} polarity={item.polarity} score={row['score']:.3f} conf={row['confidence']:.3f} status={row['status']}")


if __name__ == '__main__':
    main()
