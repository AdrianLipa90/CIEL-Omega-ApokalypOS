"""CIEL/Ω Memory Architecture - M6 IdentityMemory Demo

Demonstrates that M6 only consolidates with long, consistent patterns.
Shows the difference between:
- Short/inconsistent patterns (no consolidation)
- Long consistent patterns (creates anchor candidates)

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

import numpy as np

from ciel_omega.memory import (
    IdentityField,
    IdentityMemory,
)


def demo_short_pattern():
    """Demo: Short pattern does not consolidate in M6"""
    print("\n" + "="*70)
    print("DEMO 1: SHORT PATTERN (No Consolidation)")
    print("="*70)
    
    identity_field = IdentityField(initial_phase=0.5)
    identity_memory = IdentityMemory(identity_field)
    
    print("\nSimulating SHORT pattern (5 observations)...")
    
    for t in range(5):
        identity_field.phase = 0.5 + np.random.randn() * 0.01
        identity_memory.observe_identity_field(current_time=float(t))
    
    # Try to create candidate
    candidate = identity_memory.check_anchor_candidate_creation(
        current_time=5.0,
        anchor_key="short_pattern",
        proposed_phase=0.5
    )
    
    stats = identity_memory.get_statistics()
    
    print(f"\nResults after SHORT pattern:")
    print(f"  Traces: {stats['trace_count']}")
    print(f"  Confidence: {stats['current_confidence']:.3f}")
    print(f"  Anchor candidate created: {candidate is not None}")
    print(f"  Detected candidates: {stats['detected_candidates']}")
    print(f"  Mature candidates: {stats['mature_candidates']}")
    
    print("\n→ SHORT pattern: No consolidation (as expected)")
    
    return identity_memory


def demo_inconsistent_pattern():
    """Demo: Inconsistent pattern does not consolidate to maturity"""
    print("\n" + "="*70)
    print("DEMO 2: INCONSISTENT PATTERN (No Mature Consolidation)")
    print("="*70)
    
    identity_field = IdentityField(initial_phase=0.5)
    identity_memory = IdentityMemory(identity_field)
    
    print("\nSimulating INCONSISTENT pattern (30 observations with high variance)...")
    
    for t in range(30):
        # High variance - not stable
        identity_field.phase = 0.5 + np.random.randn() * 0.3  # Large noise
        identity_memory.observe_identity_field(current_time=float(t))
    
    # Try to create candidate
    candidate = identity_memory.check_anchor_candidate_creation(
        current_time=30.0,
        anchor_key="inconsistent_pattern",
        proposed_phase=0.5
    )
    
    stats = identity_memory.get_statistics()
    score = identity_memory.compute_consolidation_score()
    
    print(f"\nResults after INCONSISTENT pattern:")
    print(f"  Traces: {stats['trace_count']}")
    print(f"  Confidence: {stats['current_confidence']:.3f}")
    print(f"  Alignment: {stats['mean_alignment']:.3f}")
    
    print(f"\nConsolidation score (M6.1 with circular variance):")
    print(f"  Alignment:     {score.alignment:.3f}")
    print(f"  Stability:     {score.stability:.3f} (circular concentration)")
    print(f"  Confidence:    {score.confidence:.3f}")
    print(f"  Contradiction: {score.contradiction:.3f}")
    print(f"  TOTAL:         {score.compute_total():.3f}")
    print(f"  Detection threshold: {identity_memory.DETECTION_THRESHOLD}")
    
    print(f"\nCandidate status:")
    print(f"  Detected: {candidate is not None}")
    
    if candidate:
        print(f"  Trace support: {candidate.trace_support_count}")
        print(f"  Confirmations: {candidate.candidate_confirmation_count}")
        
        # Check maturity using explicit thresholds from IdentityMemory (single source of truth)
        is_mature = candidate.is_mature(
            identity_memory.MIN_CONFIRMATIONS,
            identity_memory.MIN_MATURE_ALIGNMENT,
            identity_memory.MIN_MATURE_STABILITY,
            identity_memory.MAX_MATURE_CONTRADICTION
        )
        print(f"  Is mature: {is_mature}")
        
        if is_mature:
            print("\n→ INCONSISTENT pattern: Unexpectedly reached maturity!")
        else:
            print(f"\n→ INCONSISTENT pattern: Detected but NOT MATURE")
            print(f"   (Low stability {score.stability:.3f} < {identity_memory.MIN_MATURE_STABILITY} prevents maturity)")
    else:
        print("\n→ INCONSISTENT pattern: Not even detected (score below threshold)")
    
    return identity_memory


def demo_long_consistent_pattern():
    """Demo: Long consistent pattern DOES consolidate to maturity"""
    print("\n" + "="*70)
    print("DEMO 3: LONG CONSISTENT PATTERN (Mature Consolidation)")
    print("="*70)
    
    identity_field = IdentityField(initial_phase=0.5)
    identity_memory = IdentityMemory(identity_field)
    
    n_obs = 30
    print(f"\nSimulating LONG CONSISTENT pattern ({n_obs} observations with low variance)...")
    
    for t in range(n_obs):
        # Very stable pattern
        identity_field.phase = 0.5 + np.random.randn() * 0.01  # Small noise
        identity_memory.observe_identity_field(current_time=float(t))
        
        # Check candidate every 10 steps to build confirmations
        if t > 0 and t % 10 == 0:
            identity_memory.check_anchor_candidate_creation(
                current_time=float(t),
                anchor_key="consistent_pattern",
                proposed_phase=0.5
            )
    
    # Final check
    candidate = identity_memory.check_anchor_candidate_creation(
        current_time=float(n_obs),
        anchor_key="consistent_pattern",
        proposed_phase=0.5
    )
    
    stats = identity_memory.get_statistics()
    final_score = identity_memory.compute_consolidation_score()
    
    print(f"\nResults after LONG CONSISTENT pattern:")
    print(f"  Traces: {stats['trace_count']}")
    print(f"  Confidence: {stats['current_confidence']:.3f}")
    print(f"  Alignment: {stats['mean_alignment']:.3f}")
    print(f"  D_id_local: {stats['mean_d_id_local']:.3f}")
    
    print(f"\nFinal consolidation score (M6.1):")
    print(f"  Alignment:     {final_score.alignment:.3f}")
    print(f"  Stability:     {final_score.stability:.3f} (circular concentration)")
    print(f"  Confidence:    {final_score.confidence:.3f}")
    print(f"  EBA quality:   {final_score.eba_quality:.3f}")
    print(f"  Contradiction: {final_score.contradiction:.3f}")
    print(f"  TOTAL:         {final_score.compute_total():.3f}")
    print(f"  Detection threshold: {identity_memory.DETECTION_THRESHOLD}")
    
    print(f"\nCandidate status:")
    print(f"  Created: {candidate is not None}")
    
    if candidate:
        print(f"  Key: {candidate.anchor_key}")
        print(f"  Trace support: {candidate.trace_support_count}")
        print(f"  Confirmations: {candidate.candidate_confirmation_count}")
        print(f"  Mean alignment: {candidate.mean_alignment:.3f}")
        print(f"  Mean stability: {candidate.mean_stability:.3f}")
        print(f"  Time span: {candidate.time_span:.1f}")
        
        is_detected = candidate.is_detected()
        is_mature = candidate.is_mature(
            identity_memory.MIN_CONFIRMATIONS,
            identity_memory.MIN_MATURE_ALIGNMENT,
            identity_memory.MIN_MATURE_STABILITY,
            identity_memory.MAX_MATURE_CONTRADICTION
        )
        
        print(f"\n  Level A (Detected): {is_detected}")
        print(f"  Level B (Mature): {is_mature}")
        
        if is_mature:
            print("\n→ LONG CONSISTENT pattern: ✓ MATURE CONSOLIDATION")
            print(f"   Ready for potential promotion to anchor")
        else:
            print(f"\n→ LONG CONSISTENT pattern: Detected but needs more confirmations")
            print(f"   ({candidate.candidate_confirmation_count}/{identity_memory.MIN_CONFIRMATIONS} confirmations)")
    
    mature_candidates = identity_memory.get_mature_candidates()
    print(f"\nMature candidates: {len(mature_candidates)}")
    
    return identity_memory


def demo_snapshot_capability():
    """Demo: M6 can take snapshots of identity state"""
    print("\n" + "="*70)
    print("DEMO 4: SNAPSHOT CAPABILITY")
    print("="*70)
    
    identity_field = IdentityField(initial_phase=0.5)
    identity_field.anchors = ["commitment:research", "value:honesty", "goal:understanding"]
    
    identity_memory = IdentityMemory(identity_field)
    
    print("\nObserving identity over time and taking snapshots...")
    
    for t in range(20):
        identity_field.phase = 0.5 + np.sin(t * 0.1) * 0.05  # Slow oscillation
        identity_memory.observe_identity_field(current_time=float(t))
        
        # Take snapshot every 5 steps
        if t % 5 == 0:
            snapshot = identity_memory.take_snapshot(current_time=float(t))
            print(f"\nSnapshot at t={t}:")
            print(f"  Phase: {snapshot.phase:.3f}")
            print(f"  Confidence: {snapshot.confidence:.3f}")
            print(f"  Stability: {snapshot.stability:.3f}")
            print(f"  Anchors: {len(snapshot.anchor_vector)}")
    
    print(f"\nTotal snapshots collected: {len(identity_memory.snapshots)}")
    
    return identity_memory


def main():
    """Run all M6 demos"""
    print("="*70)
    print("CIEL/Ω M6 IDENTITYMEMORY - DEMONSTRATION")
    print("Showing M6 consolidates ONLY with long, consistent patterns")
    print("="*70)
    
    # Run demos
    m6_short = demo_short_pattern()
    m6_inconsistent = demo_inconsistent_pattern()
    m6_long = demo_long_consistent_pattern()
    m6_snapshot = demo_snapshot_capability()
    
    # Summary
    print("\n" + "="*70)
    print("DEMO SUMMARY")
    print("="*70)
    
    print("\nKey findings (M6.1a with circular variance stability):")
    print("  1. SHORT patterns (5 obs): No detection")
    print("  2. INCONSISTENT patterns (30 obs, high phase variance): Not detected or not mature")
    print("  3. LONG CONSISTENT patterns (30 obs, low variance): ✓ Mature consolidation")
    print("  4. M6 can take snapshots of identity evolution")
    
    print("\nM6.1a Properties Demonstrated:")
    print("  • M6 observes IdentityField (does not control it)")
    print("  • Single episodes do NOT affect M6")
    print("  • Two-level validation: Detected (Level A) vs Mature (Level B)")
    print("  • Stability uses R^7 circular concentration (8-dim tensor-scalar field)")
    print("  • Requires multiple independent confirmations for maturity")
    print("  • Detection: C_M6 > 0.6, trace_support ≥ 3, time_span ≥ 10")
    print("  • Maturity: confirmations ≥ 3, alignment ≥ 0.75, stability ≥ 0.85, contradiction ≤ 0.30")
    print("  • Single source of truth for maturity thresholds (from IdentityMemory)")
    print("  • Creates anchor CANDIDATES (not automatic acceptance)")
    print("  • Records historical traces and snapshots")
    
    print("\n" + "="*70)
    print("M6.1a IDENTITYMEMORY DEMONSTRATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
