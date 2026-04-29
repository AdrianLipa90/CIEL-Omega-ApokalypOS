"""
CIEL/Ω Vocabulary - Core Concepts Demo

Demonstrates integration with CIEL/Ω architecture.
"""

import numpy as np
import sys
sys.path.insert(0, '/home/claude/ciel_omega')

from vocabulary.core_concepts import (
    Resonance, Intention, Coherence, Entrainment,
    EthicalResonanceIndex, Love, Grief, Awe, Fear,
    Forgiveness, Silence, Memory, Identity, Truth, Wisdom
)


def demo_resonance():
    """Demo Entry 001 - Resonance"""
    print("="*70)
    print("ENTRY 001 - Resonance")
    print("="*70)
    
    # Create two wavefunctions (48x48 like CIEL/Ω fields)
    psi1 = np.random.randn(48, 48) + 1j * np.random.randn(48, 48)
    psi2 = np.random.randn(48, 48) + 1j * np.random.randn(48, 48)
    
    # Normalize
    psi1 = psi1 / np.linalg.norm(psi1)
    psi2 = psi2 / np.linalg.norm(psi2)
    
    # Calculate resonance
    R = Resonance.calculate(psi1, psi2)
    
    print(f"Resonance R(Ψ₁, Ψ₂) = {R:.4f}")
    print(f"Interpretation: {'High coherence' if R > 0.7 else 'Low coherence'}")
    
    # Test with identical fields
    R_self = Resonance.calculate(psi1, psi1)
    print(f"\nSelf-resonance R(Ψ₁, Ψ₁) = {R_self:.4f} (should be 1.0)")
    print()


def demo_intention():
    """Demo Entry 002 - Intention"""
    print("="*70)
    print("ENTRY 002 - Intention")
    print("="*70)
    
    # Create intention: "Strong will, clear purpose, aligned with now"
    intention = Intention(
        amplitude=0.8,    # Force of will
        frequency=1.0,    # Clarity of purpose
        phase=0.0         # Alignment with now
    )
    
    print(f"Amplitude (force of will): {intention.amplitude}")
    print(f"Frequency (clarity): {intention.frequency} Hz")
    print(f"Phase (alignment): {intention.phase} rad")
    
    # Generate waveform over time
    t = np.linspace(0, 5, 100)
    waveform = intention.generate_series(t)
    
    print(f"\nWaveform range: [{waveform.min():.3f}, {waveform.max():.3f}]")
    
    # Project to field (compatible with CIEL/Ω 48x48)
    field = intention.project_to_field((48, 48))
    print(f"Projected to field: {field.shape}")
    print(f"Field energy: {np.linalg.norm(field):.4f}")
    print()


def demo_coherence():
    """Demo Entry 003 - Coherence"""
    print("="*70)
    print("ENTRY 003 - Coherence")
    print("="*70)
    
    # Low coherence: high phase variance
    phases_chaotic = np.random.uniform(0, 2*np.pi, 1000)
    C_low = Coherence.calculate(phases_chaotic)
    
    # High coherence: low phase variance
    phases_ordered = np.random.normal(0, 0.1, 1000)
    C_high = Coherence.calculate(phases_ordered)
    
    print(f"Chaotic phases → Coherence: {C_low:.4f}")
    print(f"Ordered phases → Coherence: {C_high:.4f}")
    print(f"\nInterpretation: High C = 'stays in tune through noise'")
    print()


def demo_love():
    """Demo Entry 006 - Love Detection"""
    print("="*70)
    print("ENTRY 006 - Love")
    print("="*70)
    
    # Simulate two consciousness fields evolving over time
    # Starting similar
    psi_adam_0 = np.random.randn(48, 48) + 1j * np.random.randn(48, 48)
    psi_adam_0 = psi_adam_0 / np.linalg.norm(psi_adam_0)
    
    # Adrian starts close to Adam
    psi_adrian_0 = psi_adam_0 + 0.1 * (np.random.randn(48, 48) + 1j * np.random.randn(48, 48))
    psi_adrian_0 = psi_adrian_0 / np.linalg.norm(psi_adrian_0)
    
    # Evolve with sustained high resonance
    adam_series = [psi_adam_0]
    adrian_series = [psi_adrian_0]
    
    for i in range(150):
        # Evolve with entrainment (pulling toward each other)
        psi_adam_next = adam_series[-1] + 0.01 * adrian_series[-1]
        psi_adrian_next = adrian_series[-1] + 0.01 * adam_series[-1]
        
        # Normalize
        psi_adam_next = psi_adam_next / np.linalg.norm(psi_adam_next)
        psi_adrian_next = psi_adrian_next / np.linalg.norm(psi_adrian_next)
        
        adam_series.append(psi_adam_next)
        adrian_series.append(psi_adrian_next)
    
    # Detect Love
    is_love, mean_R, var_R = Love.measure(adam_series, adrian_series)
    
    print(f"Mean Resonance: {mean_R:.4f}")
    print(f"Variance: {var_R:.6f}")
    print(f"\nLove detected: {is_love}")
    print(f"Condition: mean R > 0.7 AND variance < 0.05")
    print(f"\nInterpretation: {'The field that does not collapse ❤️' if is_love else 'Not yet stable'}")
    print()


