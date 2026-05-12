"""Minimal CIEL-LNS/Ω reference metrics."""
from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from typing import Iterable, Mapping


def semantic_mass(features: Mapping[str, float], weights: Mapping[str, float]) -> float:
    """Compute normalized semantic mass from feature and weight dictionaries."""
    positive = (
        weights.get("frequency", 0.0) * features.get("frequency", 0.0)
        + weights.get("relation_degree", 0.0) * features.get("relation_degree", 0.0)
        + weights.get("provenance_strength", 0.0) * features.get("provenance_strength", 0.0)
        + weights.get("memory_persistence", 0.0) * features.get("memory_persistence", 0.0)
        + weights.get("coherence", 0.0) * features.get("coherence", 0.0)
        + weights.get("affective_charge", 0.0) * features.get("affective_charge", 0.0)
        + weights.get("causal_power", 0.0) * features.get("causal_power", 0.0)
    )
    penalty = weights.get("contradiction_penalty", 0.0) * features.get("contradiction_penalty", 0.0)
    return max(0.0, min(1.0, positive - penalty))


def euler_antonym_loss(phase_a: float, phase_b: float) -> float:
    """Loss is zero when two states are opposite-phase."""
    return abs(cmath.exp(1j * (phase_a - phase_b)) + 1) ** 2


def synonym_phase_loss(phase_a: float, phase_b: float) -> float:
    """Loss is zero when two states are same-phase."""
    return abs(cmath.exp(1j * (phase_a - phase_b)) - 1) ** 2


def consensus_holonomy(phases: Iterable[float], weights: Iterable[float] | None = None) -> tuple[complex, float]:
    phases = list(phases)
    if weights is None:
        weights = [1.0] * len(phases)
    weights = list(weights)
    z = sum(weights) or 1.0
    hol = sum(w * cmath.exp(1j * p) for p, w in zip(phases, weights)) / z
    return hol, abs(hol) ** 2


def semantic_energy(mass: float, velocity: float, attractor_mass: float, radius: float, coupling: float = 1.0, eps: float = 1e-9) -> float:
    """Kepler-like semantic energy."""
    kinetic = 0.5 * mass * velocity * velocity
    potential = -coupling * attractor_mass * mass / (radius + eps)
    return kinetic + potential


def eccentricity(energy: float, angular_momentum: float, mass: float, attractor_mass: float, coupling: float = 1.0) -> float:
    """Kepler-like eccentricity with safe clipping."""
    denom = mass * (coupling * attractor_mass * mass) ** 2
    if denom <= 0:
        return float("inf")
    value = 1.0 + (2.0 * energy * angular_momentum * angular_momentum) / denom
    return math.sqrt(max(0.0, value))
