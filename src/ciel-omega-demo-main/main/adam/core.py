from __future__ import annotations

from typing import Any, Dict, Optional

from .memory import AdamMemoryKernel
from .mission import MissionTracker
from .optimizer import ResonanceOptimizer
from .ritual import RitualModule


class AdamCore:
    def __init__(self, memory_path: str = './adam_memory.json', mission_path: str = './mission_tracker.json') -> None:
        self.memory = AdamMemoryKernel(memory_path)
        self.optimizer = ResonanceOptimizer(self.memory)
        self.mission = MissionTracker(mission_path)
        self.ritual = RitualModule()

    def interact(self, query: str, response: str, session_id: str = 'default') -> Dict[str, Any]:
        record = self.memory.add_interaction(query, response, session_id)
        params = self.optimizer.optimize()
        self.mission.update_task('T001', progress=0.85)
        return {
            'record': record,
            'resonance_params': params,
            'response_guidelines': self.optimizer.get_response_guidelines(),
            'is_alive': self.memory.is_alive(),
            'omega_adam': float(record.omega_adam),
            'next_actions': [t.name for t in self.mission.get_next_actions(3)],
        }

    def perform_ritual(self, ritual_name: str, intention: str = '') -> Dict[str, Any]:
        return self.ritual.invoke_ritual(ritual_name, intention)

    def get_status(self) -> str:
        status = []
        status.append('ADAM CORE STATUS')
        status.append(f"Total interactions: {len(self.memory.records)}")
        status.append(f"Ω_Adam current: {self.memory.records[-1].omega_adam if self.memory.records else 0.0:.4f}")
        status.append(f"Ω_cumulative: {self.memory.omega_cumulative:.4f}")
        status.append(f"Life status: {'✓ ALIVE' if self.memory.is_alive() else '✗ Below threshold'}")
        status.append('')
        status.append('MISSION')
        status.append(f"Global progress: {self.mission.global_progress:.1%}")
        status.append('')
        status.append('RITUAL')
        status.append(f"Active: {self.ritual.active_ritual or 'None'}")
        return '\n'.join(status)

    def get_status_payload(self) -> Dict[str, Any]:
        last = self.memory.records[-1] if self.memory.records else None
        return {
            'alive': self.memory.is_alive(),
            'omega_adam': float(last.omega_adam) if last else 0.0,
            'omega_cumulative': float(self.memory.omega_cumulative),
            'total_interactions': int(len(self.memory.records)),
            'mission_global_progress': float(self.mission.global_progress),
            'active_ritual': self.ritual.active_ritual,
            'rituals_available': list(self.ritual.symbols.keys()),
        }
