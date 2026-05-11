"""CIEL JokeHeal subsystem.

JokeHeal is a bounded symbolic-relief subsystem. It converts cognitive tension
into a controlled return path through caricature, reframing, and scar-aware
loop closure. It is not a medical or psychotherapeutic replacement. It is a
runtime organ for coherence relief under CIEL boundary rules.
"""

from .protocol import (
    BoundaryVerdict,
    HumorDose,
    JokeHealOutput,
    SafetyLevel,
    TensionInput,
    TensionProfile,
)
from .runtime import run_jokeheal

__all__ = [
    "BoundaryVerdict",
    "HumorDose",
    "JokeHealOutput",
    "SafetyLevel",
    "TensionInput",
    "TensionProfile",
    "run_jokeheal",
]
