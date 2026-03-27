from ciel_omega.memory import HolonomicMemoryOrchestrator


def main():
    orch = HolonomicMemoryOrchestrator()
    events = [
        {'content': 'Adrian prefers rigor', 'salience': 0.85, 'confidence': 0.9},
        {'content': 'Adrian prefers rigor', 'salience': 0.86, 'confidence': 0.9},
        {'content': 'Adrian prefers rigor', 'salience': 0.84, 'confidence': 0.9},
        {'content': 'Adrian prefers rigor', 'salience': 0.87, 'confidence': 0.9},
        {'content': 'Adrian prefers rigor', 'salience': 0.83, 'confidence': 0.9},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.81, 'confidence': 0.86},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.82, 'confidence': 0.86},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.83, 'confidence': 0.86},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.84, 'confidence': 0.86},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.85, 'confidence': 0.86},
        {'content': 'Risk of harm detected', 'salience': 0.95, 'confidence': 0.9},
        {'content': 'Risk of harm detected', 'salience': 0.94, 'confidence': 0.9},
        {'content': 'Risk of harm detected', 'salience': 0.96, 'confidence': 0.9},
        {'content': 'Risk of harm detected', 'salience': 0.93, 'confidence': 0.9},
        {'content': 'Risk of harm detected', 'salience': 0.97, 'confidence': 0.9},
    ]

    print('=== HOLOMONIC MEMORY ORCHESTRATOR DEMO ===')
    for idx, result in enumerate(orch.run_sequence(events), start=1):
        print(f"Cycle {idx}: content={result.content!r}")
        print(f"  keys: M0={result.perceptual_key} | M1={result.working_key}")
        print(f"  consolidations: semantic={result.consolidations.semantic_item or result.consolidations.semantic_candidate} | "
              f"procedural={result.consolidations.procedural_item or result.consolidations.procedural_candidate} | "
              f"affective={result.consolidations.affective_item or result.consolidations.affective_candidate}")
        print(f"  EBA short defect={result.eba_results['short'].defect_magnitude:.4f} coherent={result.eba_results['short'].is_coherent}")
        print(f"  energy: V_static={result.energy['V_static']:.4f}, R_noise={result.energy['R_noise']:.4f}")

    snapshot = orch.snapshot()
    print('\n=== FINAL SNAPSHOT ===')
    print(snapshot)
    print('\n=== RETRIEVAL: "rigor" ===')
    retrieved = orch.retrieve('rigor', top_k=3)
    for channel, values in retrieved.items():
        if channel == 'episodic':
            print(f"  {channel}: {len(values)} recent episodes")
        else:
            print(f"  {channel}: {len(values)} hits")
    print('\nCounts:', snapshot.counts)


if __name__ == '__main__':
    main()
