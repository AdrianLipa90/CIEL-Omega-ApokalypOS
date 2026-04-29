from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..orbital_bridge import build_orbital_bridge
from ..sapiens_client import SapiensIdentity, SapiensSession, initialize_session, persist_session
from ..satellite_authority import require_interaction_surface, project_authority_summary
from .communication import build_communication_view
from .models import PanelSessionSummary, PanelState, PanelTabState
from .reduction import build_reduction_state
from .settings_store import load_panel_settings
from .support import build_support_view

_LOG = logging.getLogger(__name__)


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
    sapiens_authority = project_authority_summary(require_interaction_surface(root, 'SAT-SAPIENS-0001'))

    identity = SapiensIdentity(
        sapiens_id=sapiens_id,
        relation_label=str(settings.identity.get('relation_label', 'human-model')),
        preferred_mode=str(settings.identity.get('preferred_mode', 'guided')),
        truth_axis=str(settings.identity.get('truth_axis', 'truth')),
        memory_policy=str(settings.identity.get('memory_policy', 'session-first')),
    )
    session = initialize_session(root, identity=identity)
    communication = build_communication_view(session, user_text, root=root)
    reduction = build_reduction_state(
        bridge_summary,
        session,
        communication['packet'],
        settings={'reduction_policy': settings.reduction_policy},
    )
    paths = persist_session(root, session, communication['packet'])

    control_tab = PanelTabState(
        title='Control',
        summary={
            'coherence_index': bridge_summary.get('state_manifest', {}).get('coherence_index', 0.0),
            'closure_penalty': bridge_summary.get('health_manifest', {}).get('closure_penalty', 0.0),
            'system_health': bridge_summary.get('health_manifest', {}).get('system_health', 0.0),
            'mode': bridge_summary.get('recommended_control', {}).get('mode', 'guided'),
            'recommended_action': bridge_summary.get('health_manifest', {}).get('recommended_action', 'guided interaction'),
            'orchestration_state': reduction.get('orchestration_state', {}),
            'reduction_state': reduction.get('reduction_state', {}),
            'satellite_authority': sapiens_authority,
        },
        actions=['Run Orbital Pass', 'Run Bridge Update', 'Evaluate Reduction Readiness', 'Commit Reduction / Identity Update', 'Export Current State'],
    )

    settings_tab = PanelTabState(
        title='Settings',
        summary={
            'identity': settings.identity,
            'interaction_policy': settings.interaction_policy,
            'orbital_runtime': settings.orbital_runtime,
            'reduction_policy': settings.reduction_policy,
            'ui': settings.ui,
            'satellite_authority': sapiens_authority,
        },
        actions=['Update Settings', 'Reset Defaults'],
    )

    communication_tab = PanelTabState(
        title='Communication',
        summary={
            **communication,
            'reduction_state': reduction.get('reduction_state', {}),
            'memory_residue': reduction.get('memory_residue', {}),
            'satellite_authority': sapiens_authority,
        },
        actions=['Append User Turn', 'Persist Session', 'Export Transcript'],
    )

    support_summary = build_support_view(bridge_summary, paths=paths, root=root)
    support_summary.update({
        'reduction_state': reduction.get('reduction_state', {}),
        'memory_residue': reduction.get('memory_residue', {}),
    })
    support_tab = PanelTabState(
        title='Support',
        summary=support_summary,
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
            'satellite_authority': sapiens_authority,
        },
        manifest=manifest,
    )


def run_sapiens_panel(root: str | Path, user_text: str = 'Hello, model.', sapiens_id: str = 'sapiens') -> dict[str, Any]:
    state = build_panel_state(root, user_text=user_text, sapiens_id=sapiens_id)
    return {
        'schema': 'ciel-sot-agent/sapiens-panel-run/v0.2',
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
            'satellite_authority': state.state_sources.get('satellite_authority', {}),
        },
    }
