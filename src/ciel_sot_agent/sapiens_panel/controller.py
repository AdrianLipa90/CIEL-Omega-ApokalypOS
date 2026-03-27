from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..orbital_bridge import build_orbital_bridge
from ..sapiens_client import SapiensIdentity, SapiensSession, initialize_session, persist_session
from .communication import build_communication_view
from .models import PanelSessionSummary, PanelState, PanelTabState
from .settings_store import load_panel_settings


def _load_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / 'integration' / 'sapiens' / 'panel_manifest.json'
    return json.loads(manifest_path.read_text(encoding='utf-8'))


def _session_summary(session: SapiensSession) -> PanelSessionSummary:
    return PanelSessionSummary(
        sapiens_id=session.identity.sapiens_id,
        relation_label=session.identity.relation_label,
        preferred_mode=session.identity.preferred_mode,
        created_at=session.created_at,
        updated_at=session.updated_at,
        turn_count=len(session.memory),
    )


def build_panel_state(root: str | Path, user_text: str = 'Hello, model.', sapiens_id: str = 'sapiens') -> PanelState:
    root = Path(root)
    settings = load_panel_settings(root)
    manifest = _load_manifest(root)
    bridge_summary = build_orbital_bridge(root)

    identity = SapiensIdentity(
        sapiens_id=sapiens_id,
        relation_label=str(settings.identity.get('relation_label', 'human-model')),
        preferred_mode=str(settings.identity.get('preferred_mode', 'guided')),
        truth_axis=str(settings.identity.get('truth_axis', 'truth')),
        memory_policy=str(settings.identity.get('memory_policy', 'session-first')),
    )
    session = initialize_session(root, identity=identity)
    communication = build_communication_view(session, user_text)
    paths = persist_session(root, session, communication['packet'])

    control_tab = PanelTabState(
        title='Control',
        summary={
            'coherence_index': bridge_summary.get('state_manifest', {}).get('coherence_index', 0.0),
            'closure_penalty': bridge_summary.get('health_manifest', {}).get('closure_penalty', 0.0),
            'system_health': bridge_summary.get('health_manifest', {}).get('system_health', 0.0),
            'mode': bridge_summary.get('recommended_control', {}).get('mode', 'guided'),
            'recommended_action': bridge_summary.get('health_manifest', {}).get('recommended_action', 'guided interaction'),
        },
        actions=['Run Orbital Pass', 'Run Bridge Update', 'Build Model Packet', 'Export Current State'],
    )

    settings_tab = PanelTabState(
        title='Settings',
        summary={
            'identity': settings.identity,
            'interaction_policy': settings.interaction_policy,
            'orbital_runtime': settings.orbital_runtime,
            'ui': settings.ui,
        },
        actions=['Update Settings', 'Reset Defaults'],
    )

    communication_tab = PanelTabState(
        title='Communication',
        summary=communication,
        actions=['Append User Turn', 'Persist Session', 'Export Transcript'],
    )

    support_tab = PanelTabState(
        title='Support',
        summary={
            'health_manifest': bridge_summary.get('health_manifest', {}),
            'recommended_control': bridge_summary.get('recommended_control', {}),
            'artifact_paths': paths,
        },
        actions=['Rebuild Manifests', 'Regenerate Bridge Report', 'Reset Session', 'Export Bundle'],
    )

    return PanelState(
        control=control_tab,
        settings=settings_tab,
        communication=communication_tab,
        support=support_tab,
        session=_session_summary(session),
        state_sources={
            'orbital': bridge_summary.get('source_paths', {}),
            'bridge': {'schema': bridge_summary.get('schema', '')},
            'session': paths,
            'settings': manifest.get('dependencies', {}),
        },
        manifest=manifest,
    )


def run_sapiens_panel(root: str | Path, user_text: str = 'Hello, model.', sapiens_id: str = 'sapiens') -> dict[str, Any]:
    state = build_panel_state(root, user_text=user_text, sapiens_id=sapiens_id)
    return {
        'schema': 'ciel-sot-agent/sapiens-panel-run/v0.1',
        'panel_state': {
            'control': state.control.summary,
            'settings': state.settings.summary,
            'communication': state.communication.summary,
            'support': state.support.summary,
            'session': {
                'sapiens_id': state.session.sapiens_id,
                'relation_label': state.session.relation_label,
                'preferred_mode': state.session.preferred_mode,
                'created_at': state.session.created_at,
                'updated_at': state.session.updated_at,
                'turn_count': state.session.turn_count,
            },
            'state_sources': state.state_sources,
            'manifest': state.manifest,
        },
    }
