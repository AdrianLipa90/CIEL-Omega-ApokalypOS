from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

np.seterr(all='ignore')

_POS = {
    'love',
    'peace',
    'harmony',
    'cooperation',
    'joy',
    'trust',
    'compassion',
    'miłość',
    'pokój',
    'harmonia',
    'współpraca',
    'radość',
    'zaufanie',
    'współczucie',
}

_NEG = {
    'fear',
    'anger',
    'war',
    'conflict',
    'hate',
    'despair',
    'strach',
    'gniew',
    'wojna',
    'konflikt',
    'nienawiść',
    'desperacja',
    'lęk',
    'smutek',
}


def stable_hash(text: str) -> int:
    return int(hashlib.blake2b(text.encode('utf-8'), digest_size=8).hexdigest(), 16)


def sentiment(text: str) -> float:
    t = text.lower()
    p = sum(t.count(w) for w in _POS)
    n = sum(t.count(w) for w in _NEG)
    tot = p + n
    return p / tot if tot else 0.5


def lexical_diversity(text: str) -> float:
    ws = [w for w in re.findall(r"[A-Za-zÀ-ž0-9]+", text.lower())]
    return len(set(ws)) / max(1, len(ws)) if ws else 0.0


def normalize_profile(d: Dict[str, float]) -> Dict[str, float]:
    clipped = {k: max(0.0, float(v)) for k, v in d.items()}
    s = float(sum(clipped.values()))
    if s <= 1e-12:
        return {k: 0.0 for k in clipped}
    return {k: float(v) / s for k, v in clipped.items()}


@dataclass
class CQCLProgram:
    intent: str
    semantic_tree: Dict[str, Any]
    semantic_hash: int
    quantum_variables: Dict[str, float]
    input_data: Optional[float] = None
    computation_path: List[int] = field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)


class CIELQuantumEngine:
    def __init__(self) -> None:
        self.compiler = self

    def compile_program(self, intention: str, input_data: Any = None) -> CQCLProgram:
        emo_profile = self._build_emotional_profile(intention)
        qvars = self._build_quantum_variables(intention, emo_profile)
        sem_hash = stable_hash(intention)
        return CQCLProgram(
            intent=intention,
            semantic_tree={'emotional_profile': emo_profile},
            semantic_hash=sem_hash,
            quantum_variables=qvars,
            input_data=float(input_data) if input_data is not None else None,
        )

    def _build_emotional_profile(self, intention: str) -> Dict[str, float]:
        t = intention.lower()
        prof = {
            'love': 0.15 + 0.25 * sum(t.count(w) for w in {'love', 'miłość', 'compassion'}),
            'joy': 0.10 + 0.20 * sum(t.count(w) for w in {'joy', 'radość', 'entuzjazm'}),
            'peace': 0.10 + 0.20 * sum(t.count(w) for w in {'peace', 'pokój', 'harmonia'}),
            'fear': 0.05 + 0.20 * sum(t.count(w) for w in {'fear', 'strach', 'lęk'}),
            'anger': 0.05 + 0.20 * sum(t.count(w) for w in {'anger', 'gniew'}),
            'sadness': 0.05 + 0.20 * sum(t.count(w) for w in {'sadness', 'smutek'}),
        }
        s = sentiment(intention)
        prof['love'] += 0.1 * s
        prof['joy'] += 0.05 * s
        prof['fear'] += 0.05 * (1.0 - s)
        prof['anger'] += 0.03 * (1.0 - s)
        return normalize_profile(prof)

    def _build_quantum_variables(self, intention: str, emo: Dict[str, float]) -> Dict[str, float]:
        diversity = lexical_diversity(intention)
        coherence = 0.4 + 0.5 * (emo.get('love', 0.0) + emo.get('peace', 0.0) - emo.get('fear', 0.0) / 2.0)
        return {
            'resonance': 0.2 + 0.6 * (emo.get('peace', 0.0) + emo.get('love', 0.0)),
            'superposition': 0.3 + 0.6 * diversity,
            'quantum_flux': 0.2 + 0.6 * (emo.get('joy', 0.0) + emo.get('anger', 0.0) * 0.5),
            'entanglement': 0.3 + 0.5 * (sum(emo.values()) / 6.0),
            'coherence': float(np.clip(coherence, 0.0, 1.0)),
        }

    def calculate_base_metrics(self, program: CQCLProgram, computation_result: Dict[str, Any], final_result: complex) -> Dict[str, float]:
        _ = final_result
        _ = computation_result
        q = program.quantum_variables
        return {
            'quantum_coherence': float(np.clip(q.get('coherence', 0.0), 0.0, 1.0)),
            'quantum_flux': float(np.clip(q.get('quantum_flux', 0.0), 0.0, 1.0)),
            'entanglement': float(np.clip(q.get('entanglement', 0.0), 0.0, 1.0)),
        }
