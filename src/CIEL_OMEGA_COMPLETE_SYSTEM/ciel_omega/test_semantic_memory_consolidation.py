"""CIEL/Ω M3 Semantic Memory - Consolidation and kernel tests 3,6"""

import numpy as np

from memory import IdentityField, SemanticMemory, EpisodicMemory, MemoryDynamicsEngine


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


def test_3_contradictions_block_consolidation():
    print("\nTEST 3: contradictory episodes do not consolidate")
    identity = IdentityField(initial_phase=0.5)
    m3 = SemanticMemory(identity)
    episodes = [
        _episode("Adrian prefers rigor", 0, 0.51),
        _episode("Adrian prefers rigor", 1, 0.49),
        _episode("Adrian does not prefer rigor", 2, 0.50),
        _episode("Adrian does not prefer rigor", 3, 0.48),
    ]
    for ep in episodes:
        m3.observe_episode(ep)
    cand = m3.check_semantic_candidate_creation("adrian prefers rigor")
    item = m3.consolidate_candidate("adrian prefers rigor", 5.0)
    passed = (item is None) or (item.status == 'contested')
    print("candidate:", cand)
    print("item:", item)
    print("PASS" if passed else "FAIL")
    assert passed


def test_6_kernel_stability_preserved():
    print("\nTEST 6: M3 does not destabilize local kernel")
    engine = MemoryDynamicsEngine()
    np.random.seed(42)
    initial_phases = np.random.randn(8) * 0.5
    state = engine.initialize_state(initial_phases, initial_identity_phase=0.0)
    V0 = engine.potential.compute_static_potential(state.phases, state.anchor_phases, engine.equilibrium_shifts)['V_static']
    Dm0 = engine.potential.compute_global_memory_defect(state.phases, engine.equilibrium_shifts)
    Di0 = engine.potential.compute_global_identity_defect(state.phases)
    final_state = engine.integrate(200, dt=0.1, input_forces=None)
    Vf = engine.potential.compute_static_potential(final_state.phases, final_state.anchor_phases, engine.equilibrium_shifts)['V_static']
    Dmf = engine.potential.compute_global_memory_defect(final_state.phases, engine.equilibrium_shifts)
    Dif = engine.potential.compute_global_identity_defect(final_state.phases)
    passed = Vf < V0 and Dmf < Dm0 and Dif < Di0
    print(f"V: {V0:.4f}->{Vf:.4f}; Dm: {Dm0:.4f}->{Dmf:.4f}; Di: {Di0:.4f}->{Dif:.4f}")
    print("PASS" if passed else "FAIL")
    assert passed



def _run_test(fn):
    try:
        fn()
        return True
    except AssertionError:
        return False

def main():
    results = [_run_test(test_3_contradictions_block_consolidation), _run_test(test_6_kernel_stability_preserved)]
    print(f"\nCONSOLIDATION TESTS PASSED: {sum(results)}/{len(results)}")
    return all(results)


if __name__ == '__main__':
    ok = main()
    raise SystemExit(0 if ok else 1)
