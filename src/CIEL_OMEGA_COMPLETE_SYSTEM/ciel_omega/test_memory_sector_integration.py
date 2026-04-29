from memory import HolonomicMemoryOrchestrator


def test_memory_sector_integration_pipeline():
    orch = HolonomicMemoryOrchestrator()
    initial = orch.snapshot()
    events = [
        {'content': 'Adrian prefers rigor', 'salience': 0.85, 'confidence': 0.9},
        {'content': 'Adrian prefers rigor', 'salience': 0.86, 'confidence': 0.9},
        {'content': 'Adrian prefers rigor', 'salience': 0.84, 'confidence': 0.9},
        {'content': 'Adrian prefers rigor', 'salience': 0.87, 'confidence': 0.9},
        {'content': 'Adrian prefers rigor', 'salience': 0.83, 'confidence': 0.9},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.8, 'confidence': 0.85},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.82, 'confidence': 0.85},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.81, 'confidence': 0.85},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.83, 'confidence': 0.85},
        {'content': 'Use audit log for traceability', 'context': {'goal': 'trace decisions', 'action': 'use audit log'}, 'result': {'success': True}, 'salience': 0.84, 'confidence': 0.85},
        {'content': 'Risk of harm detected', 'salience': 0.95, 'confidence': 0.9},
        {'content': 'Risk of harm detected', 'salience': 0.94, 'confidence': 0.9},
        {'content': 'Risk of harm detected', 'salience': 0.96, 'confidence': 0.9},
        {'content': 'Risk of harm detected', 'salience': 0.93, 'confidence': 0.9},
        {'content': 'Risk of harm detected', 'salience': 0.97, 'confidence': 0.9},
    ]
    results = orch.run_sequence(events)
    final = orch.snapshot()

    assert len(results) == len(events)
    assert len(orch.m2.episodes) == len(events)
    assert orch.m3.items
    assert orch.m4.items
    assert orch.m5.items
    assert len(orch.m7.units) >= len(events)
    assert len(orch.m8.entries) >= len(events)
    assert all('short' in r.eba_results for r in results)
    assert final.energy['V_static'] >= 0.0
    assert final.defects['D_mem'] >= 0.0
    assert final.defects['D_id'] >= 0.0
    # no direct identity path during ordinary runtime
    assert len(orch.m6.anchor_candidates) == 0
    assert final.counts['m3_items'] >= 1
    assert final.counts['m4_items'] >= 1
    assert final.counts['m5_items'] >= 1
    # local kernel remained bounded
    assert final.energy['V_static'] <= initial.energy['V_static'] + 5.0
