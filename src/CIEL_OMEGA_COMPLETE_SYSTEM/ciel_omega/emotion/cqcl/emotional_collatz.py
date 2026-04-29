"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Emotional Collatz Engine — emotion-modulated Collatz sequences
driving quantum consciousness computation.

Source: extemot.py (EmotionalCollatzEngine + demo)
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Callable, Dict, List

import numpy as np

np.seterr(all="ignore")

from emotion.cqcl.cqcl_program import CQCL_Program, normalize_profile, stable_hash
from emotion.cqcl.quantum_engine import CIEL_Quantum_Engine


class EmotionalCollatzEngine(CIEL_Quantum_Engine):
    """CQCL engine with emotional Collatz operators (love/fear/joy/anger/peace/sadness)."""

    def __init__(self):
        super().__init__()
        self.emotional_operators = self._initialize_emotional_operators()

    # -- operator table -----------------------------------------------------

    def _initialize_emotional_operators(self) -> Dict[str, Dict[str, Any]]:
        return {
            "love": {
                "function": lambda n, i: n * (1 + i) if n % 2 == 0 else 3 * n + int(10 * i),
                "description": "Mnożenie przez miłość — ekspansja harmoniczna",
            },
            "fear": {
                "function": lambda n, i: max(1, int(n // max(1.0, 2 + i))) if n % 2 == 0 else max(1, n - int(5 * i)),
                "description": "Redukcja przez strach — kontrakcja ochronna",
            },
            "joy": {
                "function": lambda n, i: int(n // 2 + int(10 * i)) if n % 2 == 0 else 3 * n + int(20 * i),
                "description": "Eksplozja radości — wzmocniona kreatywność",
            },
            "anger": {
                "function": lambda n, i: int(n * (2 + i)) if n % 2 == 0 else 5 * n + int(15 * i),
                "description": "Mnożenie gniewu — intensyfikacja transformacji",
            },
            "peace": {
                "function": lambda n, i: max(1, int(n // max(1.0, 1 + i))) if n % 2 == 0 else n + 1,
                "description": "Wyciszenie pokoju — łagodna konwergencja",
            },
            "sadness": {
                "function": lambda n, i: max(1, n - int(3 * i)) if n % 2 == 0 else max(1, n // 2),
                "description": "Redukcja smutku — spowolniona ewolucja",
            },
        }

    # -- emotional Collatz transform ----------------------------------------

    def emotional_collatz_transform(self, n: int, emotional_profile: Dict[str, float]) -> int:
        if n <= 1:
            return 1
        emotional_mix = 0.0
        for emotion, intensity in emotional_profile.items():
            if emotion in self.emotional_operators and intensity > 0.1:
                op = self.emotional_operators[emotion]["function"]
                emotional_mix += op(n, intensity) * intensity
        if emotional_mix == 0:
            return n // 2 if n % 2 == 0 else 3 * n + 1
        return max(1, int(emotional_mix / sum(emotional_profile.values())))

    # -- main entry point ---------------------------------------------------

    def execute_emotional_program(self, intention: str, input_data: Any = None) -> Dict[str, Any]:
        program = self.compiler.compile_program(intention, input_data)
        emotional_path = self._generate_emotional_collatz_path(program)
        program.computation_path = emotional_path
        computation_result = self._execute_emotional_computation(program)
        final_result = self._apply_emotional_ramanujan_resonance(computation_result, program)
        metrics = self._calculate_emotional_metrics(program, computation_result, final_result)
        return {
            "program": program,
            "computation_result": computation_result,
            "final_result": final_result,
            "metrics": metrics,
            "emotional_landscape": self._analyze_emotional_landscape(program, emotional_path),
        }

    # -- Collatz path generation --------------------------------------------

    def _generate_emotional_collatz_path(self, program: CQCL_Program) -> List[int]:
        emo = dict(program.semantic_tree["emotional_profile"])
        seed = program.semantic_hash % 10000 + 1
        path: List[int] = []
        current = seed
        for iteration in range(300):
            path.append(current)
            current = self.emotional_collatz_transform(current, emo)
            if current == 1:
                break
            if iteration % 10 == 0:
                emo = self._evolve_emotional_profile(emo, iteration)
        path.append(1)
        return path

    def _evolve_emotional_profile(self, profile: Dict[str, float], iteration: int) -> Dict[str, float]:
        factor = float(np.sin(iteration * 0.1) * 0.1 + 1.0)
        evolved = {}
        for emotion, intensity in profile.items():
            fluct = float(np.clip(np.random.normal(1.0, 0.1), 0.7, 1.3))
            evolved[emotion] = max(0.0, min(1.0, intensity * factor * fluct))
        return normalize_profile(evolved)

    # -- quantum computation ------------------------------------------------

    def _execute_emotional_computation(self, program: CQCL_Program) -> Dict[str, Any]:
        from mathematics.safe_operations import HeisenbergSoftClipper, heisenberg_soft_clip
        
        path = program.computation_path
        qv = program.quantum_variables
        emo_prof = dict(program.semantic_tree["emotional_profile"])
        interm: list = []
        emo_amps: list = []
        coh_hist: list = []
        current_state = complex(program.input_data or 1.0, 0.0)
        magnitude_clipper = HeisenbergSoftClipper(k_sigma=3.0)
        log_clipper = HeisenbergSoftClipper(k_sigma=4.0)

        resonance = float(np.clip(qv["resonance"], 0.0, 1.0))
        superpos = float(np.clip(qv["superposition"], 0.0, 1.0))
        qflux = float(np.clip(qv["quantum_flux"], 0.0, 1.0))
        ent = float(np.clip(qv["entanglement"], 0.0, 1.0))
        base_coh = float(np.clip(qv["coherence"], 0.0, 1.0))

        for step, cn in enumerate(path):
            emo_intensity = sum(emo_prof.values()) / (len(emo_prof) or 1)
            if cn % 2 == 0:
                rb = max(1.0, math.sqrt(cn))
                rb = float(heisenberg_soft_clip(rb, scale=100.0))
                em = 1.0 + 0.5 * emo_intensity
                current_state *= rb * np.exp(1j * resonance * step * em) * em
            else:
                exponent = superpos * (0.5 + emo_intensity) * math.log(max(cn, 1))
                exponent = float(log_clipper(exponent, scale=12.0))
                eb = float(np.exp(exponent))
                eb = float(heisenberg_soft_clip(eb, scale=100.0))
                current_state *= eb * np.exp(1j * qflux * step * (1 + emo_intensity))

            magnitude = abs(current_state)
            if not np.isfinite(magnitude):
                phase = float(np.angle(current_state)) if np.isfinite(np.angle(current_state)) else 0.0
                clipped_mag = float(magnitude_clipper(np.nan_to_num(magnitude, nan=0.0, posinf=1e6, neginf=0.0), scale=1e6))
                current_state = clipped_mag * np.exp(1j * phase)
            elif magnitude > 1e6:
                phase = np.angle(current_state)
                clipped_mag = float(magnitude_clipper(magnitude, scale=1e6))
                current_state = clipped_mag * np.exp(1j * phase)

            if step % 5 == 0:
                entang = sum(
                    intensity * np.exp(1j * (hashlib.sha1(em.encode()).digest()[0] % 100) / 100.0 * math.pi)
                    for em, intensity in emo_prof.items()
                )
                current_state += entang * ent * 0.1

            if not np.isfinite(current_state.real) or not np.isfinite(current_state.imag):
                current_state = complex(0.0, 0.0)

            amplitude = float(np.nan_to_num(abs(current_state) * (1 + emo_intensity), nan=0.0, posinf=1e6, neginf=0.0))
            coherence_step = float(np.nan_to_num(base_coh * ((0.9 + 0.1 * emo_intensity) ** step), nan=0.0, posinf=1.0, neginf=0.0))

            interm.append(current_state)
            emo_amps.append(amplitude)
            coh_hist.append(float(np.clip(coherence_step, 0.0, 1.0)))

            program.execution_trace.append({
                "step": step, "collatz_number": cn, "state": current_state,
                "amplitude": float(abs(current_state)), "emotional_intensity": emo_intensity,
                "emotional_profile": dict(emo_prof),
            })

        emo_amps_safe = [float(np.nan_to_num(heisenberg_soft_clip(amp, scale=1e6), nan=0.0, posinf=1e6, neginf=0.0)) for amp in emo_amps]
        final_state = current_state if np.isfinite(current_state.real) and np.isfinite(current_state.imag) else complex(0.0, 0.0)

        return {
            "final_state": final_state,
            "intermediate_states": interm,
            "emotional_amplitudes": emo_amps_safe,
            "coherence_history": coh_hist,
            "path_length": len(path),
            "max_emotional_amplitude": max(emo_amps_safe) if emo_amps_safe else 0.0,
            "emotional_convergence": self._calculate_emotional_convergence(emo_amps_safe),
        }

    def _calculate_emotional_convergence(self, amplitudes: List[float]) -> float:
        if len(amplitudes) < 2:
            return 0.0
        amps = np.asarray(amplitudes, dtype=float)
        amps = np.nan_to_num(amps, nan=0.0, posinf=1e6, neginf=0.0)
        mean_amp = float(np.mean(amps))
        if mean_amp <= 1e-12:
            return 0.0
        var = float(np.var(amps) / (mean_amp + 1e-10))
        stability = 1.0 / (1.0 + max(var, 0.0))
        if len(amps) > 15:
            slope = float(np.polyfit(np.arange(len(amps), dtype=float), amps, 1)[0])
            slope = float(np.nan_to_num(slope, nan=0.0, posinf=1e3, neginf=-1e3))
            trend_stability = 1.0 / (1.0 + abs(slope))
        else:
            trend_stability = 0.5
        return float(np.clip((stability + trend_stability) / 2.0, 0.0, 1.0))

    # -- Ramanujan resonance ------------------------------------------------

    def _apply_emotional_ramanujan_resonance(self, result: Dict[str, Any], program: CQCL_Program) -> complex:
        raw = result["final_state"]
        emo = program.semantic_tree["emotional_profile"]
        corr = 1.0
        for emotion, intensity in emo.items():
            h = hashlib.blake2b(emotion.encode(), digest_size=2).digest()[0] / 255.0
            corr *= 1.0 + intensity * h * 0.1
        emo_phase = sum(
            intensity * (hashlib.sha1(em.encode()).digest()[0] % 100) / 100.0
            for em, intensity in emo.items()
        )
        phase = np.exp(1j * 2 * np.pi * (emo_phase / max(1, len(emo))))
        raw = raw if np.isfinite(raw.real) and np.isfinite(raw.imag) else complex(0.0, 0.0)
        out = raw * corr * phase
        if not np.isfinite(out.real) or not np.isfinite(out.imag):
            return complex(0.0, 0.0)
        return out

    # -- emotional metrics --------------------------------------------------

    def _calculate_emotional_metrics(self, program, result, final_result):
        base = super()._calculate_comprehensive_metrics(program, result, final_result)
        emo = program.semantic_tree["emotional_profile"]
        vals = list(emo.values())
        emotional_convergence = float(np.nan_to_num(result["emotional_convergence"], nan=0.0, posinf=1.0, neginf=0.0))
        emotional_convergence = float(np.clip(emotional_convergence, 0.0, 1.0))
        # Intensity = dominance of strongest emotion (max of distribution).
        # Using mean would always yield 1/len(vals) for normalised profiles.
        emotional_intensity = float(np.clip(max(vals) if vals else 0.0, 0.0, 1.0))
        emotional_diversity = float(np.clip(len([v for v in vals if v > 0.1]) / max(1, len(vals)), 0.0, 1.0))
        emotional_balance = float(np.clip(1.0 - abs(emo.get("love", 0) - emo.get("fear", 0)), 0.0, 1.0))
        heart_mind = float(np.clip(base["quantum_coherence"] * emotional_convergence, 0.0, 1.0))
        base.update({
            "emotional_coherence": emotional_convergence,
            "emotional_intensity": emotional_intensity,
            "emotional_diversity": emotional_diversity,
            "emotional_balance": emotional_balance,
            "heart_mind_coherence": heart_mind,
        })
        return base

    # -- landscape analysis -------------------------------------------------

    def _analyze_emotional_landscape(self, program, path):
        emo = program.semantic_tree["emotional_profile"]
        dominant = max(emo.items(), key=lambda x: x[1])[0] if emo else "none"
        changes = np.diff(path) if len(path) > 1 else np.array([])
        if len(changes) > 0:
            g, d = int(np.sum(changes > 0)), int(np.sum(changes < 0))
            pat = "EKSPANSJA_EMOCJONALNA" if g > 2 * d else "KONTRAKCJA_EMOCJONALNA" if d > 2 * g else "RÓWNOWAGA_EMOCJONALNA"
        else:
            pat = "BRAK_WZORCA"
        peaks = sum(1 for i in range(1, len(path) - 1) if path[i - 1] < path[i] > path[i + 1]) if len(path) > 2 else 0
        patterns = [pat] + (["CYKLICZNOŚĆ_EMOCJONALNA"] if peaks > len(path) // 10 else [])
        return {
            "dominant_emotion": dominant,
            "emotional_complexity": len([v for v in emo.values() if v > 0.2]),
            "path_emotional_signature": int(stable_hash(str(tuple(path))) % 10000),
            "emotional_operators_used": [e for e, v in emo.items() if v > 0.3 and e in self.emotional_operators],
            "emotional_resonance_pattern": patterns,
        }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demonstracja_emocjonalnego_collatza():
    """Run the emotional Collatz demonstration."""
    print("🎭 EMOCJONALNY COLLATZ – DEMO")
    engine = EmotionalCollatzEngine()
    intencje = [
        "Kocham życie i wszystko co ze sobą niesie – pełen entuzjazmu i radości",
        "Obawiam się przyszłości, ale pragnę znaleźć w sobie siłę i odwagę",
        "Jestem zły na niesprawiedliwość świata, ale chcę to zmienić przez działanie",
        "Czuję głęboki spokój i jedność z wszechświatem – wszystko jest idealne",
        "Smutek miesza się z nadzieją w poszukiwaniu sensu istnienia",
    ]
    for i, intencja in enumerate(intencje, 1):
        print(f"\n🧠 TEST {i}: {intencja[:72]}…")
        out = engine.execute_emotional_program(intencja, input_data=42)
        f = out["final_result"]
        m = out["metrics"]
        la = out["emotional_landscape"]
        print(f"   📊 final ≈ {f.real:+.4e}{f.imag:+.4e}j")
        print(f"   📈 emo_coh={m['emotional_coherence']:.4f} hmc={m['heart_mind_coherence']:.4f}")
        print(f"   🎭 dominant={la['dominant_emotion']} patterns={', '.join(la['emotional_resonance_pattern'])}")


__all__ = ["EmotionalCollatzEngine", "demonstracja_emocjonalnego_collatza"]
