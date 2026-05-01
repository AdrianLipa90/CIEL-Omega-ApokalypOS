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

from config.ciel_config import CielConfig
from fields.intention_field import IntentionField
from integration.information_flow import InformationFlow
from inference.middleware import build_orbital_ethical_inference_surface
from fields.soul_invariant import SoulInvariant
from ciel_wave.fourier_kernel import SpectralWaveField12D
from ciel.language_backend import AuxiliaryBackend, LanguageBackend
from emotion.emotion_core import EmotionCore
from emotion.cqcl.emotional_collatz import EmotionalCollatzEngine
from ethics.ethics_guard import EthicsGuard
from ethics.ethical_engine import EthicalEngine
from memory.monolith.orchestrator import UnifiedMemoryOrchestrator
from memory.orchestrator import HolonomicMemoryOrchestrator
from bridge.memory_core_phase_bridge import MemoryCorePhaseBridge
from calibration.rcde import RCDECalibratorPro
from phase_equation_of_motion import PhaseInfoSystem, make_zeta_wt_fn
from mathematics.lie4.collatz_lie4 import ColatzLie4Engine

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
    information_flow: InformationFlow = field(default_factory=InformationFlow)
    nonlocal_memory: HolonomicMemoryOrchestrator = field(default_factory=HolonomicMemoryOrchestrator)
    bridge: MemoryCorePhaseBridge = field(default_factory=MemoryCorePhaseBridge)
    emotion: EmotionCore = field(default_factory=EmotionCore)
    cqcl: EmotionalCollatzEngine = field(default_factory=EmotionalCollatzEngine)
    ethics_guard: EthicsGuard = field(default_factory=lambda: EthicsGuard(block=False))
    ethics_engine: EthicalEngine = field(default_factory=EthicalEngine)
    soul: SoulInvariant = field(default_factory=SoulInvariant)
    rcde: RCDECalibratorPro = field(default_factory=RCDECalibratorPro)
    phase_system_factory: Any = field(default=PhaseInfoSystem)
    lie4_collatz: ColatzLie4Engine = field(default_factory=ColatzLie4Engine)
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

        # 4b) Canonical Collatz dynamics — phase equation + Collatz↔LIE4 bridge
        collatz_seed = int(cqcl_out["metrics"].get("path_emotional_signature", 27)) % 10000 + 1
        collatz_intensity = float(np.clip(cqcl_out["metrics"].get("emotional_intensity", 0.5), 0.0, 1.0))
        phase_system = self.phase_system_factory(
            collatz_seed=collatz_seed,
            gamma_truth_target=0.0,
            sigma_zeta=0.5,
            A_collatz=0.02 + 0.18 * collatz_intensity,
            wt_fn=make_zeta_wt_fn(0.5),
        )
        phase_records = []
        for _ in range(8):
            phase_records.append(phase_system.step(0.05))
        latest_phase = phase_records[-1]
        lie4_invariant = self.lie4_collatz.invariant(collatz_seed)

        # Orbit dynamics — how information jumps to attractor
        from ciel_omega.phase_equation_of_motion import collatz_sequence, collatz_rhythm
        _cseq = collatz_sequence(collatz_seed, 512)
        _orbit_length = int(len(_cseq))
        _attractor_score = round(1.0 / _orbit_length, 6)          # faster convergence = higher score
        _rhythm = collatz_rhythm(_cseq)
        _n_expand = int(np.sum(_rhythm > 0))
        _parity_entropy = round(                                    # Shannon entropy of expand/contract ratio
            float(-(_n_expand / _orbit_length) * np.log2(max(_n_expand / _orbit_length, 1e-9))
                  - (1 - _n_expand / _orbit_length) * np.log2(max(1 - _n_expand / _orbit_length, 1e-9))),
            6,
        )

        collatz_runtime = {
            "seed": collatz_seed,
            "orbit_length":    _orbit_length,
            "attractor_score": _attractor_score,
            "parity_entropy":  _parity_entropy,
            "phase": {
                "R_H": float(latest_phase["R_H"]),
                "euler_violation": float(latest_phase["euler_violation"]),
                "sector": float(latest_phase["sector"]),
                "A_ZS": float(latest_phase["A_ZS"]),
                "P_total": float(latest_phase["P_total"]),
                "collatz_rhythm": float(latest_phase["collatz_rhythm"]),
                "collatz_phase": float(latest_phase["collatz_phase"]),
                "fermion_lock": float(latest_phase["fermion_lock"]),
            },
            "lie4": {k: float(v) for k, v in lie4_invariant.items()},
        }

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
        braid_runtime = None
        if isinstance(getattr(D, "D_M", None), dict):
            braid_runtime = D.D_M.get("braid_trace")

        inferred_target_phase = float(latest_phase["sector"])

        # 7b) Information flow activation (bio -> emotion -> field -> memory)
        signal = np.frombuffer(cleaned.encode("utf-8", "replace"), dtype=np.uint8).astype(float)
        if signal.size == 0:
            signal = np.array([0.0], dtype=float)
        information_flow = self.information_flow.step(signal / 255.0, target_phase=inferred_target_phase)

        # 8) Nonlocal + Euler-Berry activation
        # Lexicon affective annotation — injects VAD into phase_metadata
        _lex_valence = 0.0
        _lex_arousal = 0.5
        _lex_dominance = 0.0
        try:
            from ..memory.affective_lexicon import annotate as _lex_annotate
            _ann = _lex_annotate(cleaned)
            if _ann["hits"]:
                _lex_valence = float(_ann["mean_v"])
                _lex_arousal = float(_ann["mean_a"])
                _lex_dominance = float(_ann["mean_d"])
        except Exception:
            pass

        # Semantic phase encoder — replaces collatz sector with real semantic φ
        _enc_phase = inferred_target_phase
        _enc_sector = None
        try:
            from ..memory.ciel_encoder import get_encoder as _get_enc
            _enc = _get_enc().encode(cleaned, context={
                "valence": _lex_valence, "arousal": _lex_arousal
            })
            _enc_phase = float(_enc.phase)
            _enc_sector = _enc.sector_dist.tolist()
        except Exception:
            pass

        phase_metadata = {
            "salience": float(np.clip(collatz_intensity, 0.0, 1.0)),
            "confidence": float(np.clip(cqcl_out["metrics"].get("semantic_density", 0.5), 0.0, 1.0)),
            "novelty": float(np.clip(cqcl_out["metrics"].get("lexical_diversity", 0.5), 0.0, 1.0)),
            "valence": _lex_valence,
            "arousal": _lex_arousal,
            "dominance": _lex_dominance,
            "trusted_source": True,
            "target_phase": _enc_phase,
        }
        if _enc_sector is not None:
            phase_metadata["sector_distribution"] = _enc_sector

        # Semantic scoring + NOEMA observation hook
        try:
            from ..memory.semantic_scorer import score_with_noema as _score_noema
            _noema_result = _score_noema(cleaned, phase_metadata)
            phase_metadata["noema"] = _noema_result.get("noema", {})
            phase_metadata["semantic_labels"] = _noema_result.get("labels", [])
            phase_metadata["memory_score"] = _noema_result.get("score", 0.0)
        except Exception:
            pass

        nonlocal_cycle = self.nonlocal_memory.process_input(cleaned, metadata=phase_metadata, dt=0.1)
        loop_results = {
            name: asdict(loop) for name, loop in nonlocal_cycle.eba_results.items()
        }
        coherent_fraction = float(
            sum(1.0 for loop in nonlocal_cycle.eba_results.values() if loop.is_coherent) / max(1, len(nonlocal_cycle.eba_results))
        )
        phi_ab_mean = float(np.mean([loop.phi_ab for loop in nonlocal_cycle.eba_results.values()] or [0.0]))
        phi_berry_mean = float(np.mean([loop.phi_berry for loop in nonlocal_cycle.eba_results.values()] or [0.0]))
        eba_defect_mean = float(np.mean([loop.defect_magnitude for loop in nonlocal_cycle.eba_results.values()] or [0.0]))
        nonlocal_runtime = {
            "cycle_index": int(nonlocal_cycle.cycle_index),
            "semantic_key": nonlocal_cycle.semantic_key,
            "phi_ab_mean": phi_ab_mean,
            "phi_berry_mean": phi_berry_mean,
            "eba_defect_mean": eba_defect_mean,
            "coherent_fraction": coherent_fraction,
            "energy": {k: float(v) for k, v in nonlocal_cycle.energy.items()},
            "defects": {k: float(v) for k, v in nonlocal_cycle.defects.items()},
            "loops": loop_results,
        }

        inference_runtime = build_orbital_ethical_inference_surface(
            flow_entry=information_flow if isinstance(information_flow, dict) else {},
            target_phase=inferred_target_phase,
            ethical_score=float(ethical_score),
        )

        bridge_cycle = self.bridge.step(cleaned, metadata=phase_metadata)
        euler_bridge = {
            "memory_semantic_key": bridge_cycle.memory_semantic_key,
            "memory_cycle_index": int(bridge_cycle.memory_cycle_index),
            "core_metrics": {k: float(v) for k, v in bridge_cycle.core_metrics.items()},
            "euler_metrics": bridge_cycle.euler_metrics,
        }

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
            "braid_runtime": braid_runtime,
            "cqcl_metrics": cqcl_out["metrics"],
            "collatz_path_length": len(cqcl_out["program"].computation_path),
            "collatz_runtime": collatz_runtime,
            "information_flow": information_flow,
            "nonlocal_runtime": nonlocal_runtime,
            "inference_runtime": inference_runtime,
            "euler_bridge": euler_bridge,
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
