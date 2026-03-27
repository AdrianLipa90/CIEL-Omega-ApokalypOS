"""CIEL/Ω — High-level orchestration facade.

CielEngine composes wave simulation, cognition, affective processing,
memory coordination, and LLM backends into a single callable engine.

Adapted from CIEL_FIXED/ciel/engine.py with cross-references to ciel_omega modules.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from ciel_omega.config.ciel_config import CielConfig
from ciel_omega.fields.intention_field import IntentionField
from ciel_omega.fields.soul_invariant import SoulInvariant
from ciel_omega.ciel_wave.fourier_kernel import SpectralWaveField12D
from .language_backend import AuxiliaryBackend, LanguageBackend
from ciel_omega.emotion.emotion_core import EmotionCore
from ciel_omega.emotion.cqcl.emotional_collatz import EmotionalCollatzEngine
from ciel_omega.ethics.ethics_guard import EthicsGuard
from ciel_omega.ethics.ethical_engine import EthicalEngine
from ciel_omega.memory.monolith.orchestrator import UnifiedMemoryOrchestrator
from ciel_omega.memory import HolonomicMemoryOrchestrator
from .orbital_memory_persistence import PersistentOrbitalSectorMemory
from .orbital_memory_governor import build_memory_governor
from .orbital_memory_retrieval import govern_sector_retrieval
from ciel_omega.calibration.rcde import RCDECalibratorPro
from .orbital_memory_loop import (
    OrbitalLoopConfig,
    RuntimeOrbitalSignals,
    build_memory_meta,
    build_runtime_policy,
    build_wave_attrs,
    run_orbital_loop,
)
from .orbital_sector_memory import derive_orbital_memory_phase, record_orbital_sector_memory

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
    sector_memory: PersistentOrbitalSectorMemory = field(default_factory=PersistentOrbitalSectorMemory)
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

        # 7) Orbital diagnostics -> runtime policy
        simulation_coherence = float(np.mean(simulation.get("coherence", [0.5])))
        orbital = run_orbital_loop(
            OrbitalLoopConfig(
                steps=2,
                context_prefix=context,
                write_reports=True,
                pass_label=context.replace("/", "_").replace("|", "_") or "runtime",
                runtime_signals=RuntimeOrbitalSignals(
                    text_length=len(cleaned),
                    context=context,
                    mood=float(mood),
                    ethical_score=float(ethical_score),
                    soul_invariant=float(sigma),
                    simulation_coherence=simulation_coherence,
                    intention_norm=float(np.linalg.norm(intention_vector)),
                ),
            )
        )
        runtime_policy = build_runtime_policy(orbital)

        # 8) Memory capture with orbital/control feedback
        memory_meta = build_memory_meta(
            text=cleaned,
            context=context,
            mood=mood,
            ethical_score=ethical_score,
            soul_invariant=sigma,
            orbital=orbital,
            runtime_policy=runtime_policy,
        )
        associations = [
            {"kind": "orbital_control", "value": orbital.control.get("mode", "safe")},
            {"kind": "dominant_emotion", "value": dominant_emotion},
            {"kind": "runtime_policy", "value": runtime_policy["response_strategy"]},
        ]
        D = self.memory.capture(
            context=f"{context}|{orbital.control.get('mode', 'safe')}",
            sense=cleaned,
            associations=associations,
            meta=memory_meta,
        )
        tmp_out = self.memory.run_tmp(D)
        wave_attrs = build_wave_attrs(
            text=cleaned,
            context=context,
            orbital=orbital,
            ethical_score=ethical_score,
            soul_invariant=sigma,
        )
        memorised = self.memory.promote_if_bifurcated(
            D,
            tmp_out,
            wave_attrs=wave_attrs,
            runtime_policy=runtime_policy,
        )
        pending_event_phase = derive_orbital_memory_phase(orbital)
        pre_sector_snapshot = self.sector_memory.snapshot()
        if hasattr(pre_sector_snapshot, "__dataclass_fields__"):
            pre_sector_snapshot = asdict(pre_sector_snapshot)
        elif not isinstance(pre_sector_snapshot, dict):
            pre_sector_snapshot = {}
        applied_memory_governor = build_memory_governor(
            orbital=orbital.to_dict(),
            runtime_policy=runtime_policy,
            sector_snapshot=pre_sector_snapshot,
            sector_memory=self.sector_memory,
            event_phase=pending_event_phase,
        )
        sector_memory = record_orbital_sector_memory(
            sector_memory=self.sector_memory,
            text=cleaned,
            context=context,
            mood=mood,
            ethical_score=ethical_score,
            soul_invariant=sigma,
            orbital=orbital,
            runtime_policy=runtime_policy,
            monolith_memory=memorised,
            memory_governor=applied_memory_governor,
        )
        memory_governor = build_memory_governor(
            orbital=orbital.to_dict(),
            runtime_policy=runtime_policy,
            sector_snapshot=sector_memory.get("snapshot") if isinstance(sector_memory, dict) else None,
            sector_memory=self.sector_memory,
            event_phase=pending_event_phase,
        )
        governed_retrieval = govern_sector_retrieval(
            sector_memory=self.sector_memory,
            query=cleaned,
            governor=memory_governor,
            orbital=orbital.to_dict(),
        )
        if isinstance(sector_memory, dict):
            sector_memory["governed_retrieval"] = governed_retrieval
            sector_memory["applied_memory_governor"] = applied_memory_governor
            sector_memory["memory_governor"] = memory_governor

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
            "orbital": orbital.to_dict(),
            "runtime_policy": runtime_policy,
            "memory_meta": memory_meta,
            "tmp_outcome": tmp_out,
            "memorised": memorised,
            "sector_memory": sector_memory,
            "memory_governor": memory_governor,
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
