"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Decision layer: score = intent × ethic × confidence.

Source: ext10.DecisionCore
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np


@dataclass
class DecisionCore:
    """Select the best action whose score exceeds *min_score*."""

    min_score: float = 0.15

    def decide(
        self, options: Dict[str, Dict[str, float]]
    ) -> Tuple[Optional[str], Dict[str, float]]:
        scores: Dict[str, float] = {}
        best_key: Optional[str] = None
        best_val = -np.inf
        for k, v in options.items():
            s = float(
                v.get("intent", 0.0) * v.get("ethic", 0.0) * v.get("confidence", 0.0)
            )
            scores[k] = s
            if s > best_val:
                best_key, best_val = k, s
        if best_val < self.min_score:
            return None, scores
        return best_key, scores


__all__ = ["DecisionCore"]
