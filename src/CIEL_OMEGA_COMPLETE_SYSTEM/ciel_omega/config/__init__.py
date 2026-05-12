"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Configuration: constants, reality layers, and runtime config.
"""

from __future__ import annotations

from .constants import CIELPhysics, RealityConstants
from .reality_layers import RealityLayer, UltimateRealityLayer
from .ciel_config import CielConfig, SimConfig

__all__ = [
    "CIELPhysics",
    "RealityConstants",
    "RealityLayer",
    "UltimateRealityLayer",
    "CielConfig",
    "SimConfig",
]
