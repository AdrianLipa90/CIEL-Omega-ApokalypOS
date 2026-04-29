"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

CIEL/Ω – Emotional Collatz Engine (CQCL layer, self-contained)

Co jest w środku:
- CQCL_Program                 – lekki kontener programu (semantic_tree, hash, kwant.zmienne)
- CIEL_Quantum_Engine          – baza: „kompilator” intencji → program + metryki
- EmotionalCollatzEngine       – Twój silnik z operatorami emocji (love/fear/joy/anger/peace/sadness)
- Minimalny „kompilator semantyczny”:
    * wydobywa profil emocjonalny z intencji (heurystyka) + normalizacja
    * ustawia quantum_variables: resonance, superposition, quantum_flux, entanglement, coherence
- Demo: demonstracja_emocjonalnego_collatza()
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import math, re, hashlib, numpy as np

# Canonical imports replacing duplicate local definitions
from emotion.cqcl.cqcl_program import CQCL_Program
from emotion.cqcl.emotional_collatz import EmotionalCollatzEngine, demonstracja_emocjonalnego_collatza
from emotion.cqcl.quantum_engine import CIEL_Quantum_Engine

np.seterr(all="ignore")
_POS = {"love", "peace", "harmony", "cooperation", "joy", "trust", "compassion",
        "miłość", "pokój", "harmonia", "współpraca", "radość", "zaufanie", "współczucie"}
_NEG = {"fear", "anger", "war", "conflict", "hate", "despair",
        "strach", "gniew", "wojna", "konflikt", "nienawiść", "desperacja", "lęk", "smutek"}
def _stable_hash(text: str) -> int:
    # deterministyczny 64-bit hash
    return int(hashlib.blake2b(text.encode("utf-8"), digest_size=8).hexdigest(), 16)
def _sentiment(text: str) -> float:
    t = text.lower()
    p = sum(t.count(w) for w in _POS)
    n = sum(t.count(w) for w in _NEG)
    tot = p + n
    return p / tot if tot else 0.5
def _lexical_diversity(text: str) -> float:
    ws = [w for w in re.findall(r"[A-Za-zÀ-ž0-9]+", text.lower())]
    return len(set(ws)) / max(1, len(ws)) if ws else 0.0
def _normalize_profile(d: Dict[str, float]) -> Dict[str, float]:
    # obcina <0, skaluje do sumy 1 (jeśli coś jest >0)
    clipped = {k: max(0.0, float(v)) for k, v in d.items()}
    s = sum(clipped.values())
    if s <= 1e-12:
        return {k: 0.0 for k in clipped}
    return {k: v / s for k, v in clipped.items()}
if __name__ == "__main__":
    demonstracja_emocjonalnego_collatza()