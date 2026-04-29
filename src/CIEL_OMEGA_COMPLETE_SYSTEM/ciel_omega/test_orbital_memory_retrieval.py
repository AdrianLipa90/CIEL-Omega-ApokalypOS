from types import SimpleNamespace

from ciel_omega.ciel.engine import CielEngine
from ciel_omega.ciel.orbital_memory_retrieval import govern_sector_retrieval


class _DummySectorMemory:
    def __init__(self):
        self.orchestrator = SimpleNamespace(state=SimpleNamespace(phases=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.0, 0.05]))

    def retrieve(self, query: str, top_k: int = 5):
        return {
            'working': [
                {
                    'item': {
                        'canonical_text': 'near-phase memory',
                        'phase': 0.02,
                        'confidence': 0.8,
                        'identity_alignment': 0.9,
                        'context': {'control_mode': 'standard', 'rh_severity': 'low'},
                        'result': {'durable_write_allowed': True},
                    },
                    'score': 0.5,
                },
                {
                    'item': {
                        'canonical_text': 'far-phase memory',
                        'phase': 3.0,
                        'confidence': 0.8,
                        'identity_alignment': 0.9,
                        'context': {'control_mode': 'standard', 'rh_severity': 'low'},
                        'result': {'durable_write_allowed': True},
                    },
                    'score': 0.5,
                },
            ]
        }

    def snapshot(self):
        return {
            'identity_phase': 0.0,
            'latest_loop_status': {'short': True, 'deep': True},
        }


def test_governed_retrieval_exposes_ranked_scope():
    engine = CielEngine()
    engine.step('orbital memory trace alpha', context='retrieval/test')
    state = engine.step('orbital memory trace beta', context='retrieval/test')
    governed = state['sector_memory']['governed_retrieval']
    assert governed['scope'] in {'stabilize', 'narrow', 'focused', 'wide'}
    assert isinstance(governed['selected_channels'], list)
    assert isinstance(governed['ranked'], list)
    assert governed['ranked']
    assert all('channel' in row and 'score' in row for row in governed['ranked'])


def test_governed_retrieval_emits_holonomic_fields():
    engine = CielEngine()
    state = engine.step('bridge orbital runtime memory', context='retrieval/test')
    ranked = state['sector_memory']['governed_retrieval']['ranked']
    assert ranked
    row = ranked[0]
    for key in (
        'phase_alignment',
        'identity_attractor_score',
        'holonomy_quality',
        'holonomy_defect',
        'loop_coherent',
        'loop_type',
    ):
        assert key in row


def test_holonomic_ranking_prefers_phase_near_identity_and_current_orbit():
    sector_memory = _DummySectorMemory()
    governed = govern_sector_retrieval(
        sector_memory=sector_memory,
        query='memory',
        governor={'retrieval_top_k': 2, 'retrieval_scope': 'focused', 'write_mode': 'durable'},
        orbital={
            'final': {'zeta_effective_phase': 0.0},
            'control': {'mode': 'standard', 'target_phase_shift': 0.0},
            'rh_policy': {'severity': 'low'},
            'diagnostics': {'dominant_residual_sector': 'runtime', 'dominant_vorticity_sector': 'runtime'},
        },
    )
    ranked = governed['ranked']
    assert ranked[0]['text'] == 'near-phase memory'
    assert ranked[0]['phase_alignment'] > ranked[1]['phase_alignment']
    assert ranked[0]['identity_attractor_score'] > ranked[1]['identity_attractor_score']
    assert ranked[0]['holonomy_quality'] > ranked[1]['holonomy_quality']


def test_prompt_summary_prefers_governed_channels():
    engine = CielEngine()
    state = engine.step('bridge orbital runtime memory', context='retrieval/test')
    summary = state['sector_memory']['governed_retrieval']
    assert 'by_channel' in summary
    assert isinstance(summary['by_channel'], dict)
    assert 'holonomic_context' in summary
