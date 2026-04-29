"""Types for HolonomicMemoryOrchestrator.

Conservative runtime glue for the implemented CIEL/Ω memory channels.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ConsolidationEvents:
    semantic_candidate: Optional[str] = None
    semantic_item: Optional[str] = None
    procedural_candidate: Optional[str] = None
    procedural_item: Optional[str] = None
    affective_candidate: Optional[str] = None
    affective_item: Optional[str] = None
    identity_candidate: Optional[str] = None
    braid_recorded: bool = False


@dataclass
class EBAEvaluation:
    loop_type: str
    epsilon_eba: float
    defect_magnitude: float
    is_coherent: bool
    phi_dyn: float
    phi_berry: float
    phi_ab: float
    nu_e: int


@dataclass
class OrchestratorCycleResult:
    cycle_index: int
    timestamp: float
    content: str
    perceptual_key: str
    working_key: str
    episode_timestamp: float
    semantic_key: Optional[str]
    procedural_key: Optional[str]
    affective_key: Optional[str]
    consolidations: ConsolidationEvents
    eba_results: Dict[str, EBAEvaluation]
    energy: Dict[str, float]
    defects: Dict[str, float]
    notes: List[str] = field(default_factory=list)


@dataclass
class OrchestratorSnapshot:
    timestamp: float
    cycle_index: int
    identity_phase: float
    energy: Dict[str, float]
    defects: Dict[str, float]
    counts: Dict[str, int]
    latest_loop_status: Dict[str, bool]
