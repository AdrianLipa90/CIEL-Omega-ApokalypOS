from __future__ import annotations

import math
from typing import Sequence


def euclidean_distance(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("vectors must have equal length")
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def grammar_curvature_seed(vector: Sequence[float]) -> float:
    if not vector:
        return 0.0
    mean = sum(vector) / len(vector)
    return math.sqrt(sum((x - mean) ** 2 for x in vector) / len(vector))


def cross_language_compatible(distance: float, epsilon_cross: float = 0.75) -> bool:
    return distance < epsilon_cross
