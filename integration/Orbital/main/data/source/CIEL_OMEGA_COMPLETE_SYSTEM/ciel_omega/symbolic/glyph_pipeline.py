"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Glyph pipeline — chain of glyph nodes with Σ modulation.

Source: ext8.GlyphPipeline
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from ciel_omega.symbolic.glyph_interpreter import GlyphNode


@dataclass
class GlyphPipeline:
    """Combine glyph effects (weighted average with Σ as modulator)."""

    nodes: List[GlyphNode]
    color_weights: Optional[List[float]] = None
    sigma_field: Optional[np.ndarray] = None

    def combine(self) -> Dict[str, Any]:
        weights = (
            np.ones(len(self.nodes))
            if self.color_weights is None
            else np.array(self.color_weights)
        )
        weights = weights / (np.sum(weights) + 1e-12)
        summary = [f"{n.name} × {w:.2f}" for w, n in zip(weights, self.nodes)]
        coherence = float(np.mean(weights))
        sigma_mod = float(np.mean(self.sigma_field)) if self.sigma_field is not None else 1.0
        color_mix = min(1.0, coherence * sigma_mod)
        return {"coherence": coherence, "color_mix": color_mix, "summary": " | ".join(summary)}


__all__ = ["GlyphPipeline"]
