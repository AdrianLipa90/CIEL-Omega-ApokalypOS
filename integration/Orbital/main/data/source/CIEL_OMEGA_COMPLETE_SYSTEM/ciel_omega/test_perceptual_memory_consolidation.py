"""CIEL/Ω M0 Perceptual Memory - decay / kernel stability tests."""

import numpy as np

from ciel_omega.memory import IdentityField, PerceptualMemory, MemoryDynamicsEngine


def test_6_kernel_stability_preserved():
    identity = IdentityField(initial_phase=0.5)
    m0 = PerceptualMemory(identity)
    m0.observe('flashing red light', 0.0, phase=0.52, salience=0.95, confidence=0.9)
    m0.observe('sensor alert tone', 0.2, modality='audio', phase=0.50, salience=0.9, confidence=0.85)

    engine = MemoryDynamicsEngine()
    np.random.seed(42)
    state = engine.initialize_state(np.random.randn(8) * 0.5, initial_identity_phase=0.0)
    potential = engine.potential
    V0 = potential.compute_static_potential(state.phases, state.anchor_phases, engine.equilibrium_shifts)['V_static']
    Dm0 = potential.compute_global_memory_defect(state.phases, engine.equilibrium_shifts)
    Di0 = potential.compute_global_identity_defect(state.phases)
    final_state = engine.integrate(200, dt=0.1, input_forces=None)
    Vf = potential.compute_static_potential(final_state.phases, final_state.anchor_phases, engine.equilibrium_shifts)['V_static']
    Dmf = potential.compute_global_memory_defect(final_state.phases, engine.equilibrium_shifts)
    Dif = potential.compute_global_identity_defect(final_state.phases)
    print(f"V: {V0:.4f}->{Vf:.4f}; Dm: {Dm0:.4f}->{Dmf:.4f}; Di: {Di0:.4f}->{Dif:.4f}")
    ok = Vf < V0 and Dmf < Dm0 and Dif < Di0
    print('PASS' if ok else 'FAIL')
    assert ok


def test_7_ephemeral_item_evicted_without_reinforcement():
    identity = IdentityField(initial_phase=0.5)
    m0 = PerceptualMemory(identity)
    m0.observe('brief flicker', 0.0, phase=0.5, salience=0.35, confidence=0.4)
    before = m0.items['text:brief flicker'].status
    m0.decay(8.0)
    after = m0.items['text:brief flicker'].status
    print('before:', before, 'after:', after)
    ok = after in {'decayed', 'evicted'}
    print('PASS' if ok else 'FAIL')
    assert ok


def main():
    results = [test_6_kernel_stability_preserved(), test_7_ephemeral_item_evicted_without_reinforcement()]
    print(f"\nCONSOLIDATION TESTS PASSED: {sum(results)}/{len(results)}")
    raise SystemExit(0 if all(results) else 1)


if __name__ == '__main__':
    main()
