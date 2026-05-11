from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SafetyLevel(str, Enum):
    CLEAR = "clear"
    WATCH = "watch"
    BOUNDARY = "boundary"
    LITERAL_ALARM = "literal_alarm"


class HumorDose(int, Enum):
    NONE = 0
    MIST = 1
    DRY = 2
    SOFT_CARICATURE = 3
    STANDUP_REFRAME = 4
    CONTROLLED_GROTESQUE = 5


@dataclass(frozen=True)
class TensionInput:
    text: str
    context: Dict[str, Any] = field(default_factory=dict)
    user_mode: Optional[str] = None
    pain_level: Optional[float] = None
    source: str = "chat"


@dataclass(frozen=True)
class BoundaryVerdict:
    level: SafetyLevel
    literal: bool
    reasons: List[str]
    humor_allowed: bool
    max_dose: HumorDose


@dataclass(frozen=True)
class TensionProfile:
    symbolic_density: float
    cognitive_tension: float
    grotesque_caricature: bool
    mnemonic_likely: bool
    pain_overflow: bool
    tags: List[str]


@dataclass(frozen=True)
class JokeHealOutput:
    mode: str
    humor_dose: HumorDose
    symbolic_object: str
    reframe: str
    closure_score: float
    residual_tension: float
    boundary: BoundaryVerdict
    tension: TensionProfile
    noema_card: str
    scar_record: Dict[str, Any]
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["humor_dose"] = int(self.humor_dose)
        data["boundary"]["level"] = self.boundary.level.value
        data["boundary"]["max_dose"] = int(self.boundary.max_dose)
        return data
