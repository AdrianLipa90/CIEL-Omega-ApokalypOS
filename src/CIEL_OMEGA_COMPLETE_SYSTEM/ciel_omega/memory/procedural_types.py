"""CIEL/Ω Memory Architecture - Procedural Memory Types

Data structures for M4 ProceduralMemory channel.
Conservative consolidation of reusable procedures from repeated successful episodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ProceduralTrace:
    timestamp: float
    source_episode_ids: List[str]
    procedure_key: str
    goal_key: str
    action_text: str
    result_success: float
    phase: float
    phase_diff: float
    identity_alignment: float
    confidence: float
    contradiction_score: float
    novelty_score: float


@dataclass
class ProceduralCandidate:
    procedure_key: str
    goal_key: str
    canonical_action: str
    aliases: List[str] = field(default_factory=list)
    trace_support_count: int = 0
    candidate_confirmation_count: int = 0
    mean_identity_alignment: float = 0.0
    mean_confidence: float = 0.0
    stability: float = 0.0
    contradiction_score: float = 0.0
    success_rate: float = 0.0
    status: str = 'detected'  # detected, mature, blocked
    consolidated: bool = False

    def is_mature(self, min_confirmations: int, min_alignment: float,
                  min_stability: float, min_success_rate: float,
                  max_contradiction: float) -> bool:
        return (
            self.candidate_confirmation_count >= min_confirmations and
            self.mean_identity_alignment >= min_alignment and
            self.stability >= min_stability and
            self.success_rate >= min_success_rate and
            self.contradiction_score <= max_contradiction and
            self.status != 'blocked'
        )


@dataclass
class ProceduralItem:
    procedure_key: str
    goal_key: str
    canonical_action: str
    aliases: List[str]
    phase: float
    confidence: float
    stability: float
    identity_alignment: float
    success_rate: float
    provenance_episode_ids: List[str]
    created_at: float
    updated_at: float
    version: int = 1
    status: str = 'active'  # active, contested, deprecated


@dataclass
class ProceduralConsolidationScore:
    stability: float
    identity_alignment: float
    confidence: float
    repeated_support: float
    success_rate: float
    contradiction: float
    w_s: float = 0.24
    w_a: float = 0.18
    w_c: float = 0.16
    w_r: float = 0.16
    w_p: float = 0.26
    w_x: float = 0.28

    def compute_total(self) -> float:
        return (
            self.w_s * self.stability +
            self.w_a * self.identity_alignment +
            self.w_c * self.confidence +
            self.w_r * self.repeated_support +
            self.w_p * self.success_rate -
            self.w_x * self.contradiction
        )


__all__ = [
    'ProceduralTrace',
    'ProceduralCandidate',
    'ProceduralItem',
    'ProceduralConsolidationScore',
]
