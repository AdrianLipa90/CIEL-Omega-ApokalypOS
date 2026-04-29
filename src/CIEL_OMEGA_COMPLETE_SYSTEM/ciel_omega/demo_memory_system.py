"""CIEL/Ω Memory Architecture - Demonstration

Shows memory system M0-M8 in action:
- Phase dynamics
- Coupling between channels  
- Potential minimization
- Episodic storage and consolidation
- Braid memory tracking
- Audit logging

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

import numpy as np
from pathlib import Path

from memory import (
    MemoryDynamicsEngine,
    MemorySystemState,
    EpisodicMemory,
    BraidInvariantMemory,
    AuditJournalMemory,
    print_coupling_summary,
    CHANNEL_NAMES,
)


def demo_coupling_matrix():
    """Demonstrate coupling matrix structure"""
    print("\n" + "="*70)
    print("DEMO 1: COUPLING MATRIX")
    print("="*70)
    print_coupling_summary()


def demo_phase_dynamics():
    """Demonstrate phase evolution under coupling and potential"""
    print("\n" + "="*70)
    print("DEMO 2: PHASE DYNAMICS")
    print("="*70)
    
    # Initialize dynamics engine
    engine = MemoryDynamicsEngine()
    
    # Start with random initial phases near identity
    initial_phases = np.random.randn(8) * 0.2
    state = engine.initialize_state(initial_phases, initial_identity_phase=0.0)
    
    print(f"\nInitial phases:")
    for k in range(8):
        print(f"  {CHANNEL_NAMES[k]:25s}: {state.phases[k]:.4f} rad")
    
    # Evolve for 100 steps
    print(f"\nEvolving for 100 timesteps (dt=0.1)...")
    
    dt = 0.1
    num_steps = 100
    
    # Add small input force to M1 (working memory)
    input_forces = np.zeros(8)
    input_forces[1] = 0.5  # Push M1
    
    final_state = engine.integrate(num_steps, dt, input_forces)
    
    print(f"\nFinal phases after evolution:")
    for k in range(8):
        print(f"  {CHANNEL_NAMES[k]:25s}: {final_state.phases[k]:.4f} rad")
    
    # Analyze stability
    print(f"\nStability analysis:")
    stability = engine.compute_stability_metrics(final_state)
    
    print(f"  Mean identity coherence: {stability['mean_coherence']:.4f}")
    print(f"  Maximum drift ratio: {stability['max_drift_ratio']:.4f}")
    print(f"  System stable: {stability['is_stable']}")
    print(f"  Total potential: {stability['energy']['V_static']:.4f}")
    
    # Show static potential components
    comp = stability['energy']['static_components']
    print(f"\n  Static potential breakdown:")
    print(f"    Alignment:  {comp['alignment']*100:.1f}%")
    print(f"    Conflict:   {comp['conflict']*100:.1f}%")
    print(f"    Drift:      {comp['drift']*100:.1f}%")
    
    # Show dissipation separately
    R_noise = stability['energy']['R_noise']
    print(f"\n  Dissipation R_noise: {R_noise:.4f}")
    
    return engine, final_state


def demo_episodic_memory():
    """Demonstrate episodic memory M2"""
    print("\n" + "="*70)
    print("DEMO 3: EPISODIC MEMORY (M2)")
    print("="*70)
    
    # Create episodic memory
    episodic = EpisodicMemory()
    
    # Store some episodes
    episodes_data = [
        {
            'content': 'User asked about quantum mechanics',
            'context': {'topic': 'physics', 'mood': 'curious'},
            'result': 'Provided detailed explanation',
            'salience': 0.8,
            'identity_impact': 0.6,
        },
        {
            'content': 'Discussion about ethics in AI',
            'context': {'topic': 'ethics', 'mood': 'serious'},
            'result': 'Explored alignment principles',
            'salience': 0.9,
            'identity_impact': 0.9,
        },
        {
            'content': 'Casual conversation about weather',
            'context': {'topic': 'casual', 'mood': 'light'},
            'result': 'Brief exchange',
            'salience': 0.3,
            'identity_impact': 0.1,
        },
        {
            'content': 'Deep discussion on consciousness',
            'context': {'topic': 'consciousness', 'mood': 'profound'},
            'result': 'Explored phenomenology and qualia',
            'salience': 0.95,
            'identity_impact': 0.95,
        },
    ]
    
    print(f"\nStoring {len(episodes_data)} episodes...")
    
    for ep_data in episodes_data:
        episodic.store(ep_data['content'], metadata=ep_data)
    
    # Show statistics
    stats = episodic.get_statistics()
    print(f"\nEpisodic memory statistics:")
    print(f"  Total episodes: {stats['count']}")
    print(f"  Mean salience: {stats['mean_salience']:.3f}")
    print(f"  Mean identity impact: {stats['mean_identity_impact']:.3f}")
    print(f"  Consolidation candidates: {stats['consolidation_candidates']}")
    
    # Check consolidation candidates
    candidates = episodic.get_consolidation_candidates(min_score=0.8)
    print(f"\nHigh-value episodes ready for consolidation to semantic (M3):")
    for episode in candidates:
        print(f"  - {episode.content[:50]}")
        print(f"    Salience: {episode.salience:.2f}, Impact: {episode.identity_impact:.2f}")
        print(f"    Score: {episode.consolidation_score:.2f}")
    
    # Retrieve by query
    print(f"\nRetrieving episodes about 'consciousness'...")
    results = episodic.retrieve({'context_match': {'topic': 'consciousness'}})
    print(f"  Found {len(results)} matching episode(s)")
    
    return episodic


def demo_braid_memory():
    """Demonstrate braid/invariant memory M7"""
    print("\n" + "="*70)
    print("DEMO 4: BRAID/INVARIANT MEMORY (M7)")
    print("="*70)
    
    # Create braid memory
    braid = BraidInvariantMemory()
    
    # Simulate phase trajectory
    print(f"\nSimulating phase trajectory (200 steps)...")
    
    phases = []
    phase = 0.0
    
    for t in range(200):
        # Random walk with slight drift
        phase += np.random.randn() * 0.1 + 0.01
        phase = phase % (2 * np.pi)
        phases.append(phase)
        
        # Update braid state
        braid.state.phase = phase
        braid.update_phase_history()
        
        # Store significant points
        if t % 20 == 0:
            braid.store(
                content=f"State at t={t}",
                metadata={'timestamp': t, 'phase': phase}
            )
    
    # Show braid statistics
    print(f"\nBraid memory units: {len(braid.units)}")
    print(f"  Coherence: {braid.compute_coherence():.4f}")
    print(f"  Detected loops: {len(braid.detected_loops)}")
    print(f"  Topological scars: {len(braid.scars)}")
    
    # Compute drift signature
    drift_sig = braid.compute_drift_signature()
    if drift_sig['status'] != 'insufficient_history':
        print(f"\nDrift signature:")
        print(f"  Drift rate: {drift_sig['drift_rate']:.6f} rad/step")
        print(f"  Phase variance: {drift_sig['variance']:.4f}")
        if drift_sig['dominant_period']:
            print(f"  Dominant period: {drift_sig['dominant_period']:.1f} steps")
    
    # Show mean phasor
    mean_phasor = braid.mean_phasor()
    print(f"\nMean phasor:")
    print(f"  Magnitude: {abs(mean_phasor):.4f}")
    print(f"  Phase: {np.angle(mean_phasor):.4f} rad")
    
    return braid


def demo_audit_journal():
    """Demonstrate audit/journal memory M8"""
    print("\n" + "="*70)
    print("DEMO 5: AUDIT/JOURNAL MEMORY (M8)")
    print("="*70)
    
    # Create audit journal
    journal = AuditJournalMemory()
    
    # Log various events
    print(f"\nLogging system events...")
    
    journal.log_decision(
        description="Initialized memory system with 8 channels",
        metadata={'timestamp': 0}
    )
    
    journal.log_promotion(
        memory_content="Quantum mechanics discussion",
        source_channel=2,  # Episodic
        target_channel=3,  # Semantic
        score=0.92,
        reason="High salience and stability"
    )
    
    journal.log_conflict(
        channels=[1, 5],  # Working vs Affective
        description="Working memory conflict with ethical constraints",
        resolution="Ethical bounds enforced, working memory adjusted"
    )
    
    journal.log_defect(
        channel=7,  # Braid
        defect_type="holonomy",
        magnitude=0.15,
        description="Small holonomy defect detected in loop closure"
    )
    
    journal.log_consolidation(
        source_channel=2,  # Episodic
        target_channel=3,  # Semantic
        num_memories=3,
        success_rate=0.85
    )
    
    # Show report
    print(f"\n{journal.generate_report()}")
    
    # Analyze specific channel
    print(f"\nChannel M2 (Episodic) activity:")
    activity = journal.analyze_channel_activity(2)
    print(f"  Total entries: {activity['total_entries']}")
    print(f"  By type: {activity['by_type']}")
    
    return journal


def demo_integrated_system():
    """Demonstrate integrated system with all components"""
    print("\n" + "="*70)
    print("DEMO 6: INTEGRATED SYSTEM")
    print("="*70)
    
    print(f"\nInitializing integrated memory system...")
    
    # Create all components
    dynamics = MemoryDynamicsEngine()
    episodic = EpisodicMemory()
    braid = BraidInvariantMemory()
    journal = AuditJournalMemory()
    
    # Initialize system state
    state = dynamics.initialize_state()
    journal.log_decision("System initialized", metadata={'phase': state.identity_phase})
    
    # Simulate interaction: new high-impact episode
    print(f"\nProcessing high-impact event...")
    
    episode_data = {
        'content': 'Breakthrough insight on identity alignment',
        'context': {'topic': 'identity', 'breakthrough': True},
        'result': 'Major conceptual advancement',
        'salience': 0.98,
        'identity_impact': 0.95,
    }
    
    # Store in episodic
    episodic.store(episode_data['content'], metadata=episode_data)
    journal.log_decision(
        f"Stored high-impact episode (salience={episode_data['salience']:.2f})",
        metadata=episode_data
    )
    
    # Apply input force to system
    input_forces = np.zeros(8)
    input_forces[2] = episode_data['salience']  # M2 gets force
    input_forces[6] = episode_data['identity_impact'] * 0.5  # M6 influenced
    
    # Evolve system
    print(f"Evolving system dynamics...")
    state = dynamics.step(state, dt=0.1, input_forces=input_forces)
    
    # Update braid with new state
    braid.state.phase = state.phases[7]
    braid.update_phase_history()
    braid.store("State after high-impact event", metadata={'timestamp': 1})
    
    # Check for consolidation
    candidates = episodic.get_consolidation_candidates(min_score=0.9)
    if candidates:
        print(f"\nConsolidation check:")
        print(f"  Found {len(candidates)} candidate(s) for promotion to semantic memory")
        journal.log_promotion(
            memory_content=candidates[0].content,
            source_channel=2,
            target_channel=3,
            score=candidates[0].consolidation_score,
            reason="Exceeded consolidation threshold"
        )
    
    # Show final state
    print(f"\nFinal system state:")
    stability = dynamics.compute_stability_metrics(state)
    print(f"  Identity coherence: {stability['mean_coherence']:.4f}")
    print(f"  System stable: {stability['is_stable']}")
    print(f"  Total potential: {stability['energy']['V_static']:.4f}")
    
    print(f"\nMemory statistics:")
    print(f"  Episodic: {len(episodic.episodes)} episodes")
    print(f"  Braid: {len(braid.units)} units, coherence={braid.compute_coherence():.3f}")
    print(f"  Journal: {len(journal.entries)} audit entries")
    
    return dynamics, episodic, braid, journal


def main():
    """Run all demonstrations"""
    print("="*70)
    print("CIEL/Ω MEMORY ARCHITECTURE DEMONSTRATION")
    print("M0-M8 Phase-Based Memory System")
    print("="*70)
    
    # Run demos
    demo_coupling_matrix()
    engine, state = demo_phase_dynamics()
    episodic = demo_episodic_memory()
    braid = demo_braid_memory()
    journal = demo_audit_journal()
    dynamics, episodic, braid, journal = demo_integrated_system()
    
    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nImplemented components:")
    print("  ✓ Phase state infrastructure (base.py)")
    print("  ✓ Coupling matrix J_kj (coupling.py)")
    print("  ✓ Memory potentials V_mem (potential.py)")
    print("  ✓ Dynamics integration (dynamics.py)")
    print("  ✓ M2 Episodic Memory")
    print("  ✓ M7 Braid/Invariant Memory")
    print("  ✓ M8 Audit/Journal Memory")
    print()
    print("Implemented channels in this consolidated build:")
    print("  ✓ M0 Perceptual Memory")
    print("  ✓ M1 Working Memory")
    print("  ✓ M2 Episodic Memory")
    print("  ✓ M3 Semantic Memory")
    print("  ✓ M4 Procedural Memory")
    print("  ✓ M5 Affective/Ethical Memory")
    print("  ✓ M6 Identity Trace Memory")
    print("  ✓ M7 Braid/Invariant Memory")
    print("  ✓ M8 Audit/Journal Memory")
    print()
    print("Still missing in the full architecture:")
    print("  - HolonomicMemoryOrchestrator")
    print("  - RelationEngine")
    print("  - IdentitySynthesizer")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
