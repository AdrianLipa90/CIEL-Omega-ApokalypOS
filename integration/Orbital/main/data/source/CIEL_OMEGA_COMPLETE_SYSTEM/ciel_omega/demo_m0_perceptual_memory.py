"""CIEL/Ω Demo - M0 Perceptual Memory v1"""

from ciel_omega.memory import IdentityField, PerceptualMemory


def main():
    identity = IdentityField(initial_phase=0.5)
    m0 = PerceptualMemory(identity)

    print('=== DEMO 1: repeated percept exposure ===')
    m0.observe('Flashing red light', 0.0, phase=0.55, salience=0.95, confidence=0.9)
    m0.observe('flashing red light', 0.2, phase=0.54, salience=0.95, confidence=0.9)
    item = m0.items['text:flashing red light']
    print('dominant key:', item.percept_key)
    print('activation:', round(item.activation, 3), 'exposures:', item.exposure_count)

    print('\n=== DEMO 2: fast decay / eviction ===')
    m0.observe('brief flicker', 0.0, phase=0.5, salience=0.35, confidence=0.4)
    before = m0.items['text:brief flicker'].status
    m0.decay(8.0)
    after = m0.items['text:brief flicker'].status
    print('brief flicker status:', before, '->', after)

    print('\n=== DEMO 3: retrieval ranking across modalities ===')
    m0.observe('sensor alert tone', 0.0, modality='audio', phase=0.5, salience=0.8, confidence=0.75)
    results = m0.retrieve('red light', top_k=3, include_decayed=True)
    for i, res in enumerate(results, 1):
        item = res['item']
        print(f"#{i}: key={item.percept_key} score={res['score']:.3f} salience={item.salience:.2f} status={item.status}")

    print('\n=== SNAPSHOT ===')
    snap = m0.snapshot(8.0)
    print('active_keys:', snap.active_keys)
    print('dominant:', snap.dominant_key, 'activation:', round(snap.dominant_activation, 3))


if __name__ == '__main__':
    main()
