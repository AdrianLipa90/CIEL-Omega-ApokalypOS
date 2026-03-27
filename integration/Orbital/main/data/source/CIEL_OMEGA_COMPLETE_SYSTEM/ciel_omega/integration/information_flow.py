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

from ciel_omega.bio.eeg_processor import EEGProcessor
from ciel_omega.bio.eeg_emotion_mapper import EEGEmotionMapper
from ciel_omega.emotion.emotion_core import EmotionCore
from ciel_omega.fields.intention_field import IntentionField
from ciel_omega.fields.soul_invariant import SoulInvariant
from ciel_omega.memory.long_term import LongTermMemory


@dataclass
class InformationFlow:
    """Compose bio → emotion → field → memory into a single pipeline."""

    intention: IntentionField = field(default_factory=IntentionField)
    eeg: EEGProcessor = field(default_factory=EEGProcessor)
    mapper: EEGEmotionMapper = field(default_factory=EEGEmotionMapper)
    emotion: EmotionCore = field(default_factory=EmotionCore)
    memory: LongTermMemory = field(default_factory=LongTermMemory)
    soul: SoulInvariant = field(default_factory=SoulInvariant)

    def step(self, signal: Iterable[float]) -> Dict[str, Any]:
        """Process sensor signal through the entire pipeline."""
        sig = np.fromiter(signal, dtype=float)

        # EEG band extraction
        bands = self.eeg.band_powers(sig)

        # Intention vector
        intention_vector = self.intention.generate()

        # EEG → emotion mapping
        affect = self.mapper.map(bands)
        emotion_state = self.emotion.update(affect)
        mood = self.emotion.summary_scalar()

        # Soul invariant (reshape signal to 2D)
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

        # Persist to long-term memory
        self.memory.put(
            label="info_flow",
            psi=(padded.reshape(side, side) + 0j),
            sigma=sigma,
            meta={"mood": mood, "dominant": max(affect, key=affect.get)},
        )

        return entry


__all__ = ["InformationFlow"]
