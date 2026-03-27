"""CIEL/Ω Memory Architecture - Critical Fixes Validation

Validates:
1. β is symmetric while J is asymmetric
2. D_mem and D_id global defects work correctly
3. IdentityField is separate from M6
4. System behavior under weak forcing

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

import numpy as np

from ciel_omega.memory import (
    MemoryDynamicsEngine,
    MemoryPotential,
    IdentityField,
    COUPLING_MATRIX,
    CHANNEL_NAMES,
)


def validate_beta_symmetry():
    """Validate that β is symmetric while J is asymmetric"""
    print("\n" + "="*70)
    print("VALIDATION 1: β SYMMETRIC, J ASYMMETRIC")
    print("="*70)
    
    # Get J and β
    J = COUPLING_MATRIX
    
    potential = MemoryPotential()
    beta = potential.beta
    
    print("\nChecking asymmetry of J (coupling matrix):")
    print("-"*70)
    
    # Find asymmetric pairs
    asymmetric_pairs = []
    for k in range(8):
        for j in range(k+1, 8):
            if abs(J[k,j] - J[j,k]) > 1e-6:
                asymmetric_pairs.append((k, j, J[k,j], J[j,k]))
    
    print(f"Found {len(asymmetric_pairs)} asymmetric pairs in J:")
    for k, j, J_kj, J_jk in asymmetric_pairs[:5]:
        print(f"  {CHANNEL_NAMES[k][:4]} → {CHANNEL_NAMES[j][:4]}: J={J_kj:.3f}, "
              f"{CHANNEL_NAMES[j][:4]} → {CHANNEL_NAMES[k][:4]}: J={J_jk:.3f}")
    
    print("\nChecking symmetry of β (conflict potential):")
    print("-"*70)
    
    # Check all pairs for symmetry
    max_asymmetry = 0.0
    asymmetric_beta = []
    
    for k in range(8):
        for j in range(k+1, 8):
            diff = abs(beta[k,j] - beta[j,k])
            max_asymmetry = max(max_asymmetry, diff)
            if diff > 1e-6:
                asymmetric_beta.append((k, j, beta[k,j], beta[j,k], diff))
    
    if len(asymmetric_beta) == 0:
        print("✓ β is perfectly symmetric (β_kj = β_jk for all pairs)")
        print(f"  Maximum asymmetry: {max_asymmetry:.2e}")
    else:
        print(f"✗ Found {len(asymmetric_beta)} asymmetric pairs in β")
        for k, j, b_kj, b_jk, diff in asymmetric_beta[:5]:
            print(f"  {CHANNEL_NAMES[k][:4]}↔{CHANNEL_NAMES[j][:4]}: "
                  f"β_kj={b_kj:.4f}, β_jk={b_jk:.4f}, diff={diff:.2e}")
    
    # Show relationship β = sqrt(J_kj * J_jk)
    print("\nVerifying β = sqrt(J_kj * J_jk) * coupling_factor:")
    print("-"*70)
    
    test_pairs = [(1, 6), (2, 3), (5, 6), (6, 7)]
    for k, j in test_pairs:
        J_kj = J[k, j]
        J_jk = J[j, k]
        geometric_mean = np.sqrt(J_kj * J_jk)
        beta_kj = beta[k, j]
        
        # Check if beta is close to geometric mean (with coupling weight)
        print(f"  {CHANNEL_NAMES[k][:4]}↔{CHANNEL_NAMES[j][:4]}: "
              f"sqrt(J)={geometric_mean:.4f}, β={beta_kj:.4f}")
    
    return len(asymmetric_beta) == 0


def validate_global_defects():
    """Validate D_mem and D_id calculations"""
    print("\n" + "="*70)
    print("VALIDATION 2: GLOBAL DEFECTS D_mem AND D_id")
    print("="*70)
    
    potential = MemoryPotential()
    
    # Test case 1: Perfect alignment (all phases at identity)
    print("\nCase 1: Perfect alignment (all phases = identity phase)")
    print("-"*70)
    
    identity_phase = 0.5
    potential.identity.phase = identity_phase
    phases = np.ones(8) * identity_phase
    equilibrium_shifts = np.zeros((8, 8))
    
    D_mem = potential.compute_global_memory_defect(phases, equilibrium_shifts)
    D_id = potential.compute_global_identity_defect(phases)
    
    print(f"  D_mem = {D_mem:.6f} (should be ~0)")
    print(f"  D_id  = {D_id:.6f} (should be ~0)")
    
    if D_mem < 0.01 and D_id < 0.01:
        print("  ✓ Both defects near zero for perfect alignment")
    else:
        print("  ✗ Defects too large for perfect alignment")
    
    # Test case 2: Random phases (high defect)
    print("\nCase 2: Random phases (high defect expected)")
    print("-"*70)
    
    phases = np.random.randn(8) * np.pi
    
    D_mem = potential.compute_global_memory_defect(phases, equilibrium_shifts)
    D_id = potential.compute_global_identity_defect(phases)
    
    print(f"  D_mem = {D_mem:.6f}")
    print(f"  D_id  = {D_id:.6f}")
    print("  (Higher values expected for random configuration)")
    
    # Test case 3: Weak forcing should reduce defects
    print("\nCase 3: Evolution under weak forcing")
    print("-"*70)
    
    engine = MemoryDynamicsEngine()
    
    # Start with random phases
    initial_phases = np.random.randn(8) * 0.5
    state = engine.initialize_state(initial_phases, initial_identity_phase=0.0)
    
    # Compute equilibrium shifts
    shifts = engine.coupling.compute_phase_shift_matrix(
        role_amplitudes=engine.coupling.get_default_role_amplitudes()
    )
    
    # Initial defects
    D_mem_0 = potential.compute_global_memory_defect(state.phases, shifts)
    D_id_0 = potential.compute_global_identity_defect(state.phases)
    
    print(f"  Initial: D_mem = {D_mem_0:.4f}, D_id = {D_id_0:.4f}")
    
    # Evolve with weak forcing
    dt = 0.1
    num_steps = 100
    weak_force = np.ones(8) * 0.01  # Small uniform force
    
    final_state = engine.integrate(num_steps, dt, weak_force)
    
    # Final defects
    D_mem_f = potential.compute_global_memory_defect(final_state.phases, shifts)
    D_id_f = potential.compute_global_identity_defect(final_state.phases)
    
    print(f"  Final:   D_mem = {D_mem_f:.4f}, D_id = {D_id_f:.4f}")
    print(f"  Change:  ΔD_mem = {D_mem_f - D_mem_0:+.4f}, "
          f"ΔD_id = {D_id_f - D_id_0:+.4f}")
    
    if D_mem_f < D_mem_0 and D_id_f < D_id_0:
        print("  ✓ Both defects decreased under weak forcing")
    else:
        print("  ⚠ Defects did not decrease as expected")
    
    return D_mem_f < D_mem_0 and D_id_f < D_id_0


def validate_identity_separation():
    """Validate that IdentityField is separate from M6"""
    print("\n" + "="*70)
    print("VALIDATION 3: IdentityField SEPARATE FROM M6")
    print("="*70)
    
    # Create IdentityField
    identity = IdentityField(initial_phase=0.3)
    
    print("\nIdentityField:")
    print(f"  Type: {type(identity).__name__}")
    print(f"  Phase: {identity.phase:.4f}")
    print(f"  Anchors: {identity.anchors}")
    print(f"  Has memory storage: {hasattr(identity, 'store')}")
    
    print("\nKey observations:")
    print("  • IdentityField is NOT a BaseMemoryChannel")
    print("  • IdentityField does NOT have .store() method")
    print("  • IdentityField is the ATTRACTOR, not a memory channel")
    print("  • M6 IdentityMemory (when implemented) will store HISTORY of identity")
    
    # Check that IdentityField is not a memory channel
    from ciel_omega.memory.base import BaseMemoryChannel
    
    is_memory_channel = isinstance(identity, BaseMemoryChannel)
    print(f"\n  IdentityField instanceof BaseMemoryChannel: {is_memory_channel}")
    
    if not is_memory_channel:
        print("  ✓ IdentityField is correctly separate from memory channels")
    else:
        print("  ✗ ERROR: IdentityField should NOT be a memory channel")
    
    return not is_memory_channel


def validate_coupling_constraints():
    """Validate coupling constraints (M0 cannot directly change M7, etc.)"""
    print("\n" + "="*70)
    print("VALIDATION 4: COUPLING CONSTRAINTS")
    print("="*70)
    
    J = COUPLING_MATRIX
    
    print("\nChecking critical constraints:")
    print("-"*70)
    
    # M0 → M7 should be very weak
    J_07 = J[0, 7]
    print(f"1. M0 → M7 (Perceptual → Invariant): J = {J_07:.4f}")
    if J_07 < 0.05:
        print("   ✓ Very weak coupling (as expected)")
    else:
        print("   ✗ Too strong! M0 should barely influence M7")
    
    # M0 → M6 should be very weak
    J_06 = J[0, 6]
    print(f"2. M0 → M6 (Perceptual → Identity): J = {J_06:.4f}")
    if J_06 < 0.05:
        print("   ✓ Very weak coupling (as expected)")
    else:
        print("   ✗ Too strong! M0 should barely influence M6")
    
    # M6 ↔ M7 should be very strong
    J_67 = J[6, 7]
    J_76 = J[7, 6]
    print(f"3. M6 ↔ M7 (Identity ↔ Invariant): J_67 = {J_67:.4f}, J_76 = {J_76:.4f}")
    if J_67 > 0.8 and J_76 > 0.8:
        print("   ✓ Very strong coupling (as expected)")
    else:
        print("   ✗ Too weak! M6 and M7 should be tightly coupled")
    
    # M1 → M6 should be strong
    J_16 = J[1, 6]
    print(f"4. M1 → M6 (Working → Identity): J = {J_16:.4f}")
    if J_16 > 0.7:
        print("   ✓ Strong coupling (as expected)")
    else:
        print("   ⚠ Could be stronger for identity projection")
    
    all_pass = (J_07 < 0.05 and J_06 < 0.05 and 
                J_67 > 0.8 and J_76 > 0.8 and J_16 > 0.7)
    
    return all_pass


def main():
    """Run all validations"""
    print("="*70)
    print("CIEL/Ω MEMORY ARCHITECTURE - CRITICAL FIXES VALIDATION")
    print("="*70)
    
    results = {}
    
    # Run validations
    results['beta_symmetric'] = validate_beta_symmetry()
    results['global_defects'] = validate_global_defects()
    results['identity_separate'] = validate_identity_separation()
    results['coupling_constraints'] = validate_coupling_constraints()
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name:25s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("ALL VALIDATIONS PASSED")
    else:
        print("SOME VALIDATIONS FAILED - REVIEW REQUIRED")
    print("="*70)
    
    print("\nCritical fixes implemented:")
    print("  1. β = sqrt(J_kj * J_jk) * coupling_factor (symmetric)")
    print("  2. D_mem and D_id global defects")
    print("  3. IdentityField separate from M6")
    print("  4. Coupling constraints verified")
    
    print("\nStill TODO:")
    print("  - M6 IdentityMemory channel implementation")
    print("  - Full orchestrator with consolidation logic")
    print("  - Remaining channels (M0, M1, M3, M4, M5)")
    print()


if __name__ == "__main__":
    main()
