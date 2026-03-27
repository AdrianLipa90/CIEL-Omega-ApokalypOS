"""CIEL/Ω — High-level orchestration facade.

CielEngine composes wave simulation, cognition, affective processing,
memory coordination, and LLM backends into a single callable engine.

Adapted from CIEL_FIXED/ciel/engine.py with cross-references to ciel_omega modules.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from config.ciel_config import CielConfig
from fields.intention_field import IntentionField
from fields.soul_invariant import SoulInvariant
from ciel_wave.fourier_kernel import SpectralWaveField12D
from ciel.language_backend import AuxiliaryBackend, LanguageBackend
from emotion.emotion_core import EmotionCore
from emotion.cqcl.emotional_collatz import EmotionalCollatzEngine
from ethics.ethics_guard import EthicsGuard
from ethics.ethical_engine import EthicalEngine
from memory.monolith.orchestrator import UnifiedMemoryOrchestrator
from calibration.rcde import RCDECalibratorPro

log = logging.getLogger("CIEL.Engine")


@dataclass
class CielEngine:
    """Compose the primary orchestrators into a single callable engine.

    Cross-references:
      config/          → CielConfig
      fields/          → IntentionField, SoulInvariant
      ciel_wave/       → SpectralWaveField12D
      emotion/         → EmotionCore, EmotionalCollatzEngine
      ethics/          → EthicsGuard, EthicalEngine
      memory/monolith/ → UnifiedMemoryOrchestrator
      calibration/     → RCDECalibratorPro
      ciel/            → LanguageBackend, AuxiliaryBackend (LLM)
    """

    config: CielConfig = field(default_factory=CielConfig)
    intention: IntentionField = field(default_factory=IntentionField)
    kernel: SpectralWaveField12D = field(default_factory=SpectralWaveField12D)
    memory: UnifiedMemoryOrchestrator = field(default_factory=UnifiedMemoryOrchestrator)
    emotion: EmotionCore = field(default_factory=EmotionCore)
    cqcl: EmotionalCollatzEngine = field(default_factory=EmotionalCollatzEngine)
    ethics_guard: EthicsGuard = field(default_factory=lambda: EthicsGuard(block=False))
    ethics_engine: EthicalEngine = field(default_factory=EthicalEngine)
    soul: SoulInvariant = field(default_factory=SoulInvariant)
    rcde: RCDECalibratorPro = field(default_factory=RCDECalibratorPro)
    language_backend: Optional[LanguageBackend] = None
    aux_backend: Optional[AuxiliaryBackend] = None

    def boot(self) -> None:
        log.info("Booting CIEL Engine")

    def shutdown(self) -> None:
        log.info("Shutting down CIEL Engine")

    def step(self, text: str, *, context: str = "dialogue") -> Dict[str, Any]:
        """Run a single processing step: intention → fields → CQCL → ethics → memory."""

        cleaned = (text or "").strip()
        if not cleaned:
            return {"status": "empty"}

        # 1) Intention vector (12D)
        intention_vector = self.intention.generate().tolist()

        # 2) Wave kernel simulation
        simulation = self.kernel.run()

        # 3) CQCL emotional compilation
        cqcl_out = self.cqcl.execute_emotional_program(cleaned, input_data=42)
        emotional_profile = cqcl_out["program"].semantic_tree["emotional_profile"]
        dominant_emotion = cqcl_out["emotional_landscape"]["dominant_emotion"]

        # 4) Emotion core update
        emotion_state = self.emotion.update(emotional_profile)
        mood = self.emotion.summary_scalar()

        # 5) Soul Invariant (on intention as 2D proxy)
        side = int(np.ceil(np.sqrt(len(intention_vector))))
        padded = np.pad(intention_vector, (0, side * side - len(intention_vector)))
        sigma = self.soul.compute(padded.reshape(side, side))

        # 6) Ethics check
        ethical_score = self.ethics_engine.evaluate(
            coherence=float(np.mean(simulation.get("coherence", [0.5]))),
            intention=cqcl_out["metrics"].get("emotional_intensity", 0.5),
            mass=0.5,
        )
        self.ethics_guard.check_step(
            coherence=float(np.mean(simulation.get("coherence", [0.5]))),
            ethical_ok=ethical_score > 0.3,
            info_fidelity=sigma,
        )

        # 7) Memory capture
        D = self.memory.capture(context=context, sense=cleaned)
        tmp_out = self.memory.run_tmp(D)
        memorised = self.memory.promote_if_bifurcated(D, tmp_out)

        return {
            "status": "ok",
            "intention_vector": intention_vector,
            "simulation": simulation,
            "emotional_profile": emotional_profile,
            "dominant_emotion": dominant_emotion,
            "emotion_state": emotion_state,
            "mood": mood,
            "soul_invariant": sigma,
            "ethical_score": ethical_score,
            "tmp_outcome": tmp_out,
            "memorised": memorised,
            "cqcl_metrics": cqcl_out["metrics"],
            "collatz_path_length": len(cqcl_out["program"].computation_path),
        }

    def interact(
        self,
        user_text: str,
        dialogue: List[Dict[str, str]],
        context: str = "dialogue",
        use_aux_analysis: bool = True,
    ) -> Dict[str, Any]:
        """Run core step + optional LLM generation and analysis."""

        ciel_state = self.step(user_text, context=context)
        if self.language_backend is None:
            return {"status": "no_language_backend", "ciel_state": ciel_state}

        reply = self.language_backend.generate_reply(dialogue, ciel_state)
        result: Dict[str, Any] = {"status": "ok", "ciel_state": ciel_state, "reply": reply}

        if use_aux_analysis and self.aux_backend is not None:
            analysis = self.aux_backend.analyse_state(ciel_state, reply)
            result["analysis"] = analysis

        return result


__all__ = ["CielEngine"]
