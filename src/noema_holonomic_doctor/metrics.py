"""Phase-style diagnostic metrics for NOEMA Holonomic Doctor."""
from __future__ import annotations

import math
from .manifest import ManifestEntry


def epsilon_neutrino(file_count: int, total_bytes: int) -> float:
    """Derive a tiny local tolerance from machine precision and repo scale."""
    scale = max(1.0, math.log2(max(2, file_count + total_bytes)))
    return math.ulp(1.0) * scale


def d_lambda(manifest: list[ManifestEntry]) -> float:
    """Slow global drift baseline proxy from manifest occupancy.

    Without a previous cycle this is a baseline density, not a historical delta.
    """
    if not manifest:
        return 0.0
    total = sum(entry.size for entry in manifest)
    nonzero = sum(1 for entry in manifest if entry.size > 0)
    return nonzero / max(1.0, total)


def euler_berry_phase(manifest_sha256: str) -> float:
    """Map a manifest hash to a phase angle in [0, 2π)."""
    seed = int(manifest_sha256[:16], 16)
    return (seed / float(0xFFFFFFFFFFFFFFFF)) * 2.0 * math.pi


def closure_error(phase: float) -> float:
    """Normalized distance of exp(i*phase) from Euler closure."""
    return abs(math.atan2(math.sin(phase), math.cos(phase))) / math.pi


def doctor_cost(severity_counts: dict[str, int], closure: float, d_lam: float, eps_nu: float) -> float:
    weights = {"critical": 5.0, "high": 3.0, "medium": 1.5, "low": 0.5}
    return sum(weights.get(k, 1.0) * v for k, v in severity_counts.items()) + closure + d_lam - eps_nu


__all__ = ["closure_error", "d_lambda", "doctor_cost", "epsilon_neutrino", "euler_berry_phase"]
