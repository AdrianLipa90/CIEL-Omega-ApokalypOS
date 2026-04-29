"""CIEL/Ω M6.1 Patch - Acceptance Tests A-F

Tests specified by Adrian for M6.1 patch validation.

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

import numpy as np

from memory import (
    IdentityField,
    IdentityMemory,
    MemoryDynamicsEngine,
    MemoryPotential,
)


def test_a_consistent_pattern_reaches_maturity():
    """TEST A: Consistent long pattern creates mature candidate"""
    print("\n" + "="*70)
    print("TEST A: CONSISTENT PATTERN → MATURE CANDIDATE")
    print("="*70)
    
    np.random.seed(100)
    identity_field = IdentityField(initial_phase=0.5)
    identity_memory = IdentityMemory(identity_field)
    
    print("\nSimulating consistent pattern (σ=0.01) with multiple confirmations...")
    
    # Observe and confirm multiple times
    for cycle in range(4):  # 4 confirmation cycles
        for t in range(10):
            identity_field.phase = 0.5 + np.random.randn() * 0.01
            identity_memory.observe_identity_field(current_time=float(cycle*10 + t))
        
        # Check candidate at end of each cycle
        candidate = identity_memory.check_anchor_candidate_creation(
            current_time=float((cycle+1)*10),
            anchor_key="consistent_pattern",
            proposed_phase=0.5
        )
        
        if candidate:
            # Check maturity with explicit thresholds from IdentityMemory
            is_mature = candidate.is_mature(
                identity_memory.MIN_CONFIRMATIONS,
                identity_memory.MIN_MATURE_ALIGNMENT,
                identity_memory.MIN_MATURE_STABILITY,
                identity_memory.MAX_MATURE_CONTRADICTION
            )
            print(f"  Cycle {cycle+1}: confirmations={candidate.candidate_confirmation_count}, "
                  f"stability={candidate.mean_stability:.3f}, mature={is_mature}")
    
    stats = identity_memory.get_statistics()
    score = identity_memory.compute_consolidation_score()
    
    print(f"\nFinal state:")
    print(f"  Detected candidates: {stats['detected_candidates']}")
    print(f"  Mature candidates: {stats['mature_candidates']}")
    print(f"  Final stability: {score.stability:.3f}")
    
    mature_list = identity_memory.get_mature_candidates()
    passed = len(mature_list) > 0
    
    if passed:
        print("\n✓ TEST A PASSED: Consistent pattern reached maturity")
        print(f"   Mature candidate: {mature_list[0]}")
    else:
        print("\n✗ TEST A FAILED: Consistent pattern did not reach maturity")
        if candidate:
            print(f"   Confirmations: {candidate.candidate_confirmation_count}/3")
            print(f"   Stability: {candidate.mean_stability:.3f}/0.85")
    
    assert passed


def test_b_short_pattern_no_candidate():
    """TEST B: Short pattern (5 obs) does not create candidate"""
    print("\n" + "="*70)
    print("TEST B: SHORT PATTERN → NO CANDIDATE")
    print("="*70)
    
    identity_field = IdentityField(initial_phase=0.5)
    identity_memory = IdentityMemory(identity_field)
    
    print("\nSimulating SHORT pattern (5 observations)...")
    
    for t in range(5):
        identity_field.phase = 0.5 + np.random.randn() * 0.01
        identity_memory.observe_identity_field(current_time=float(t))
    
    candidate = identity_memory.check_anchor_candidate_creation(
        current_time=5.0,
        anchor_key="short_pattern",
        proposed_phase=0.5
    )
    
    stats = identity_memory.get_statistics()
    
    print(f"\nResults:")
    print(f"  Traces: {stats['trace_count']}")
    print(f"  Detected candidates: {stats['detected_candidates']}")
    print(f"  Candidate created: {candidate is not None}")
    
    passed = (candidate is None)
    
    if passed:
        print("\n✓ TEST B PASSED: Short pattern blocked (insufficient traces)")
    else:
        print("\n✗ TEST B FAILED: Short pattern created candidate")
    
    assert passed


def test_c_inconsistent_pattern_no_maturity():
    """TEST C: Inconsistent pattern does not reach maturity"""
    print("\n" + "="*70)
    print("TEST C: INCONSISTENT PATTERN → NO MATURE CANDIDATE")
    print("="*70)
    
    np.random.seed(42)
    identity_field = IdentityField(initial_phase=0.5)
    identity_memory = IdentityMemory(identity_field)
    
    print("\nSimulating INCONSISTENT pattern (σ=0.3) with confirmation attempts...")
    
    # Try to confirm multiple times
    for cycle in range(4):
        for t in range(10):
            identity_field.phase = 0.5 + np.random.randn() * 0.3  # High variance
            identity_memory.observe_identity_field(current_time=float(cycle*10 + t))
        
        candidate = identity_memory.check_anchor_candidate_creation(
            current_time=float((cycle+1)*10),
            anchor_key="inconsistent_pattern",
            proposed_phase=0.5
        )
        
        if candidate:
            # Check maturity with explicit thresholds
            is_mature = candidate.is_mature(
                identity_memory.MIN_CONFIRMATIONS,
                identity_memory.MIN_MATURE_ALIGNMENT,
                identity_memory.MIN_MATURE_STABILITY,
                identity_memory.MAX_MATURE_CONTRADICTION
            )
            print(f"  Cycle {cycle+1}: stability={candidate.mean_stability:.3f}, "
                  f"mature={is_mature}")
    
    stats = identity_memory.get_statistics()
    score = identity_memory.compute_consolidation_score()
    
    print(f"\nFinal state:")
    print(f"  Detected candidates: {stats['detected_candidates']}")
    print(f"  Mature candidates: {stats['mature_candidates']}")
    print(f"  Final stability: {score.stability:.3f}")
    print(f"  Maturity threshold: 0.85")
    
    passed = (stats['mature_candidates'] == 0)
    
    if passed:
        print("\n✓ TEST C PASSED: Inconsistent pattern blocked from maturity")
        print(f"   (stability {score.stability:.3f} < 0.85)")
    else:
        print("\n✗ TEST C FAILED: Inconsistent pattern reached maturity")
    
    assert passed


def test_d_single_episode_no_candidate():
    """TEST D: Single episode does not create candidate"""
    print("\n" + "="*70)
    print("TEST D: SINGLE EPISODE → NO CANDIDATE")
    print("="*70)
    
    identity_field = IdentityField(initial_phase=0.5)
    identity_memory = IdentityMemory(identity_field)
    
    print("\nSimulating SINGLE episode...")
    
    identity_memory.observe_identity_field(current_time=1.0)
    
    candidate = identity_memory.check_anchor_candidate_creation(
        current_time=1.0,
        anchor_key="single_episode",
        proposed_phase=0.5
    )
    
    stats = identity_memory.get_statistics()
    
    print(f"\nResults:")
    print(f"  Traces: {stats['trace_count']}")
    print(f"  Candidate created: {candidate is not None}")
    
    passed = (candidate is None)
    
    if passed:
        print("\n✓ TEST D PASSED: Single episode blocked")
    else:
        print("\n✗ TEST D FAILED: Single episode created candidate")
    
    assert passed


def test_e_kernel_stability_preserved():
    """TEST E: M6.1 does not destabilize kernel"""
    print("\n" + "="*70)
    print("TEST E: KERNEL STABILITY WITH M6.1")
    print("="*70)
    
    engine = MemoryDynamicsEngine()
    potential = engine.potential
    
    np.random.seed(42)
    initial_phases = np.random.randn(8) * 0.5
    state = engine.initialize_state(initial_phases, initial_identity_phase=0.0)
    
    V_static_0 = potential.compute_static_potential(
        state.phases, state.anchor_phases, engine.equilibrium_shifts
    )['V_static']
    
    D_mem_0 = potential.compute_global_memory_defect(
        state.phases, engine.equilibrium_shifts
    )
    
    D_id_0 = potential.compute_global_identity_defect(state.phases)
    
    print(f"\nInitial state:")
    print(f"  V_static: {V_static_0:.4f}")
    print(f"  D_mem:    {D_mem_0:.4f}")
    print(f"  D_id:     {D_id_0:.4f}")
    
    print("\nIntegrating for 200 steps (dt=0.1)...")
    final_state = engine.integrate(200, dt=0.1, input_forces=None)
    
    V_static_f = potential.compute_static_potential(
        final_state.phases, final_state.anchor_phases, engine.equilibrium_shifts
    )['V_static']
    
    D_mem_f = potential.compute_global_memory_defect(
        final_state.phases, engine.equilibrium_shifts
    )
    
    D_id_f = potential.compute_global_identity_defect(final_state.phases)
    
    print(f"\nFinal state:")
    print(f"  V_static: {V_static_f:.4f}")
    print(f"  D_mem:    {D_mem_f:.4f}")
    print(f"  D_id:     {D_id_f:.4f}")
    
    print(f"\nChanges:")
    print(f"  ΔV_static: {V_static_f - V_static_0:+.4f}")
    print(f"  ΔD_mem:    {D_mem_f - D_mem_0:+.4f}")
    print(f"  ΔD_id:     {D_id_f - D_id_0:+.4f}")
    
    V_decreased = V_static_f < V_static_0
    D_mem_decreased = D_mem_f < D_mem_0
    D_id_decreased = D_id_f < D_id_0
    
    passed = V_decreased and D_mem_decreased and D_id_decreased
    
    print(f"\nStability checks:")
    print(f"  V_static decreased: {V_decreased} {'✓' if V_decreased else '✗'}")
    print(f"  D_mem decreased:    {D_mem_decreased} {'✓' if D_mem_decreased else '✗'}")
    print(f"  D_id decreased:     {D_id_decreased} {'✓' if D_id_decreased else '✗'}")
    
    if passed:
        print("\n✓ TEST E PASSED: Kernel stability preserved with M6.1")
    else:
        print("\n✗ TEST E FAILED: Kernel stability compromised")
    
    assert passed


def test_f_field_separation():
    """TEST F: trace_support_count != candidate_confirmation_count semantically"""
    print("\n" + "="*70)
    print("TEST F: SEPARATION OF CONFIRMATION LEVELS")
    print("="*70)
    
    identity_field = IdentityField(initial_phase=0.5)
    identity_memory = IdentityMemory(identity_field)
    
    print("\nBuilding candidate with multiple confirmation cycles...")
    
    # Cycle 1: Initial detection
    for t in range(15):
        identity_field.phase = 0.5 + np.random.randn() * 0.01
        identity_memory.observe_identity_field(current_time=float(t))
    
    cand1 = identity_memory.check_anchor_candidate_creation(15.0, "test", 0.5)
    
    # Cycle 2: Second confirmation
    for t in range(15, 30):
        identity_field.phase = 0.5 + np.random.randn() * 0.01
        identity_memory.observe_identity_field(current_time=float(t))
    
    cand2 = identity_memory.check_anchor_candidate_creation(30.0, "test", 0.5)
    
    print(f"\nAfter cycle 1:")
    if cand1:
        print(f"  trace_support_count: {cand1.trace_support_count}")
        print(f"  candidate_confirmation_count: {cand1.candidate_confirmation_count}")
    
    print(f"\nAfter cycle 2:")
    if cand2:
        print(f"  trace_support_count: {cand2.trace_support_count}")
        print(f"  candidate_confirmation_count: {cand2.candidate_confirmation_count}")
    
    # Check semantic separation
    if cand2:
        trace_count = cand2.trace_support_count
        confirm_count = cand2.candidate_confirmation_count
        
        fields_exist = hasattr(cand2, 'trace_support_count') and hasattr(cand2, 'candidate_confirmation_count')
        different_values = trace_count != confirm_count
        confirm_incremented = confirm_count == 2
        
        passed = fields_exist and different_values and confirm_incremented
        
        print(f"\nVerification:")
        print(f"  Both fields exist: {fields_exist}")
        print(f"  Different values: {different_values}")
        print(f"  Confirmation count incremented: {confirm_incremented}")
        
        if passed:
            print("\n✓ TEST F PASSED: Confirmation levels properly separated")
            print(f"   trace_support (window size) = {trace_count}")
            print(f"   candidate_confirmation (cycles) = {confirm_count}")
        else:
            print("\n✗ TEST F FAILED: Separation incomplete")
    else:
        passed = False
        print("\n✗ TEST F FAILED: No candidate created")
    
    assert passed



def _run_test(fn):
    try:
        fn()
        return True
    except AssertionError:
        return False

def main():
    """Run all M6.1 acceptance tests"""
    print("="*70)
    print("CIEL/Ω M6.1 PATCH - ACCEPTANCE TESTS A-F")
    print("="*70)
    
    results = {}
    
    # Run tests
    results['test_a_maturity'] = test_a_consistent_pattern_reaches_maturity()
    results['test_b_short'] = test_b_short_pattern_no_candidate()
    results['test_c_inconsistent'] = test_c_inconsistent_pattern_no_maturity()
    results['test_d_single'] = test_d_single_episode_no_candidate()
    results['test_e_stability'] = test_e_kernel_stability_preserved()
    results['test_f_separation'] = test_f_field_separation()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name:30s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("ALL M6.1 TESTS PASSED")
    else:
        print(f"SOME TESTS FAILED ({sum(results.values())}/{len(results)} passed)")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    main()
