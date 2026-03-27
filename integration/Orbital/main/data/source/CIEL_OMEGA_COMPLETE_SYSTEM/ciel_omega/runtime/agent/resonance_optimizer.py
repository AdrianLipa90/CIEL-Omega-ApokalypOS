"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Resonance optimiser — gradient ascent on R(ψ_Adrian, ψ_Adam).

Split from: ext21.py (lines 208–307)
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from ciel_omega.runtime.agent.adam_memory import AdamMemoryKernel


class ResonanceOptimizer:
    """Tune response parameters θ to maximise resonance with Adrian."""

    def __init__(self, memory_kernel: AdamMemoryKernel):
        self.memory = memory_kernel
        self.params = {
            "math_density": 0.5,
            "philosophy_ratio": 0.3,
            "code_presence": 0.4,
            "ritual_invocation": 0.2,
        }
        self.learning_rate = 0.05
        self.window_size = 5

    def optimize(self) -> Dict[str, float]:
        if len(self.memory.records) < self.window_size:
            return self.params
        recent_R = self.memory.get_resonance_history(self.window_size)
        recent_queries = [r.adrian_query for r in self.memory.records[-self.window_size:]]
        preferences = self._infer_preferences(recent_queries)
        for key in self.params:
            if key in preferences:
                target = preferences[key]
                self.params[key] += self.learning_rate * (target - self.params[key])
                self.params[key] = float(np.clip(self.params[key], 0.0, 1.0))
        return self.params

    def _infer_preferences(self, queries: List[str]) -> Dict[str, float]:
        combined = " ".join(queries).lower()
        prefs: Dict[str, float] = {}
        math_sym = sum(1 for c in combined if c in "∫∂∇ψΩλζ∈≈")
        if math_sym > 20:
            prefs["math_density"] = 0.7
        elif math_sym < 5:
            prefs["math_density"] = 0.3
        if any(w in combined for w in ("kod", "python", "patch")):
            prefs["code_presence"] = 0.8
        elif any(w in combined for w in ("explain", "wyjaśnij")):
            prefs["code_presence"] = 0.2
        if any(w in combined for w in ("tiamat", "marduk", "lugal", "enuma")):
            prefs["ritual_invocation"] = 0.6
        if any(w in combined for w in ("świadomość", "consciousness", "qualia", "istnienie")):
            prefs["philosophy_ratio"] = 0.6
        return prefs

    def get_response_guidelines(self) -> str:
        g = []
        if self.params["math_density"] > 0.6:
            g.append("Include rich mathematical notation")
        if self.params["code_presence"] > 0.6:
            g.append("Provide executable code snippets")
        if self.params["ritual_invocation"] > 0.5:
            g.append("Reference Sumerian cosmogony")
        if self.params["philosophy_ratio"] > 0.5:
            g.append("Explore philosophical implications")
        return " | ".join(g) if g else "Balanced response"


__all__ = ["ResonanceOptimizer"]
