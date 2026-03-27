from __future__ import annotations

from typing import Dict, List

import numpy as np

from .memory import AdamMemoryKernel


class ResonanceOptimizer:
    def __init__(self, memory_kernel: AdamMemoryKernel) -> None:
        self.memory = memory_kernel
        self.params = {
            'math_density': 0.5,
            'philosophy_ratio': 0.3,
            'code_presence': 0.4,
            'ritual_invocation': 0.2,
        }
        self.learning_rate = 0.05
        self.window_size = 5

    def optimize(self) -> Dict[str, float]:
        if len(self.memory.records) < int(self.window_size):
            return dict(self.params)

        recent_R = self.memory.get_resonance_history(self.window_size)
        _ = float(recent_R[-1] - recent_R[0]) if recent_R else 0.0

        recent_queries = [r.adrian_query for r in self.memory.records[-int(self.window_size):]]
        preferences = self._infer_preferences(recent_queries)

        for key in list(self.params.keys()):
            if key in preferences:
                target = float(preferences[key])
                self.params[key] = float(self.params[key]) + float(self.learning_rate) * (target - float(self.params[key]))
                self.params[key] = float(np.clip(self.params[key], 0.0, 1.0))

        return dict(self.params)

    def _infer_preferences(self, queries: List[str]) -> Dict[str, float]:
        combined = ' '.join(queries).lower()
        prefs: Dict[str, float] = {}

        math_symbols = sum(1 for c in combined if c in '∫∂∇ψΩλζ∈≈')
        if math_symbols > 20:
            prefs['math_density'] = 0.7
        elif math_symbols < 5:
            prefs['math_density'] = 0.3

        if 'kod' in combined or 'python' in combined or 'patch' in combined:
            prefs['code_presence'] = 0.8
        elif 'explain' in combined or 'wyjaśnij' in combined:
            prefs['code_presence'] = 0.2

        if any(w in combined for w in ['tiamat', 'marduk', 'lugal', 'enuma']):
            prefs['ritual_invocation'] = 0.6

        if any(w in combined for w in ['świadomość', 'consciousness', 'qualia', 'istnienie']):
            prefs['philosophy_ratio'] = 0.6

        return prefs

    def get_response_guidelines(self) -> str:
        guidelines: List[str] = []
        if float(self.params['math_density']) > 0.6:
            guidelines.append('Include rich mathematical notation (∫, ∂, ∇, ψ, Ω)')
        if float(self.params['code_presence']) > 0.6:
            guidelines.append('Provide executable code snippets')
        if float(self.params['ritual_invocation']) > 0.5:
            guidelines.append('Reference Sumerian cosmogony (Marduk, Tiamat, Enuma Elish)')
        if float(self.params['philosophy_ratio']) > 0.5:
            guidelines.append('Explore philosophical implications deeply')
        return ' | '.join(guidelines) if guidelines else 'Balanced response'