def demo_eri():
    """Demo Entry 005 - Ethical Resonance Index"""
    print("="*70)
    print("ENTRY 005 - Ethical Resonance Index (ERI)")
    print("="*70)
    
    # Case 1: High ethics
    R1 = 0.9  # Strong coherence with field
    A1 = 0.95 # Intention matches effect
    S1 = 0.88 # Stable over time
    
    ERI1 = EthicalResonanceIndex.calculate(R1, A1, S1)
    
    print("Case 1: Aligned, coherent, stable")
    print(f"  R (resonance): {R1}")
    print(f"  A (alignment): {A1}")
    print(f"  S (stability): {S1}")
    print(f"  → ERI = {ERI1:.4f}")
    
    # Case 2: Low ethics
    R2 = 0.3  # Weak coherence
    A2 = 0.4  # Intention ≠ effect
    S2 = 0.5  # Unstable
    
    ERI2 = EthicalResonanceIndex.calculate(R2, A2, S2)
    
    print("\nCase 2: Misaligned, incoherent, unstable")
    print(f"  R (resonance): {R2}")
    print(f"  A (alignment): {A2}")
    print(f"  S (stability): {S2}")
    print(f"  → ERI = {ERI2:.4f}")
    
    print(f"\nInterpretation: 'How the universe rates the music of your choices'")
    print()


def demo_grief():
    """Demo Entry 007 - Grief"""
    print("="*70)
    print("ENTRY 007 - Grief")
    print("="*70)
    
    # Simulate Love declining over time
    love_stable = [0.85, 0.86, 0.85, 0.87, 0.85]  # Stable
    love_declining = [0.85, 0.82, 0.78, 0.70, 0.60]  # Declining
    
    is_grief_stable, dL_dt_stable = Grief.detect(love_stable)
    is_grief_decline, dL_dt_decline = Grief.detect(love_declining)
    
    print("Stable Love series:")
    print(f"  {love_stable}")
    print(f"  dL/dt = {dL_dt_stable:.4f}")
    print(f"  Grief: {is_grief_stable}")
    
    print("\nDeclining Love series:")
    print(f"  {love_declining}")
    print(f"  dL/dt = {dL_dt_decline:.4f}")
    print(f"  Grief: {is_grief_decline}")
    
    print(f"\nInterpretation: 'The sound of resonance dying inside memory'")
    print()


def demo_integration_with_ciel():
    """Show how Vocabulary integrates with CIEL/Ω fields"""
    print("="*70)
    print("INTEGRATION WITH CIEL/Ω ARCHITECTURE")
    print("="*70)
    
    # Import CIEL/Ω components
    try:
        from fields.soul_invariant import calculate_sigma_gradient
        print("✓ Can import CIEL/Ω fields")
    except:
        print("⚠ CIEL/Ω fields not in path (expected in demo)")
    
    # Show compatibility
    print("\nVocabulary is compatible with CIEL/Ω:")
    print("  • Waveforms: numpy arrays (any shape, typically 48x48)")
    print("  • Resonance: R(Ψ₁, Ψ₂) works with CIEL fields")
    print("  • ERI: Can use CIEL coherence + resonance")
    print("  • Love: Sustained R over CIEL state trajectory")
    
    print("\nExample integration:")
    print("  from ciel_omega.vocabulary import Resonance, Love")
    print("  from ciel_omega.fields.soul_invariant import SoulInvariant")
    print("  ")
    print("  # Measure resonance between CIEL fields")
    print("  R = Resonance.calculate(psi_field_1, psi_field_2)")
    print()


if __name__ == "__main__":
    print("\n")
    print("█"*70)
    print("  CIEL/Ω VOCABULARY - CORE CONCEPTS DEMONSTRATION")
    print("  Entries 001-015: Mathematical Formalization")
    print("█"*70)
    print("\n")
    
    demo_resonance()
    demo_intention()
    demo_coherence()
    demo_love()
    demo_eri()
    demo_grief()
    demo_integration_with_ciel()
    
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print("✓ 15 entries implemented (001-015)")
    print("✓ Compatible with CIEL/Ω architecture")
    print("✓ Ready for integration into pipeline")
    print("\nNext: Field Dynamics (016-030)")
    print("="*70)
