"""CIEL/Ω Memory Architecture - M0 Perceptual Memory Types

Data structures for perceptual ingress memory. M0 is a fast, short-lived,
pre-semantic buffer for raw percepts. It provides salience-ranked retrieval
without directly modifying identity or higher-order memories.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PerceptualTrace:
    timestamp: float
    source_id: str
    percept_key: str
    modality: str
    raw_content: str
    normalized_content: str
    phase: float
    phase_diff: float
    identity_alignment: float
    salience: float
    confidence: float
    novelty_score: float


@dataclass
class PerceptualItem:
    percept_key: str
    modality: str
    canonical_text: str
    aliases: List[str] = field(default_factory=list)
    activation: float = 0.0
    salience: float = 0.0
    confidence: float = 0.0
    identity_alignment: float = 0.0
    phase: float = 0.0
    exposure_count: int = 0
    first_observed_at: float = 0.0
    last_observed_at: float = 0.0
    status: str = "active"  # active, decayed, evicted

    def is_active(self, min_activation: float) -> bool:
        return self.activation >= min_activation and self.status == "active"


@dataclass
class PerceptualSnapshot:
    timestamp: float
    active_keys: List[str]
    total_items: int
    dominant_key: str | None
    dominant_activation: float
    mean_salience: float


__all__ = [
    'PerceptualTrace',
    'PerceptualItem',
    'PerceptualSnapshot',
]
