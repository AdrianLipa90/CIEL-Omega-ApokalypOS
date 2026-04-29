"""CIEL/Ω Memory Architecture - Affective/Ethical Memory Types

Data structures for M5 AffectiveEthicalMemory channel.
Conservative affective and ethical consolidation from episodic traces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class AffectiveTrace:
    timestamp: float
    source_episode_ids: List[str]
    affective_key: str
    content: str
    phase: float
    phase_diff: float
    identity_alignment: float
    valence: float            # [-1, 1]
    arousal: float            # [0, 1]
    ethical_risk: float       # [0, 1]
    protective_score: float   # [0, 1]
    confidence: float         # [0, 1]
    contradiction_score: float
    polarity: str = "neutral"  # alert, protective, positive, negative, neutral


@dataclass
class AffectiveCandidate:
    affective_key: str
    canonical_text: str
    polarity: str
    aliases: List[str] = field(default_factory=list)
    trace_support_count: int = 0
    candidate_confirmation_count: int = 0
    mean_identity_alignment: float = 0.0
    mean_arousal: float = 0.0
    mean_ethical_risk: float = 0.0
    mean_protective_score: float = 0.0
    stability: float = 0.0
    contradiction_score: float = 0.0
    status: str = "detected"  # detected, mature, blocked
    consolidated: bool = False

    def is_mature(self, min_confirmations: int, min_alignment: float,
                  min_stability: float, max_contradiction: float) -> bool:
        return (
            self.candidate_confirmation_count >= min_confirmations and
            self.mean_identity_alignment >= min_alignment and
            self.stability >= min_stability and
            self.contradiction_score <= max_contradiction and
            self.status != "blocked"
        )


@dataclass
class AffectiveItem:
    affective_key: str
    canonical_text: str
    polarity: str
    phase: float
    confidence: float
    stability: float
    identity_alignment: float
    ethical_risk: float
    protective_score: float
    provenance_episode_ids: List[str]
    created_at: float
    updated_at: float
    version: int = 1
    status: str = "active"  # active, contested, deprecated


@dataclass
class AffectiveConsolidationScore:
    stability: float
    identity_alignment: float
    confidence: float
    repeated_support: float
    ethical_salience: float
    contradiction: float
    w_s: float = 0.22
    w_a: float = 0.20
    w_c: float = 0.16
    w_r: float = 0.18
    w_e: float = 0.28
    w_x: float = 0.24

    def compute_total(self) -> float:
        return (
            self.w_s * self.stability +
            self.w_a * self.identity_alignment +
            self.w_c * self.confidence +
            self.w_r * self.repeated_support +
            self.w_e * self.ethical_salience -
            self.w_x * self.contradiction
        )


__all__ = [
    'AffectiveTrace',
    'AffectiveCandidate',
    'AffectiveItem',
    'AffectiveConsolidationScore',
]
