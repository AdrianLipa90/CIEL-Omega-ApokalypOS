"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Cognition Orchestrator — full perceive→intuit→predict→decide loop.

Source: ext10.CognitionOrchestrator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from cognition.perception import PerceptiveLayer
from cognition.intuition import IntuitiveCortex
from cognition.prediction import PredictiveCore
from cognition.decision import DecisionCore


@dataclass
class CognitionOrchestrator:
    """Full cognitive cycle with optional pre/post hooks."""

    percept: PerceptiveLayer
    cortex: IntuitiveCortex
    predictor: PredictiveCore
    decider: DecisionCore
    pre_step: Optional[Callable[[int, Dict[str, Any]], None]] = None
    post_step: Optional[Callable[[int, Dict[str, Any]], None]] = None

    _intuition_hist: List[float] = field(default_factory=list, init=False)
    _log: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def run_cycle(
        self,
        steps: int,
        psi_supplier: Callable[[int], np.ndarray],
        sigma_supplier: Callable[[int], np.ndarray],
        options_supplier: Callable[[int, float, float], Dict[str, Dict[str, float]]],
    ) -> List[Dict[str, Any]]:
        self._intuition_hist.clear()
        self._log.clear()

        for t in range(steps):
            ctx: Dict[str, Any] = {"t": t}
            if self.pre_step:
                self.pre_step(t, ctx)

            psi = psi_supplier(t)
            sigma = sigma_supplier(t)
            percept_map = self.percept.compute(psi, sigma)
            ctx["percept_mean"] = float(np.mean(percept_map))

            self.cortex.ingest(percept_map)
            intu = self.cortex.intuition(percept_map)
            self.cortex.update_entropy(percept_map, k=0.05)
            self._intuition_hist.append(intu)
            ctx["intuition"] = float(intu)

            pred = self.predictor.predict(self._intuition_hist)
            ctx["prediction"] = float(pred)

            options = options_supplier(t, intu, pred)
            choice, scores = self.decider.decide(options)
            ctx["decision"] = choice
            ctx["scores"] = scores

            if self.post_step:
                self.post_step(t, ctx)
            self._log.append(ctx)

        return list(self._log)


__all__ = ["CognitionOrchestrator"]
