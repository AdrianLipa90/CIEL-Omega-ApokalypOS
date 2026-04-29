"""Test if strengthening α_k improves D_id monotonicity

Current issue: D_id increases in ~25% of random initial conditions.
Hypothesis: α_k (alignment cost) is too weak relative to β_kj (conflict).
Solution: Multiply α_k by factor > 1 to prioritize identity alignment.
"""

import numpy as np
from memory import MemoryDynamicsEngine, MemoryPotential

def test_alignment_strengthening(alpha_factor=1.5, num_trials=20):
    """Test D_id monotonicity with strengthened alignment costs"""
    
    print(f"Testing D_id evolution with α_k multiplied by {alpha_factor}")
    print("="*70)
    
    successes = 0
    failures = []
    
    for trial in range(num_trials):
        # Create engine
        engine = MemoryDynamicsEngine()
        potential = engine.potential
        
        # Strengthen alignment costs
        potential.alpha *= alpha_factor
        
        # Random initial state
        np.random.seed(trial)
        initial_phases = np.random.randn(8) * 0.5
        state = engine.initialize_state(initial_phases, initial_identity_phase=0.0)
        
        # Initial D_id
        D_id_0 = potential.compute_global_identity_defect(state.phases)
        
        # Evolve with zero forcing
        dt = 0.1
        num_steps = 200
        final_state = engine.integrate(num_steps, dt, input_forces=None)
        
        # Final D_id
        D_id_f = potential.compute_global_identity_defect(final_state.phases)
        
        # Check if decreased
        if D_id_f < D_id_0:
            successes += 1
        else:
            failures.append({
                'trial': trial,
                'D_id_0': D_id_0,
                'D_id_f': D_id_f,
                'delta': D_id_f - D_id_0
            })
    
    print(f"\nResults for α_factor = {alpha_factor}:")
    print(f"  Successes: {successes}/{num_trials}")
    print(f"  Failures:  {len(failures)}/{num_trials}")
    
    if failures:
        print(f"\n  Failure cases:")
        for f in failures[:3]:
            print(f"    Trial {f['trial']}: {f['D_id_0']:.4f} → {f['D_id_f']:.4f} "
                  f"(Δ = +{f['delta']:.4f})")
    
    success_rate = successes / num_trials
    print(f"\n  Success rate: {success_rate*100:.1f}%")
    
    assert success_rate >= 0.95

if __name__ == "__main__":
    print("TESTING IDENTITY ALIGNMENT STRENGTHENING")
    print("="*70)
    
    # Test different strengthening factors
    factors = [1.0, 1.2, 1.5, 2.0, 3.0]
    
    results = {}
    for factor in factors:
        rate = test_alignment_strengthening(factor, num_trials=20)
        results[factor] = rate
        print()
    
    print("="*70)
    print("SUMMARY")
    print("="*70)
    for factor, rate in results.items():
        status = "✓" if rate >= 0.95 else "⚠" if rate >= 0.75 else "✗"
        print(f"  α_factor = {factor:.1f}: {rate*100:5.1f}% {status}")
    
    # Find minimum factor for 95% success
    best = None
    for factor in sorted(results.keys()):
        if results[factor] >= 0.95:
            best = factor
            break
    
    if best:
        print(f"\nRecommendation: Use α_factor = {best:.1f} for ≥95% D_id monotonicity")
    else:
        print(f"\nNote: May need α_factor > {max(factors)} for reliable monotonicity")
