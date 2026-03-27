from __future__ import annotations

from typing import Any

from ..sapiens_client import SapiensSession, build_model_packet


def build_communication_view(session: SapiensSession, user_text: str) -> dict[str, Any]:
    packet = build_model_packet(session, user_text)
    return {
        'latest_user_turn': user_text,
        'packet': packet,
        'memory_excerpt': packet.get('memory_excerpt', []),
        'turn_count': packet.get('session', {}).get('turn_count', 0),
    }
