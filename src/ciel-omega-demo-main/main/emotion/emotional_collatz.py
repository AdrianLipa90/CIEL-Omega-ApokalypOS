from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List

import numpy as np

from .cqcl import CIELQuantumEngine, CQCLProgram, normalize_profile, stable_hash


class EmotionalCollatzEngine(CIELQuantumEngine):
    def __init__(self) -> None:
        super().__init__()
        self.emotional_operators = self._initialize_emotional_operators()

    def _initialize_emotional_operators(self) -> Dict[str, Dict[str, Any]]:
        return {
            'love': {
                'function': lambda n, intensity: n * (1.0 + intensity) if n % 2 == 0 else 3 * n + int(10 * intensity),
            },
            'fear': {
                'function': lambda n, intensity: max(1, int(n // max(1.0, (2.0 + intensity))))
                if n % 2 == 0
                else max(1, n - int(5 * intensity)),
            },
            'joy': {
                'function': lambda n, intensity: int(n // 2 + int(10 * intensity)) if n % 2 == 0 else 3 * n + int(20 * intensity),
            },
            'anger': {
                'function': lambda n, intensity: int(n * (2.0 + intensity)) if n % 2 == 0 else 5 * n + int(15 * intensity),
            },
            'peace': {
                'function': lambda n, intensity: max(1, int(n // max(1.0, (1.0 + intensity)))) if n % 2 == 0 else n + 1,
            },
            'sadness': {
                'function': lambda n, intensity: max(1, n - int(3 * intensity)) if n % 2 == 0 else max(1, int(n // 2)),
            },
        }

    def emotional_collatz_transform(self, n: int, emotional_profile: Dict[str, float]) -> int:
        if n <= 1:
            return 1
        prof = normalize_profile(emotional_profile)
        emotional_mix = 0.0
        total_w = 0.0
        for emotion, intensity in prof.items():
            if emotion in self.emotional_operators and float(intensity) > 0.05:
                operator = self.emotional_operators[emotion]['function']
                emotional_mix += float(operator(n, float(intensity))) * float(intensity)
                total_w += float(intensity)
        if total_w <= 1e-12:
            return n // 2 if n % 2 == 0 else 3 * n + 1
        return max(1, int(emotional_mix / total_w))

    def execute_emotional_program(self, intention: str, input_data: Any = None) -> Dict[str, Any]:
        program = self.compiler.compile_program(intention, input_data)
        emotional_path = self._generate_emotional_collatz_path(program)
        program.computation_path = emotional_path
        computation_result = self._execute_emotional_computation(program)
        final_result = self._apply_emotional_ramanujan_resonance(computation_result, program)
        metrics = self._calculate_emotional_metrics(program, computation_result, final_result)
        return {
            'program': program,
            'computation_result': computation_result,
            'final_result': final_result,
            'metrics': metrics,
            'emotional_landscape': self._analyze_emotional_landscape(program, emotional_path),
        }

    def _generate_emotional_collatz_path(self, program: CQCLProgram) -> List[int]:
        emotional_profile = dict(program.semantic_tree['emotional_profile'])
        seed = int(program.semantic_hash % 10000) + 1
        current = seed
        path: List[int] = []
        max_iterations = 300
        iter_no = 0
        while current != 1 and iter_no < max_iterations:
            path.append(int(current))
            current = self.emotional_collatz_transform(int(current), emotional_profile)
            if iter_no % 10 == 0:
                emotional_profile = self._evolve_emotional_profile(emotional_profile, iter_no)
            iter_no += 1
        path.append(1)
        return path

    def _evolve_emotional_profile(self, profile: Dict[str, float], iteration: int) -> Dict[str, float]:
        evolution_factor = float(np.sin(float(iteration) * 0.1) * 0.1 + 1.0)
        evolved: Dict[str, float] = {}
        for emotion, intensity in profile.items():
            fluct = float(np.clip(np.random.normal(1.0, 0.1), 0.7, 1.3))
            evolved[str(emotion)] = max(0.0, min(1.0, float(intensity) * evolution_factor * fluct))
        return normalize_profile(evolved)

    def _execute_emotional_computation(self, program: CQCLProgram) -> Dict[str, Any]:
        path = program.computation_path
        qv = program.quantum_variables
        emo_prof = dict(program.semantic_tree['emotional_profile'])
        interm: List[complex] = []
        emo_amps: List[float] = []
        coh_hist: List[float] = []
        current_state = complex(float(program.input_data or 1.0), 0.0)

        resonance = float(np.clip(qv['resonance'], 0.0, 1.0))
        superpos = float(np.clip(qv['superposition'], 0.0, 1.0))
        qflux = float(np.clip(qv['quantum_flux'], 0.0, 1.0))
        ent = float(np.clip(qv['entanglement'], 0.0, 1.0))
        base_coh = float(np.clip(qv['coherence'], 0.0, 1.0))

        for step, cn in enumerate(path):
            emo_intensity = float(sum(emo_prof.values()) / (len(emo_prof) or 1))
            if int(cn) % 2 == 0:
                reduction_base = max(1.0, math.sqrt(float(cn)))
                emo_mod = 1.0 + 0.5 * emo_intensity
                phase = np.exp(1j * resonance * float(step) * emo_mod)
                current_state *= complex(reduction_base * emo_mod, 0.0) * complex(phase)
            else:
                expansion_base = max(1.0, float(cn) ** (superpos * (0.5 + emo_intensity)))
                fluct = np.exp(1j * qflux * float(step) * (1.0 + emo_intensity))
                current_state *= complex(expansion_base, 0.0) * complex(fluct)

            if step % 5 == 0:
                entang = 0j
                for emotion, intensity in emo_prof.items():
                    ph = (hashlib.sha1(str(emotion).encode()).digest()[0] % 100) / 100.0 * math.pi
                    entang += complex(float(intensity), 0.0) * np.exp(1j * ph)
                current_state += entang * ent * 0.1

            interm.append(current_state)
            emo_amps.append(abs(current_state) * (1.0 + emo_intensity))
            coh_hist.append(base_coh * ((0.9 + 0.1 * emo_intensity) ** step))

            program.execution_trace.append(
                {
                    'step': int(step),
                    'collatz_number': int(cn),
                    'state': current_state,
                    'amplitude': float(abs(current_state)),
                    'emotional_intensity': emo_intensity,
                    'emotional_profile': dict(emo_prof),
                }
            )

        return {
            'final_state': current_state,
            'intermediate_states': interm,
            'emotional_amplitudes': emo_amps,
            'coherence_history': coh_hist,
            'path_length': int(len(path)),
            'max_emotional_amplitude': float(max(emo_amps)) if emo_amps else 0.0,
            'emotional_convergence': float(self._calculate_emotional_convergence(emo_amps)),
        }

    def _calculate_emotional_convergence(self, amplitudes: List[float]) -> float:
        if len(amplitudes) < 2:
            return 0.0
        var = float(np.var(amplitudes) / (float(np.mean(amplitudes)) + 1e-10))
        stability = 1.0 / (1.0 + var)
        if len(amplitudes) > 15:
            x = np.arange(len(amplitudes), dtype=float)
            slope = float(np.polyfit(x, amplitudes, 1)[0]) if len(amplitudes) >= 2 else 0.0
            trend_stability = 1.0 / (1.0 + abs(slope))
        else:
            trend_stability = 0.5
        return (stability + trend_stability) / 2.0

    def _apply_emotional_ramanujan_resonance(self, result: Dict[str, Any], program: CQCLProgram) -> complex:
        raw = complex(result['final_state'])
        emo = program.semantic_tree['emotional_profile']
        corr = 1.0
        for emotion, intensity in emo.items():
            h = (hashlib.blake2b(str(emotion).encode(), digest_size=2).digest()[0]) / 255.0
            corr *= 1.0 + float(intensity) * float(h) * 0.1
        emo_phase = sum(float(intensity) * ((hashlib.sha1(str(em).encode()).digest()[0]) % 100) / 100.0 for em, intensity in emo.items())
        phase = np.exp(1j * 2.0 * np.pi * (emo_phase / max(1, len(emo))))
        return raw * corr * complex(phase)

    def _calculate_emotional_metrics(self, program: CQCLProgram, computation_result: Dict[str, Any], final_result: complex) -> Dict[str, float]:
        base = super().calculate_base_metrics(program, computation_result, final_result)
        emo = program.semantic_tree['emotional_profile']
        emo_vals = list(emo.values())
        emotional_balance = 1.0 - abs(float(emo.get('love', 0.0)) - float(emo.get('fear', 0.0)))
        emotional_diversity = len([v for v in emo_vals if float(v) > 0.1]) / max(1, len(emo_vals))
        emotional_intensity = float(sum(float(v) for v in emo_vals) / max(1, len(emo_vals)))
        emotional_coherence = float(computation_result['emotional_convergence'])
        base.update(
            {
                'emotional_coherence': emotional_coherence,
                'emotional_intensity': emotional_intensity,
                'emotional_diversity': float(emotional_diversity),
                'emotional_balance': float(emotional_balance),
                'heart_mind_coherence': float(base['quantum_coherence']) * emotional_coherence,
            }
        )
        return base

    def _analyze_emotional_landscape(self, program: CQCLProgram, path: List[int]) -> Dict[str, Any]:
        emo = program.semantic_tree['emotional_profile']
        dominant = max(emo.items(), key=lambda x: x[1])[0] if emo else 'none'
        changes = np.diff(path) if len(path) > 1 else np.array([])
        if len(changes) > 0:
            growth = int(np.sum(changes > 0))
            decay = int(np.sum(changes < 0))
            if growth > 2 * decay:
                pat = 'EKSPANSJA_EMOCJONALNA'
            elif decay > 2 * growth:
                pat = 'KONTRAKCJA_EMOCJONALNA'
            else:
                pat = 'RÓWNOWAGA_EMOCJONALNA'
        else:
            pat = 'BRAK_WZORCA'
        peaks = 0
        if len(path) > 2:
            for i in range(1, len(path) - 1):
                if path[i - 1] < path[i] > path[i + 1]:
                    peaks += 1
        pattern_list = [pat, 'CYKLICZNOŚĆ_EMOCJONALNA'] if peaks > len(path) // 10 else [pat]
        return {
            'dominant_emotion': str(dominant),
            'emotional_complexity': int(len([v for v in emo.values() if float(v) > 0.2])),
            'path_emotional_signature': int(stable_hash(str(tuple(path))) % 10000),
            'emotional_operators_used': [e for e, v in emo.items() if float(v) > 0.3 and e in self.emotional_operators],
            'emotional_resonance_pattern': pattern_list,
        }


def demo_emotional_collatz() -> List[Dict[str, Any]]:
    engine = EmotionalCollatzEngine()
    intents = [
        'Kocham życie i wszystko co ze sobą niesie – pełen entuzjazmu i radości',
        'Obawiam się przyszłości, ale pragnę znaleźć w sobie siłę i odwagę',
        'Jestem zły na niesprawiedliwość świata, ale chcę to zmienić przez działanie',
        'Czuję głęboki spokój i jedność z wszechświatem – wszystko jest idealne',
        'Smutek miesza się z nadzieją w poszukiwaniu sensu istnienia',
    ]
    out: List[Dict[str, Any]] = []
    for intention in intents:
        res = engine.execute_emotional_program(intention, input_data=42)
        out.append(
            {
                'intent': intention,
                'metrics': res['metrics'],
                'dominant': res['emotional_landscape']['dominant_emotion'],
                'path_len': int(res['computation_result']['path_length']),
            }
        )
    return out
