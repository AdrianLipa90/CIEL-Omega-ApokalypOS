"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

CQCL program container and NLP/hashing helpers.

Source: extemot.py (helpers + CQCL_Program dataclass)
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Sentiment / hashing helpers
# ---------------------------------------------------------------------------

_POS = {
    "love", "peace", "harmony", "cooperation", "joy", "trust", "compassion",
    "miłość", "pokój", "harmonia", "współpraca", "radość", "zaufanie", "współczucie",
}
_NEG = {
    "fear", "anger", "war", "conflict", "hate", "despair",
    "strach", "gniew", "wojna", "konflikt", "nienawiść", "desperacja", "lęk", "smutek",
}


def stable_hash(text: str) -> int:
    """Deterministic 64-bit hash via BLAKE2b."""
    return int(hashlib.blake2b(text.encode("utf-8"), digest_size=8).hexdigest(), 16)


def sentiment(text: str) -> float:
    """Simple keyword-counting sentiment ∈ [0, 1]."""
    t = text.lower()
    p = sum(t.count(w) for w in _POS)
    n = sum(t.count(w) for w in _NEG)
    tot = p + n
    return p / tot if tot else 0.5


def lexical_diversity(text: str) -> float:
    ws = re.findall(r"[A-Za-zÀ-ž0-9]+", text.lower())
    return len(set(ws)) / max(1, len(ws)) if ws else 0.0


def normalize_profile(d: Dict[str, float]) -> Dict[str, float]:
    clipped = {k: max(0.0, float(v)) for k, v in d.items()}
    s = sum(clipped.values())
    if s <= 1e-12:
        return {k: 0.0 for k in clipped}
    return {k: v / s for k, v in clipped.items()}


# ---------------------------------------------------------------------------
# CQCL Program container
# ---------------------------------------------------------------------------

@dataclass
class CQCL_Program:
    """Lightweight container for a compiled intention program."""

    intent: str
    semantic_tree: Dict[str, Any]
    semantic_hash: int
    quantum_variables: Dict[str, float]
    input_data: Optional[float] = None
    computation_path: List[int] = field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)


__all__ = [
    "CQCL_Program",
    "stable_hash",
    "sentiment",
    "lexical_diversity",
    "normalize_profile",
]
