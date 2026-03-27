"""Test D_mem/D_id evolution with zero external forcing"""

import numpy as np
from ciel_omega.memory import MemoryDynamicsEngine, MemoryPotential

def test_defect_evolution():
    """Test that defects decrease when no external forcing"""
    
    print("Testing defect evolution with ZERO external forcing")
    print("="*70)
    
    engine = MemoryDynamicsEngine()
    potential = engine.potential
    
    # Start with random phases
    initial_phases = np.random.randn(8) * 0.5
    state = engine.initialize_state(initial_phases, initial_identity_phase=0.0)
    
    # Initial defects
    D_mem_0 = potential.compute_global_memory_defect(
        state.phases, engine.equilibrium_shifts
    )
    D_id_0 = potential.compute_global_identity_defect(state.phases)
    
    print(f"Initial: D_mem = {D_mem_0:.4f}, D_id = {D_id_0:.4f}")
    
    # Evolve with NO external forcing
    dt = 0.1
    num_steps = 200
    zero_force = None  # No external forces
    
    final_state = engine.integrate(num_steps, dt, zero_force)
    
    # Final defects
    D_mem_f = potential.compute_global_memory_defect(
        final_state.phases, engine.equilibrium_shifts
    )
    D_id_f = potential.compute_global_identity_defect(final_state.phases)
    
    print(f"Final:   D_mem = {D_mem_f:.4f}, D_id = {D_id_f:.4f}")
    print(f"Change:  ΔD_mem = {D_mem_f - D_mem_0:+.4f}, ΔD_id = {D_id_f - D_id_0:+.4f}")
    
    # Check potential too
    energy_0 = potential.compute_monitored_energy(
        state.phases, state.anchor_phases, 
        state.velocities, engine.equilibrium_shifts
    )
    V_0 = energy_0['V_static']
    
    energy_f = potential.compute_monitored_energy(
        final_state.phases, final_state.anchor_phases,
        final_state.velocities, engine.equilibrium_shifts
    )
    V_f = energy_f['V_static']
    
    print(f"\nPotential: V_0 = {V_0:.4f}, V_f = {V_f:.4f}, ΔV = {V_f - V_0:+.4f}")
    
    passed = D_mem_f < D_mem_0 and D_id_f < D_id_0 and V_f < V_0
    if passed:
        print("\n✓ PASS: Defects and potential all decreased")
    else:
        print("\n✗ FAIL: System did not minimize defects")
        if D_mem_f >= D_mem_0:
            print(f"  D_mem increased by {D_mem_f - D_mem_0:.4f}")
        if D_id_f >= D_id_0:
            print(f"  D_id increased by {D_id_f - D_id_0:.4f}")
        if V_f >= V_0:
            print(f"  V increased by {V_f - V_0:.4f}")
    assert passed

if __name__ == "__main__":
    test_defect_evolution()
