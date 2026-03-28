from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import src.ciel_sot_agent.sapiens_client as sapiens_client

EPISTEMIC_SEPARATION = ['fact', 'inference', 'hypothesis', 'unknown']


def _surface_policy(session: sapiens_client.SapiensSession) -> dict[str, Any]:
    geom = session.state_geometry or {}
    surface = geom.get('surface', {}) if isinstance(geom, dict) else {}
    mode = session.control_profile.get('mode') or surface.get('mode', 'standard')
    return {
        'mode': mode,
        'truth_over_smoothing': True,
        'explicit_uncertainty': True,
        'epistemic_separation': list(EPISTEMIC_SEPARATION),
    }



def _build_model_packet_v02(session: sapiens_client.SapiensSession, user_text: str) -> dict[str, Any]:
    sapiens_client.append_turn(session, 'sapiens', user_text)
    geom = session.state_geometry
    surface_policy = _surface_policy(session)
    return {
        'schema': 'ciel-sot-agent/sapiens-client-packet/v0.2',
        'identity': asdict(session.identity),
        'session': {
            'created_at': session.created_at,
            'updated_at': session.updated_at,
            'turn_count': len(session.memory),
        },
        'state_geometry': geom,
        'control_profile': session.control_profile,
        'surface_policy': surface_policy,
        'latest_user_turn': user_text,
        'memory_excerpt': [asdict(turn) for turn in session.memory[-6:]],
        'inference_contract': {
            'relation_before_identity': True,
            'identity_before_memory': True,
            'mode': session.control_profile.get('mode', 'standard'),
            'truth_axis': session.identity.truth_axis,
            'epistemic_separation': list(EPISTEMIC_SEPARATION),
        },
    }



def _persist_session_v02(root: str | Path, session: sapiens_client.SapiensSession, packet: dict[str, Any]) -> dict[str, str]:
    root = Path(root)
    report_dir = root / sapiens_client.CLIENT_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    session_path = report_dir / 'session.json'
    packet_path = report_dir / 'latest_packet.json'
    policy_path = report_dir / 'surface_policy.json'
    transcript_path = report_dir / 'transcript.md'

    surface_policy = packet.get('surface_policy', _surface_policy(session))

    session_path.write_text(json.dumps(asdict(session), ensure_ascii=False, indent=2), encoding='utf-8')
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding='utf-8')
    policy_path.write_text(json.dumps(surface_policy, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# Sapiens Session Transcript', '']
    for turn in session.memory:
        lines.append(f'## {turn.role} @ {turn.timestamp}')
        lines.append(turn.content)
        lines.append('')
    transcript_path.write_text('\n'.join(lines), encoding='utf-8')
    return {
        'session_json': str(session_path),
        'latest_packet_json': str(packet_path),
        'surface_policy_json': str(policy_path),
        'transcript_md': str(transcript_path),
    }


sapiens_client.build_model_packet = _build_model_packet_v02
sapiens_client.persist_session = _persist_session_v02
