from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class PerceptiveLayer:
    clip_percentile: Optional[float] = 99.5

    def compute(self, psi_field: np.ndarray, sigma_field: np.ndarray) -> np.ndarray:
        psi = psi_field.astype(np.complex128, copy=False)
        sig = sigma_field.astype(np.float64, copy=False)
        percept = sig * (psi.real + np.abs(psi.imag))
        if self.clip_percentile is not None:
            hi = float(np.percentile(percept, self.clip_percentile))
            percept = np.clip(percept, 0.0, hi) / (hi + 1e-12)
        else:
            percept = percept / (float(np.max(percept)) + 1e-12)
        return percept


@dataclass
class IntuitiveCortex:
    entropy_map: np.ndarray
    predictivity: float = 0.7
    memory_buffer: List[np.ndarray] = field(default_factory=list)
    max_memory: int = 64

    def _weights(self) -> np.ndarray:
        w = np.exp(-np.asarray(self.entropy_map, dtype=float).ravel())
        return w / (float(np.sum(w)) + 1e-12)

    def ingest(self, obs: np.ndarray) -> None:
        v = np.asarray(obs, dtype=float).ravel()
        self.memory_buffer.append(v)
        if len(self.memory_buffer) > int(self.max_memory):
            self.memory_buffer.pop(0)

    def intuition(self, inputs: np.ndarray) -> float:
        x = np.asarray(inputs, dtype=float).ravel()
        w = self._weights()
        raw = float(np.dot(w, x))
        if self.memory_buffer:
            m = np.mean(np.stack(self.memory_buffer, axis=0), axis=0)
            raw = (1.0 - float(self.predictivity)) * raw + float(self.predictivity) * float(np.dot(w, m))
        return float(np.tanh(raw))

    def update_entropy(self, percept: np.ndarray, k: float = 0.1) -> None:
        p = np.asarray(percept, dtype=float).ravel()
        p = p / (float(np.max(p)) + 1e-12)
        self.entropy_map = np.clip(self.entropy_map - k * p + 0.5 * k * (1.0 - p), 0.0, 5.0)


@dataclass
class PredictiveCore:
    tau: float = 12.0

    def predict(self, history: List[float]) -> float:
        if not history:
            return 0.0
        h = np.asarray(history, dtype=float)
        t = np.arange(len(h))[::-1]
        w = np.exp(-t / max(float(self.tau), 1e-6))
        return float(np.sum(w * h) / (float(np.sum(w)) + 1e-12))


@dataclass
class DecisionCore:
    min_score: float = 0.15

    def decide(self, options: Dict[str, Dict[str, float]]) -> Tuple[Optional[str], Dict[str, float]]:
        scores: Dict[str, float] = {}
        best_key: Optional[str] = None
        best_val = float('-inf')
        for k, v in options.items():
            s = float(v.get('intent', 0.0) * v.get('ethic', 0.0) * v.get('confidence', 0.0))
            scores[k] = s
            if s > best_val:
                best_key, best_val = k, s
        if best_val < float(self.min_score):
            return None, scores
        return best_key, scores


@dataclass
class CognitionOrchestrator:
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
        *,
        steps: int,
        psi_supplier: Callable[[int], np.ndarray],
        sigma_supplier: Callable[[int], np.ndarray],
        options_supplier: Callable[[int, float, float], Dict[str, Dict[str, float]]],
    ) -> List[Dict[str, Any]]:
        self._intuition_hist.clear()
        self._log.clear()

        for t in range(int(steps)):
            ctx: Dict[str, Any] = {'t': t}

            if self.pre_step:
                self.pre_step(t, ctx)

            psi = psi_supplier(t)
            sigma = sigma_supplier(t)
            percept = self.percept.compute(psi, sigma)
            ctx['percept_mean'] = float(np.mean(percept))

            self.cortex.ingest(percept)
            intuition = self.cortex.intuition(percept)
            self.cortex.update_entropy(percept, k=0.05)
            self._intuition_hist.append(float(intuition))
            ctx['intuition'] = float(intuition)

            pred = self.predictor.predict(self._intuition_hist)
            ctx['prediction'] = float(pred)

            options = options_supplier(t, float(intuition), float(pred))
            choice, scores = self.decider.decide(options)
            ctx['decision'] = choice
            ctx['scores'] = scores

            if self.post_step:
                self.post_step(t, ctx)

            self._log.append(ctx)

        return list(self._log)


def run_demo(*, steps: int = 12, n: int = 64) -> List[Dict[str, Any]]:
    x = np.linspace(-2.0, 2.0, n)
    X, Y = np.meshgrid(x, x)
    psi0 = np.exp(-(X**2 + Y**2)) * np.exp(1j * (X + 0.3 * Y))
    sigma0 = np.exp(-(X**2 + Y**2) / 2.0)

    def psi_supplier(t: int) -> np.ndarray:
        return psi0 * np.exp(1j * 0.05 * t)

    def sigma_supplier(t: int) -> np.ndarray:
        return np.clip(sigma0 * (0.95 + 0.05 * np.cos(0.1 * t)), 0.0, 1.0)

    def options_supplier(t: int, intuition: float, prediction: float) -> Dict[str, Dict[str, float]]:
        base_ethic = 0.9
        return {
            'help': {
                'intent': max(0.0, intuition),
                'ethic': base_ethic,
                'confidence': 0.7 + 0.2 * prediction,
            },
            'wait': {
                'intent': 0.4 + 0.3 * (1.0 - abs(intuition)),
                'ethic': 0.8,
                'confidence': 0.6,
            },
            'risky': {
                'intent': 0.6 * prediction,
                'ethic': 0.4 + 0.2 * (t % 2),
                'confidence': 0.5,
            },
        }

    percept = PerceptiveLayer()
    cortex = IntuitiveCortex(entropy_map=np.ones(n * n))
    pred = PredictiveCore(tau=10.0)
    decide = DecisionCore(min_score=0.2)
    cog = CognitionOrchestrator(percept, cortex, pred, decide)

    return cog.run_cycle(
        steps=int(steps),
        psi_supplier=psi_supplier,
        sigma_supplier=sigma_supplier,
        options_supplier=options_supplier,
    )
