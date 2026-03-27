"""Demo for M1 Working Memory v1."""

from ciel_omega.memory import IdentityField, WorkingMemory


def main():
    identity = IdentityField(initial_phase=0.5)
    m1 = WorkingMemory(identity)

    print('=' * 70)
    print('DEMO 1 — reinforcement and active context')
    print('=' * 70)
    m1.observe('active task focus', 0.0, phase=0.52, salience=0.9, confidence=0.85)
    m1.observe('active task focus', 1.0, phase=0.51, salience=0.85, confidence=0.90)
    m1.observe('secondary note', 1.5, phase=1.8, salience=0.45, confidence=0.5)
    for key, item in m1.items.items():
        print(key, 'activation=', round(item.activation, 3), 'status=', item.status)

    print('\n' + '=' * 70)
    print('DEMO 2 — decay without reinforcement')
    print('=' * 70)
    m1.decay(18.0)
    for key, item in m1.items.items():
        print(key, 'activation=', round(item.activation, 3), 'status=', item.status)

    print('\n' + '=' * 70)
    print('DEMO 3 — retrieval ranking')
    print('=' * 70)
    results = m1.retrieve('task focus', top_k=3, include_decayed=True)
    for r in results:
        item = r['item']
        print(item.working_key, 'score=', round(r['score'], 3), 'activation=', round(item.activation, 3), 'status=', item.status)

    print('\n' + '=' * 70)
    print('SNAPSHOT')
    print('=' * 70)
    snap = m1.snapshot(18.0)
    print(snap)


if __name__ == '__main__':
    main()
