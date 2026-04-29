"""CIEL/Ω Memory Architecture - Working Memory Types

Data structures for M1 WorkingMemory channel.
Conservative active operational field with short-term decay and reinforcement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class WorkingTrace:
    timestamp: float
    source_ids: List[str]
    working_key: str
    content: str
    phase: float
    phase_diff: float
    identity_alignment: float
    activation_delta: float
    salience: float
    confidence: float


@dataclass
class WorkingItem:
    working_key: str
    canonical_text: str
    aliases: List[str] = field(default_factory=list)
    activation: float = 0.0
    confidence: float = 0.0
    identity_alignment: float = 0.0
    phase: float = 0.0
    reinforcement_count: int = 0
    first_observed_at: float = 0.0
    last_observed_at: float = 0.0
    last_accessed_at: float = 0.0
    status: str = "active"  # active, decayed, evicted

    def is_active(self, min_activation: float) -> bool:
        return self.activation >= min_activation and self.status == "active"


@dataclass
class WorkingSnapshot:
    timestamp: float
    active_keys: List[str]
    total_items: int
    top_item_key: str | None
    top_activation: float
    mean_identity_alignment: float


__all__ = [
    'WorkingTrace',
    'WorkingItem',
    'WorkingSnapshot',
]
