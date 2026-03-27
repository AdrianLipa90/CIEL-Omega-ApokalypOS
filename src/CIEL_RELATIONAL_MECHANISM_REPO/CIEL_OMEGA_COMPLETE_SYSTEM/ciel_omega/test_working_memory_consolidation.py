"""CIEL/Ω M1 Working Memory - kernel stability and operational tests."""

import numpy as np

from memory import IdentityField, WorkingMemory, MemoryDynamicsEngine


def test_6_kernel_stability_preserved():
    identity = IdentityField(initial_phase=0.5)
    m1 = WorkingMemory(identity)
    m1.observe('active task focus', 0.0, phase=0.52, salience=0.9, confidence=0.9)
    m1.observe('active task focus', 1.0, phase=0.51, salience=0.85, confidence=0.85)

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


def test_7_singleton_decays_without_reinforcement():
    identity = IdentityField(initial_phase=0.5)
    m1 = WorkingMemory(identity)
    m1.observe('single cue', 0.0, phase=0.5, salience=0.6, confidence=0.5)
    before = m1.items['single cue'].status
    m1.decay(25.0)
    after = m1.items['single cue'].status
    print('before:', before, 'after:', after)
    ok = after in {'decayed', 'evicted'}
    print('PASS' if ok else 'FAIL')
    assert ok



def _run_test(fn):
    try:
        fn()
        return True
    except AssertionError:
        return False

def main():
    results = [_run_test(test_6_kernel_stability_preserved), _run_test(test_7_singleton_decays_without_reinforcement)]
    print(f"\nCONSOLIDATION TESTS PASSED: {sum(results)}/{len(results)}")
    raise SystemExit(0 if all(results) else 1)


if __name__ == '__main__':
    main()
