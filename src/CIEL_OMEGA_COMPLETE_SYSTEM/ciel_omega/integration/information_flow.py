"""CIEL/Ω — High-level information flow pipeline.

Stitches bio, emotion, field and memory into a reproducible pipeline.
Single step() method: sensor signal → filter → intention → emotion → memory.

Cross-references:
  bio/           → EEGProcessor, CrystalFieldReceiver
  emotion/       → EmotionCore, EEGEmotionMapper
  fields/        → IntentionField, SoulInvariant
  memory/        → LongTermMemory
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable

import numpy as np

from bio.eeg_processor import EEGProcessor
from bio.eeg_emotion_mapper import EEGEmotionMapper
from emotion.emotion_core import EmotionCore
from fields.intention_field import IntentionField
from fields.soul_invariant import SoulInvariant
from memory.long_term import LongTermMemory
from inference.middleware import build_inference_seed


@dataclass
class InformationFlow:
    """Compose bio → emotion → field → memory into a single pipeline.

    This layer carries and prepares state. Final inference execution belongs to
    the orbital-ethical inference surface, not to InformationFlow itself.
    """

    intention: IntentionField = field(default_factory=IntentionField)
    eeg: EEGProcessor = field(default_factory=EEGProcessor)
    mapper: EEGEmotionMapper = field(default_factory=EEGEmotionMapper)
    emotion: EmotionCore = field(default_factory=EmotionCore)
    memory: LongTermMemory = field(default_factory=LongTermMemory)
    soul: SoulInvariant = field(default_factory=SoulInvariant)

    def step(self, signal: Iterable[float], *, target_phase: float | None = None) -> Dict[str, Any]:
        sig = np.fromiter(signal, dtype=float)

        bands = self.eeg.band_powers(sig)
        intention_vector = self.intention.generate()
        affect = self.mapper.map(bands)
        emotion_state = self.emotion.update(affect)
        mood = self.emotion.summary_scalar()

        side = max(2, int(np.ceil(np.sqrt(sig.size))))
        padded = np.pad(sig, (0, side * side - sig.size))
        sigma = self.soul.compute(padded.reshape(side, side))

        entry = {
            "bands": bands,
            "intention": intention_vector.tolist(),
            "affect": affect,
            "emotion_state": emotion_state,
            "mood": mood,
            "soul_invariant": sigma,
        }
        entry["inference_seed"] = build_inference_seed(entry, target_phase=target_phase)

        self.memory.put(
            label="info_flow",
            psi=(padded.reshape(side, side) + 0j),
            sigma=sigma,
            meta={"mood": mood, "dominant": max(affect, key=affect.get)},
        )

        return entry


__all__ = ["InformationFlow"]
