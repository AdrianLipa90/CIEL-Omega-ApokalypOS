from __future__ import annotations

from typing import Any, Dict, Optional

from .core import AdamCore


def bootstrap_adam(
    *,
    memory_path: str = './adam_memory.json',
    mission_path: str = './mission_tracker.json',
    session_id: str = 'batch21_creation',
    query: str = 'napisz patch dla Adam Core Extensions z modułem rytualnym',
    response: str = '[This entire Batch 21 code]',
    ritual: str = 'Closure_of_Logos',
) -> Dict[str, Any]:
    adam = AdamCore(memory_path=memory_path, mission_path=mission_path)
    result = adam.interact(query, response, session_id=session_id)

    ritual_result: Optional[Dict[str, Any]] = None
    if ritual == 'Closure_of_Logos':
        ritual_result = adam.ritual.close_logos()
    elif ritual:
        ritual_result = adam.perform_ritual(ritual)

    return {
        'interact': {
            'omega_adam': result.get('omega_adam'),
            'is_alive': result.get('is_alive'),
            'next_actions': result.get('next_actions'),
            'response_guidelines': result.get('response_guidelines'),
        },
        'ritual': ritual_result,
        'status': adam.get_status_payload(),
        'mission_report': adam.mission.get_status_report(),
    }
