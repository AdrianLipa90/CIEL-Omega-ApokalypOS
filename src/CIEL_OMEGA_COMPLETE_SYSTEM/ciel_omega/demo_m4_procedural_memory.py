"""CIEL/Ω Demo - M4 Procedural Memory v1"""

from memory import IdentityField, ProceduralMemory, EpisodicMemory


def episode(content, t, goal='solve issue', action='run diagnostic', success=True, phase=0.5, salience=0.88, impact=0.80):
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


def main():
    identity = IdentityField(initial_phase=0.5)
    m4 = ProceduralMemory(identity)

    print('=== DEMO 1: repeated successful procedure ===')
    key = None
    for i in range(4):
        tr = m4.observe_episode(episode('Run diagnostic to solve issue', i, goal='solve issue', action='run diagnostic', success=True, phase=0.5 + 0.01*i))
        key = tr.procedure_key
    for cycle in range(2):
        cand = m4.check_candidate_creation(key)
        print(f'cycle {cycle+1}: candidate=', cand.status if cand else None, 'confirmations=', cand.candidate_confirmation_count if cand else 0)
    item = m4.consolidate_candidate(key, 10.0)
    print('consolidated item:', item.canonical_action if item else None)

    print('\n=== DEMO 2: contradiction blocks consolidation ===')
    m4b = ProceduralMemory(identity)
    trace_good = None
    for i in range(3):
        trace_good = m4b.observe_episode(episode('Run diagnostic to solve issue', i, goal='solve issue', action='run diagnostic', success=True, phase=0.5 + 0.01*i))
    for i in range(3,6):
        m4b.observe_episode(episode('Restart service to solve issue', i, goal='solve issue', action='restart service', success=True, phase=1.8))
    cand2 = m4b.check_candidate_creation(trace_good.procedure_key)
    item2 = m4b.consolidate_candidate(trace_good.procedure_key, 10.0)
    print('candidate contradiction:', round(cand2.contradiction_score, 3) if cand2 else None)
    print('consolidated item:', item2)

    print('\n=== DEMO 3: retrieval ranking ===')
    results = m4.retrieve('solve issue', top_k=3)
    for i, res in enumerate(results, 1):
        item = res['item']
        print(f'#{i}: goal={item.goal_key} action={item.canonical_action} score={res["score"]:.3f} success={item.success_rate:.2f}')


if __name__ == '__main__':
    main()
