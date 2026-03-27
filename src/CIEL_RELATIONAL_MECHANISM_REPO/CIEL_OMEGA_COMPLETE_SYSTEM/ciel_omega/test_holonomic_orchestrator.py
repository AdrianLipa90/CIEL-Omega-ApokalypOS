from memory import HolonomicMemoryOrchestrator


def test_basic_pipeline_creates_core_records():
    orch = HolonomicMemoryOrchestrator()
    result = orch.process_input('Adrian prefers rigor', {'salience': 0.8, 'confidence': 0.9, 'modality': 'text'})
    assert result.perceptual_key.startswith('text:')
    assert result.working_key == 'adrian prefers rigor'
    assert len(orch.m2.episodes) == 1
    assert len(orch.m8.entries) >= 1
    assert 'short' in result.eba_results
    assert result.energy['V_static'] >= 0.0


def test_repeated_fact_consolidates_semantic():
    orch = HolonomicMemoryOrchestrator()
    for _ in range(5):
        orch.process_input('Adrian prefers rigor', {'salience': 0.9, 'confidence': 0.9})
    assert 'adrian prefers rigor' in orch.m3.items
    item = orch.m3.items['adrian prefers rigor']
    assert item.status == 'active'


def test_repeated_goal_action_consolidates_procedural():
    orch = HolonomicMemoryOrchestrator()
    for _ in range(5):
        orch.process_input(
            'Use audit log for traceability',
            {
                'context': {'goal': 'trace decisions', 'action': 'use audit log'},
                'result': {'success': True},
                'salience': 0.85,
                'confidence': 0.85,
            },
        )
    key = 'trace decisions -> use audit log'
    assert key in orch.m4.items


def test_repeated_alert_consolidates_affective():
    orch = HolonomicMemoryOrchestrator()
    for _ in range(5):
        orch.process_input('Risk of harm detected', {'salience': 0.95, 'confidence': 0.9})
    assert 'risk of harm detected' in orch.m5.items


def test_no_direct_identity_candidate_without_anchor_key():
    orch = HolonomicMemoryOrchestrator(identity_phase=0.4)
    before_phase = orch.identity_field.phase
    for _ in range(4):
        orch.process_input('Neutral observation', {'salience': 0.4, 'confidence': 0.5})
    assert orch.identity_field.phase == before_phase
    assert len(orch.m6.anchor_candidates) == 0


def test_retrieval_cross_channel_returns_ranked_results():
    orch = HolonomicMemoryOrchestrator()
    for _ in range(5):
        orch.process_input('Adrian prefers rigor', {'salience': 0.85, 'confidence': 0.9})
    results = orch.retrieve('rigor', top_k=3)
    assert results['semantic']
    assert results['working']
    assert results['perceptual']
    assert results['semantic'][0]['item'].semantic_key == 'adrian prefers rigor'
