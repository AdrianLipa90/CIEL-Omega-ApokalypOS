"""CIEL/Ω Memory Architecture - Holonomy & EBA Demonstration

Demonstrates:
1. Hybrid equilibrium phase shift construction Δ^(0)_kj
2. Euler-Berry-Aharonov-Bohm topological condition
3. Loop validation for memory consolidation

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

import numpy as np

from memory import (
    CouplingEngine,
    HolonomyCalculator,
    MemoryLoop,
    define_standard_loops,
    create_loop_from_trajectory,
    CHANNEL_NAMES,
)


def demo_equilibrium_shifts():
    """Demonstrate hybrid equilibrium shift construction"""
    print("\n" + "="*70)
    print("DEMO 1: HYBRID EQUILIBRIUM PHASE SHIFTS Δ^(0)_kj")
    print("="*70)
    
    coupling = CouplingEngine()
    
    # Get role amplitudes for key pairs
    role_amps = coupling.get_default_role_amplitudes()
    
    print("\nRole amplitudes for strategic pairs (in units of π):")
    print("-"*70)
    strategic_pairs = [
        (6, 7, "Identity ↔ Invariant"),
        (6, 5, "Identity ↔ Affective"),
        (6, 3, "Identity ↔ Semantic"),
        (2, 3, "Episodic ↔ Semantic"),
        (1, 2, "Working ↔ Episodic"),
        (0, 1, "Perceptual ↔ Working"),
    ]
    
    for k, j, name in strategic_pairs:
        amp_pi = role_amps[k, j] / np.pi
        print(f"  {name:30s}: {amp_pi:.3f}π = {role_amps[k, j]:.4f} rad")
    
    # Compute equilibrium shifts with hybrid formula
    print("\nComputing equilibrium shifts with hybrid formula...")
    print("  Parameters: λ_r=0.35, λ_τ=0.45, σ_r=0.20, σ_τ=1.0")
    
    shifts = coupling.compute_phase_shift_matrix(
        lambda_r=0.35,
        lambda_tau=0.45,
        sigma_r=0.20,
        sigma_tau=1.0,
        delta_max_pair=0.18 * np.pi,
        role_amplitudes=role_amps
    )
    
    print("\nEquilibrium shifts Δ^(0)_kj for key pairs (in rad):")
    print("-"*70)
    print(f"{'Pair':<35s} {'Δ^(0)_kj':>10s} {'[π units]':>12s}")
    print("-"*70)
    
    for k, j, name in strategic_pairs:
        shift = shifts[k, j]
        shift_pi = shift / np.pi
        print(f"{name:35s} {shift:10.4f} {shift_pi:12.4f}π")
    
    # Show matrix structure
    print("\nFull equilibrium shift matrix structure:")
    print("(showing magnitude, positive = j leads k)")
    print("-"*70)
    
    # Print matrix with channel labels
    header = "     " + "".join([f"{CHANNEL_NAMES[j][:4]:>8s}" for j in range(8)])
    print(header)
    print("-"*70)
    
    for k in range(8):
        row = f"{CHANNEL_NAMES[k][:4]:<5s}"
        for j in range(8):
            if k == j:
                row += f"{'---':>8s}"
            else:
                shift_pi = shifts[k, j] / np.pi
                row += f"{shift_pi:8.3f}"
        print(row)
    
    print("\nKey observations:")
    print("  • Inner channels (M6, M7) have small mutual shifts (near co-phase)")
    print("  • Episodic→Semantic has larger lag (consolidation)")
    print("  • Perceptual→Working has largest shift (fast outer layer)")
    print("  • Shifts are anti-symmetric: Δ^(0)_kj = -Δ^(0)_jk")
    
    return shifts


def demo_eba_condition():
    """Demonstrate EBA topological condition for loops"""
    print("\n" + "="*70)
    print("DEMO 2: EULER-BERRY-AHARONOV-BOHM CONDITION")
    print("="*70)
    
    calc = HolonomyCalculator()
    
    # Define standard loop types
    standard_loops = define_standard_loops()
    
    print("\nStandard loop types:")
    for loop_name, channels in standard_loops.items():
        channel_str = " → ".join([CHANNEL_NAMES[ch][:4] for ch in channels])
        print(f"  {loop_name:25s}: {channel_str}")
    
    # Create synthetic trajectories for each loop type
    print("\n" + "="*70)
    print("Testing EBA condition on synthetic loops")
    print("="*70)
    
    test_cases = []
    
    # Case 1: Well-closed loop (small defect)
    print("\nCase 1: COHERENT LOOP (should pass)")
    print("-"*70)
    
    channels = standard_loops['short']  # M1 → M2 → M3 → M1
    # Create smooth closed trajectory
    n_steps = len(channels)
    phases = [0.1, 0.3, 0.5, 0.12]  # Nearly returns to start
    
    loop1 = create_loop_from_trajectory(
        channel_sequence=channels,
        phase_trajectory=phases,
        loop_type='short'
    )
    
    result1 = calc.compute_eba_defect(loop1)
    
    print(f"  Loop: {' → '.join([CHANNEL_NAMES[ch][:4] for ch in channels])}")
    print(f"  Φ_dyn:   {result1['phi_dyn']:.4f} rad = {result1['phi_dyn']/np.pi:.3f}π")
    print(f"  Φ_Berry: {result1['phi_berry']:.4f} rad = {result1['phi_berry']/np.pi:.3f}π")
    print(f"  Φ_AB:    {result1['phi_ab']:.4f} rad = {result1['phi_ab']/np.pi:.3f}π")
    print(f"  ν_E:     {result1['nu_e']}")
    print(f"  ε_EBA:   {result1['epsilon_eba']:.4f} rad = {result1['epsilon_eba']/np.pi:.3f}π")
    print(f"  Status:  {'✓ COHERENT' if result1['is_coherent'] else '✗ DEFECT'}")
    
    valid1 = calc.check_consolidation_validity(loop1, threshold=0.15)
    print(f"  Consolidation valid: {valid1}")
    
    test_cases.append(('Coherent short loop', result1, valid1))
    
    # Case 2: Loop with defect (large ε_EBA)
    print("\nCase 2: DEFECTIVE LOOP (should fail)")
    print("-"*70)
    
    channels = standard_loops['medium']
    # Create trajectory that doesn't close well
    phases = [0.0, 1.5, 2.8, 4.0, 5.2, 6.0, 1.2]  # Large defect at end
    
    loop2 = create_loop_from_trajectory(
        channel_sequence=channels,
        phase_trajectory=phases,
        loop_type='medium'
    )
    
    # Add some hidden channel phases
    hidden_states = np.random.randn(8) * 0.5
    result2 = calc.compute_eba_defect(loop2, hidden_states)
    
    print(f"  Loop: {' → '.join([CHANNEL_NAMES[ch][:4] for ch in channels[:3]])}... (7 steps)")
    print(f"  Φ_dyn:   {result2['phi_dyn']:.4f} rad = {result2['phi_dyn']/np.pi:.3f}π")
    print(f"  Φ_Berry: {result2['phi_berry']:.4f} rad = {result2['phi_berry']/np.pi:.3f}π")
    print(f"  Φ_AB:    {result2['phi_ab']:.4f} rad = {result2['phi_ab']/np.pi:.3f}π")
    print(f"  ν_E:     {result2['nu_e']}")
    print(f"  ε_EBA:   {result2['epsilon_eba']:.4f} rad = {result2['epsilon_eba']/np.pi:.3f}π")
    print(f"  Status:  {'✓ COHERENT' if result2['is_coherent'] else '✗ DEFECT'}")
    
    valid2 = calc.check_consolidation_validity(loop2, hidden_states, threshold=0.15)
    print(f"  Consolidation valid: {valid2}")
    
    test_cases.append(('Defective medium loop', result2, valid2))
    
    # Case 3: Deep identity loop with small defect
    print("\nCase 3: DEEP IDENTITY LOOP (near-coherent)")
    print("-"*70)
    
    channels = standard_loops['deep']
    # Smooth trajectory with very small defect
    phases = [0.0, 0.05, 0.08, 0.10, 0.08, 0.04, 0.02]
    
    loop3 = create_loop_from_trajectory(
        channel_sequence=channels,
        phase_trajectory=phases,
        loop_type='deep'
    )
    
    result3 = calc.compute_eba_defect(loop3)
    
    print(f"  Loop: {' → '.join([CHANNEL_NAMES[ch][:4] for ch in channels[:4]])}... (7 steps)")
    print(f"  Φ_dyn:   {result3['phi_dyn']:.4f} rad = {result3['phi_dyn']/np.pi:.3f}π")
    print(f"  Φ_Berry: {result3['phi_berry']:.4f} rad = {result3['phi_berry']/np.pi:.3f}π")
    print(f"  Φ_AB:    {result3['phi_ab']:.4f} rad = {result3['phi_ab']/np.pi:.3f}π")
    print(f"  ν_E:     {result3['nu_e']}")
    print(f"  ε_EBA:   {result3['epsilon_eba']:.4f} rad = {result3['epsilon_eba']/np.pi:.3f}π")
    print(f"  Status:  {'✓ COHERENT' if result3['is_coherent'] else '✗ DEFECT'}")
    
    valid3 = calc.check_consolidation_validity(loop3, threshold=0.15)
    print(f"  Consolidation valid: {valid3}")
    
    test_cases.append(('Deep identity loop', result3, valid3))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for name, result, valid in test_cases:
        status = "PASS" if valid else "FAIL"
        defect_mag = result['defect_magnitude']
        print(f"{name:30s}: {status:4s}  |ε_EBA| = {defect_mag:.4f}")
    
    print("\nKey insights:")
    print("  • EBA condition catches topological defects in loops")
    print("  • Coherent loops have |ε_EBA| << 1")
    print("  • Defective loops cannot be consolidated to deeper memory")
    print("  • This prevents false pattern consolidation")
    
    return test_cases


def demo_consolidation_gates():
    """Demonstrate EBA as gating function for consolidation"""
    print("\n" + "="*70)
    print("DEMO 3: EBA AS CONSOLIDATION GATE")
    print("="*70)
    
    calc = HolonomyCalculator()
    
    # Simulate multiple episodes trying to consolidate to semantic
    print("\nSimulating episodic → semantic consolidation attempts:")
    print("-"*70)
    
    episodes = [
        {
            'name': 'High-quality memory',
            'trajectory': [0.1, 0.25, 0.35, 0.12],  # Clean loop
            'salience': 0.9,
            'expected': 'ACCEPT'
        },
        {
            'name': 'Noisy memory',
            'trajectory': [0.1, 1.2, 2.8, 4.5],  # Poor closure
            'salience': 0.85,
            'expected': 'REJECT'
        },
        {
            'name': 'Medium quality',
            'trajectory': [0.1, 0.3, 0.55, 0.18],  # Moderate defect
            'salience': 0.8,
            'expected': 'BORDERLINE'
        },
    ]
    
    loop_channels = [2, 3, 2]  # M2 → M3 → M2 (episodic ↔ semantic)
    
    for i, ep in enumerate(episodes, 1):
        print(f"\nEpisode {i}: {ep['name']}")
        print(f"  Salience: {ep['salience']:.2f}")
        
        loop = create_loop_from_trajectory(
            channel_sequence=loop_channels,
            phase_trajectory=ep['trajectory'],
            loop_type='semantic_consolidation'
        )
        
        result = calc.compute_eba_defect(loop)
        valid = calc.check_consolidation_validity(loop, threshold=0.15)
        
        print(f"  ε_EBA: {result['epsilon_eba']:.4f} rad")
        print(f"  Decision: {'✓ CONSOLIDATE' if valid else '✗ REJECT'}")
        print(f"  Expected: {ep['expected']}")
        
        # Show that EBA overrides salience
        if ep['salience'] > 0.8 and not valid:
            print(f"  → High salience but EBA defect prevents consolidation")
        elif ep['salience'] < 0.9 and valid:
            print(f"  → Moderate salience but good EBA allows consolidation")
    
    print("\nConclusion:")
    print("  EBA acts as topological quality gate:")
    print("  • Prevents consolidation of geometrically inconsistent memories")
    print("  • Even high-salience memories must satisfy EBA condition")
    print("  • Ensures semantic memory maintains phase coherence")


def main():
    """Run all demonstrations"""
    print("="*70)
    print("CIEL/Ω HOLONOMY & EBA DEMONSTRATION")
    print("Equilibrium Shifts + Topological Consistency")
    print("="*70)
    
    # Run demos
    shifts = demo_equilibrium_shifts()
    test_cases = demo_eba_condition()
    demo_consolidation_gates()
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nImplemented features:")
    print("  ✓ Hybrid equilibrium shift formula Δ^(0)_kj")
    print("    - Radial geometry component")
    print("    - Time hierarchy component")
    print("    - Role amplitude component")
    print("  ✓ EBA topological condition")
    print("    - Dynamical phase Φ_dyn")
    print("    - Berry geometric phase Φ_Berry")
    print("    - Aharonov-Bohm non-local phase Φ_AB")
    print("    - Winding number ν_E")
    print("    - Defect calculation ε_EBA")
    print("  ✓ Consolidation gating via EBA")
    print("    - Soft constraint (potential)")
    print("    - Hard constraint (threshold)")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
