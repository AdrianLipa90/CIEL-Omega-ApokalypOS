"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Affective orchestrator: EEG → EmotionCore → Σ modulation → colour.

Source: ext9.AffectiveOrchestrator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

import numpy as np

from ciel_omega.emotion.emotion_core import EmotionCore
from ciel_omega.emotion.feeling_field import FeelingField
from ciel_omega.bio.eeg_emotion_mapper import EEGEmotionMapper


@dataclass
class AffectiveOrchestrator:
    """Glue: EEG bands → emotion state → spatial affect → optional colour."""

    mapper: EEGEmotionMapper = field(default_factory=EEGEmotionMapper)
    core: EmotionCore = field(default_factory=EmotionCore)
    use_color: bool = True

    def step(
        self,
        eeg_bands: Dict[str, float],
        sigma_scalar: float = 1.0,
        psi_field: Optional[np.ndarray] = None,
        coherence_field: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        affect_vec = self.mapper.map(eeg_bands)
        mod_affect = {k: float(np.clip(v * sigma_scalar, 0.0, 1.0)) for k, v in affect_vec.items()}
        emo_state = self.core.update(mod_affect)
        mood = self.core.summary_scalar()

        field_out = None
        if psi_field is not None and coherence_field is not None:
            field_out = FeelingField().build(np.abs(psi_field), coherence_field)

        color: Optional[Tuple[float, float, float]] = None
        if self.use_color:
            try:
                from ciel_omega.visualization.color_map import ColorMap
                color = ColorMap.map_value(mood)
            except Exception:
                v = float(np.clip(mood, 0.0, 1.0))
                color = (0.2 * (1 - v) + v, 0.4 * (1 - v) + v, 0.9 * (1 - v) + 0.95 * v)

        return {
            "affect_vector": affect_vec,
            "affect_modulated": mod_affect,
            "emotion_state": emo_state,
            "mood_scalar": float(mood),
            "affect_field": field_out,
            "color": color,
        }


__all__ = ["AffectiveOrchestrator"]
