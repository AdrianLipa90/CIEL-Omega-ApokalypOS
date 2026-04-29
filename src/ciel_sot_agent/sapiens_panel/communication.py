from __future__ import annotations

from pathlib import Path
from typing import Any

from ..sapiens_client import SapiensSession, build_model_packet
from ..satellite_authority import require_interaction_surface, project_authority_summary


def build_communication_view(session: SapiensSession, user_text: str, *, root: str | Path | None = None) -> dict[str, Any]:
    root = Path(root) if root is not None else Path(__file__).resolve().parents[3]
    authority = project_authority_summary(require_interaction_surface(root, 'SAT-SAPIENS-0001'))
    packet = build_model_packet(session, user_text)
    return {
        'latest_user_turn': user_text,
        'packet': packet,
        'memory_excerpt': packet.get('memory_excerpt', []),
        'turn_count': packet.get('session', {}).get('turn_count', 0),
        'satellite_authority': authority,
    }
