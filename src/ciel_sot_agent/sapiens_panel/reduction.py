from __future__ import annotations

from typing import Any

from ..sapiens_client import SapiensSession


def build_reduction_state(
    bridge_summary: dict[str, Any],
    session: SapiensSession,
    packet: dict[str, Any],
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    settings = settings or {}
    reduction_policy = dict(settings.get('reduction_policy', {}))
    threshold = float(reduction_policy.get('readiness_threshold', 0.62))
    coherence_index = float(bridge_summary.get('state_manifest', {}).get('coherence_index', 0.0))
    system_health = float(bridge_summary.get('health_manifest', {}).get('system_health', 0.0))
    closure_penalty = float(bridge_summary.get('health_manifest', {}).get('closure_penalty', 0.0))

    orchestration_state = {
        'orbital_mode': bridge_summary.get('recommended_control', {}).get('mode', 'guided'),
        'recommended_action': bridge_summary.get('health_manifest', {}).get('recommended_action', 'guided interaction'),
        'coherence_index': coherence_index,
        'system_health': system_health,
    }

    readiness_score = max(0.0, min(1.0, 0.55 * coherence_index + 0.45 * system_health - 0.05 * closure_penalty))
    reduction_ready = readiness_score >= threshold

    reduction_state = {
        'readiness_threshold': threshold,
        'readiness_score': readiness_score,
        'reduction_ready': reduction_ready,
        'closure_penalty': closure_penalty,
        'commit_action': 'Commit Reduction / Identity Update' if reduction_ready else 'Hold Reduction / Continue Orchestration',
    }

    excerpt = list(packet.get('memory_excerpt', []))
    memory_residue = {
        'policy': reduction_policy.get('memory_residue_policy', 'session-residue'),
        'turn_count': len(session.memory),
        'residue_count': len(excerpt),
        'residue_excerpt': excerpt,
        'identity_anchor': {
            'sapiens_id': session.identity.sapiens_id,
            'relation_label': session.identity.relation_label,
            'truth_axis': session.identity.truth_axis,
        },
    }

    return {
        'schema': 'ciel-sot-agent/sapiens-reduction-state/v0.1',
        'orchestration_state': orchestration_state,
        'reduction_state': reduction_state,
        'memory_residue': memory_residue,
    }
