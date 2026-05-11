from __future__ import annotations

from src.ciel_sot_agent.noema_sot import _project_memory_field


def test_project_memory_field_returns_projection_metrics() -> None:
    subsystems = {
        "a": {
            "M_sem": 1.0,
            "orbital_level": 1,
            "metrics": {
                "coherence_index": 0.8,
                "system_health": 0.7,
                "closure_penalty": 0.2,
                "ethical_score": 0.9,
                "soul_invariant": 0.85,
                "identity_phase": 0.12,
            },
        },
        "b": {
            "M_sem": 0.5,
            "orbital_level": 2,
            "metrics": {
                "coherence_index": 0.6,
                "system_health": 0.5,
                "closure_penalty": 0.3,
                "ethical_score": 0.8,
                "soul_invariant": 0.75,
                "identity_phase": 0.18,
            },
        },
    }
    pipeline = {
        "coherence_index": 0.75,
        "system_health": 0.65,
        "closure_penalty": 0.25,
        "ethical_score": 0.88,
        "soul_invariant": 0.8,
        "identity_phase": 0.14,
    }

    proj = _project_memory_field(subsystems, pipeline)

    assert 0.0 <= proj["projection_confidence"] <= 1.0
    assert 0.0 <= proj["projection_residual"] <= 1.0
    assert 0.0 <= proj["j_noema"] <= 1.0
    assert proj["projected_centroid"]["coherence_index"] > 0.0
