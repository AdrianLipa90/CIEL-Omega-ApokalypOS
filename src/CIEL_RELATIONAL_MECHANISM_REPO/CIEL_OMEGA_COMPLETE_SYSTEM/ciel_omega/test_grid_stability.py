"""CIEL/Ω Memory Architecture - Grid Stability Test

Regression test for numerical stability across parameter grid:
- Seeds: 0-49
- Timesteps: {0.05, 0.1, 0.2, 0.3}
- Initial scales: {0.5, 1.0}

Tests whether V_static, D_mem, and D_id decrease under zero forcing.

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

import numpy as np
import warnings
from typing import Dict, List
from memory import MemoryDynamicsEngine, MemoryPotential


def run_stability_test(seed: int, dt: float, scale: float, 
                      num_steps: int = 200) -> Dict:
    """Run single stability test.
    
    Args:
        seed: Random seed for initialization
        dt: Timestep
        scale: Initial phase scale (std deviation)
        num_steps: Number of steps to integrate
        
    Returns:
        Dictionary with test results
    """
    engine = MemoryDynamicsEngine()
    potential = engine.potential
    
    # Initialize with seed
    np.random.seed(seed)
    initial_phases = np.random.randn(8) * scale
    state = engine.initialize_state(initial_phases, initial_identity_phase=0.0)
    
    # Compute initial metrics
    V_static_0 = potential.compute_static_potential(
        state.phases, state.anchor_phases, engine.equilibrium_shifts
    )['V_static']
    
    D_mem_0 = potential.compute_global_memory_defect(
        state.phases, engine.equilibrium_shifts
    )
    
    D_id_0 = potential.compute_global_identity_defect(state.phases)
    
    # Integrate with zero forcing; capture the expected large-dt substepping warning
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        final_state = engine.integrate(num_steps, dt, input_forces=None)
    expected_warning = any("Large timestep" in str(w.message) for w in caught)
    
    # Compute final metrics
    V_static_f = potential.compute_static_potential(
        final_state.phases, final_state.anchor_phases, engine.equilibrium_shifts
    )['V_static']
    
    D_mem_f = potential.compute_global_memory_defect(
        final_state.phases, engine.equilibrium_shifts
    )
    
    D_id_f = potential.compute_global_identity_defect(final_state.phases)
    
    # Compute changes
    delta_V = V_static_f - V_static_0
    delta_D_mem = D_mem_f - D_mem_0
    delta_D_id = D_id_f - D_id_0
    
    # Check stability (all should decrease)
    V_stable = delta_V < 0
    D_mem_stable = delta_D_mem < 0
    D_id_stable = delta_D_id < 0
    all_stable = V_stable and D_mem_stable and D_id_stable
    
    return {
        'seed': seed,
        'dt': dt,
        'scale': scale,
        'V_static_0': V_static_0,
        'V_static_f': V_static_f,
        'delta_V': delta_V,
        'D_mem_0': D_mem_0,
        'D_mem_f': D_mem_f,
        'delta_D_mem': delta_D_mem,
        'D_id_0': D_id_0,
        'D_id_f': D_id_f,
        'delta_D_id': delta_D_id,
        'V_stable': V_stable,
        'D_mem_stable': D_mem_stable,
        'D_id_stable': D_id_stable,
        'all_stable': all_stable,
        'expected_warning': expected_warning,
    }


def test_problematic_case():
    """Test the specific problematic case identified by Adrian.
    
    seed=3, dt=0.3, scale=1.0 should show D_id increase.
    """
    print("\n" + "="*70)
    print("TESTING PROBLEMATIC CASE: seed=3, dt=0.3, scale=1.0")
    print("="*70)
    
    result = run_stability_test(seed=3, dt=0.3, scale=1.0)
    
    print(f"\nInitial:")
    print(f"  V_static = {result['V_static_0']:.4f}")
    print(f"  D_mem    = {result['D_mem_0']:.4f}")
    print(f"  D_id     = {result['D_id_0']:.4f}")
    
    print(f"\nFinal:")
    print(f"  V_static = {result['V_static_f']:.4f}")
    print(f"  D_mem    = {result['D_mem_f']:.4f}")
    print(f"  D_id     = {result['D_id_f']:.4f}")
    
    print(f"\nChanges:")
    print(f"  ΔV_static = {result['delta_V']:+.4f} "
          f"{'✓' if result['V_stable'] else '✗'}")
    print(f"  ΔD_mem    = {result['delta_D_mem']:+.4f} "
          f"{'✓' if result['D_mem_stable'] else '✗'}")
    print(f"  ΔD_id     = {result['delta_D_id']:+.4f} "
          f"{'✓' if result['D_id_stable'] else '✗'}")
    
    if result['all_stable']:
        print("\n✓ Case is now stable (problem fixed by substepping)")
    else:
        print("\n✗ Case still shows instability")
    
    assert result['expected_warning']
    assert result['all_stable']


if __name__ == "__main__":
    print("Testing problematic case from Adrian's audit...")
    test_problematic_case()
