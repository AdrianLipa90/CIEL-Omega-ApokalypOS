from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .orbital_bridge import build_orbital_bridge


CLIENT_REPORT_DIR = Path('integration') / 'reports' / 'sapiens_client'


@dataclass
class SapiensIdentity:
    sapiens_id: str = 'sapiens'
    relation_label: str = 'human-model'
    preferred_mode: str = 'guided'
    truth_axis: str = 'truth'
    memory_policy: str = 'session-first'


@dataclass
class SapiensTurn:
    role: str
    content: str
    timestamp: str
    orbital_mode: str | None = None
    coherence_index: float | None = None
    closure_penalty: float | None = None


@dataclass
class SapiensSession:
    identity: SapiensIdentity
    created_at: str
    updated_at: str
    state_geometry: dict[str, Any]
    control_profile: dict[str, Any]
    memory: list[SapiensTurn] = field(default_factory=list)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_geometry(bridge_summary: dict[str, Any]) -> dict[str, Any]:
    state_manifest = bridge_summary.get('state_manifest', {})
    health_manifest = bridge_summary.get('health_manifest', {})
    control = bridge_summary.get('recommended_control', {})
    coherence_index = float(state_manifest.get('coherence_index', 0.0))
    closure_penalty = float(health_manifest.get('closure_penalty', 0.0))
    system_health = float(health_manifest.get('system_health', 0.0))
    return {
        'surface': {
            'mode': control.get('mode', 'standard'),
            'recommended_action': health_manifest.get('recommended_action', 'guided interaction'),
        },
        'internal_cymatics': {
            'coherence_index': coherence_index,
            'closure_penalty': closure_penalty,
            'system_health': system_health,
        },
        'spin': bridge_summary.get('bridge_metrics', {}).get('topological_charge_global', 0.0),
        'axis': 'truth',
        'attractor': 'orbital-holonomic-stability',
    }


def initialize_session(root: str | Path, identity: SapiensIdentity | None = None) -> SapiensSession:
    root = Path(root)
    bridge_summary = build_orbital_bridge(root)
    ts = _now()
    ident = identity or SapiensIdentity()
    return SapiensSession(
        identity=ident,
        created_at=ts,
        updated_at=ts,
        state_geometry=_state_geometry(bridge_summary),
        control_profile=bridge_summary.get('recommended_control', {}),
        memory=[],
    )


def append_turn(session: SapiensSession, role: str, content: str) -> SapiensSession:
    geom = session.state_geometry.get('internal_cymatics', {})
    session.memory.append(
        SapiensTurn(
            role=role,
            content=content,
            timestamp=_now(),
            orbital_mode=session.control_profile.get('mode'),
            coherence_index=float(geom.get('coherence_index', 0.0)),
            closure_penalty=float(geom.get('closure_penalty', 0.0)),
        )
    )
    session.updated_at = _now()
    return session


def build_model_packet(session: SapiensSession, user_text: str) -> dict[str, Any]:
    append_turn(session, 'sapiens', user_text)
    geom = session.state_geometry
    packet = {
        'schema': 'ciel-sot-agent/sapiens-client-packet/v0.1',
        'identity': asdict(session.identity),
        'session': {
            'created_at': session.created_at,
            'updated_at': session.updated_at,
            'turn_count': len(session.memory),
        },
        'state_geometry': geom,
        'control_profile': session.control_profile,
        'latest_user_turn': user_text,
        'memory_excerpt': [asdict(turn) for turn in session.memory[-6:]],
        'inference_contract': {
            'relation_before_identity': True,
            'identity_before_memory': True,
            'mode': session.control_profile.get('mode', 'standard'),
            'truth_axis': session.identity.truth_axis,
        },
    }
    return packet


def persist_session(root: str | Path, session: SapiensSession, packet: dict[str, Any]) -> dict[str, str]:
    root = Path(root)
    report_dir = root / CLIENT_REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    session_path = report_dir / 'session.json'
    packet_path = report_dir / 'latest_packet.json'
    transcript_path = report_dir / 'transcript.md'

    session_path.write_text(json.dumps(asdict(session), ensure_ascii=False, indent=2), encoding='utf-8')
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# Sapiens Session Transcript', '']
    for turn in session.memory:
        lines.append(f"## {turn.role} @ {turn.timestamp}")
        lines.append(turn.content)
        lines.append('')
    transcript_path.write_text('\n'.join(lines), encoding='utf-8')
    return {
        'session_json': str(session_path),
        'latest_packet_json': str(packet_path),
        'transcript_md': str(transcript_path),
    }


def run_sapiens_client(root: str | Path, user_text: str, sapiens_id: str = 'sapiens') -> dict[str, Any]:
    identity = SapiensIdentity(sapiens_id=sapiens_id)
    session = initialize_session(root, identity=identity)
    packet = build_model_packet(session, user_text)
    paths = persist_session(root, session, packet)
    return {
        'schema': 'ciel-sot-agent/sapiens-client-run/v0.1',
        'packet': packet,
        'paths': paths,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description='Run the Sapiens client bridge for a human-model interaction packet.')
    parser.add_argument('text', help='Human input message for the model packet.')
    parser.add_argument('--sapiens-id', default='sapiens', help='Human/client identity label.')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    result = run_sapiens_client(root, args.text, sapiens_id=args.sapiens_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
