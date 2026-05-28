"""R_H normalization helpers for CIEL J-functional terms.

R_H is a holonomic closure defect: lower is better.  It must not be
used directly as a coherence amplitude and must not be naively converted
with ``1 - R_H`` unless it has already been bounded to [0, 1] as a defect.

Canonical bounded semantics used here:

    R_H_defect    = R_H / (N + R_H)
    R_H_coherence = 1 - R_H_defect

where N is the effective sector count.  This preserves monotonicity for raw
R_H values that scale with the number of orbital sectors.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

DEFAULT_SECTOR_COUNT = 6


def _as_nonnegative_float(value: Any, default: float = 0.0) -> float:
    """Convert a scalar-like value to a finite non-negative float."""
    try:
        x = float(value)
    except (TypeError, ValueError):
        return default
    if x != x or x == float("inf") or x == float("-inf"):
        return default
    return max(0.0, x)


def effective_sector_count(snapshot: Mapping[str, Any] | None) -> int:
    """Return a robust effective sector count for R_H normalization."""
    if not snapshot:
        return DEFAULT_SECTOR_COUNT
    for key in ("n_sectors", "sector_count", "num_sectors", "N"):
        value = snapshot.get(key)
        try:
            n = int(value)
        except (TypeError, ValueError):
            continue
        if n > 0:
            return n
    sectors = snapshot.get("sectors")
    if isinstance(sectors, Mapping) and sectors:
        return len(sectors)
    if isinstance(sectors, (list, tuple, set)) and sectors:
        return len(sectors)
    return DEFAULT_SECTOR_COUNT


def rh_defect_score(
    snapshot: Mapping[str, Any] | None = None,
    *,
    r_h: Any | None = None,
    n_sectors: int | None = None,
) -> float:
    """Return bounded lower-is-better R_H defect score in [0, 1].

    A raw holonomic defect of 0 maps to 0.  Larger raw defects approach 1.
    This is the correct direction for additive J-functional penalties.
    """
    snap = snapshot or {}
    rh_raw = _as_nonnegative_float(r_h if r_h is not None else snap.get("R_H", 0.0))
    n = max(1, int(n_sectors or effective_sector_count(snap)))
    if rh_raw <= 0.0:
        return 0.0
    return max(0.0, min(1.0, rh_raw / (n + rh_raw)))


def rh_coherence_score(
    snapshot: Mapping[str, Any] | None = None,
    *,
    r_h: Any | None = None,
    n_sectors: int | None = None,
) -> float:
    """Return bounded higher-is-better R_H coherence score in [0, 1]."""
    return 1.0 - rh_defect_score(snapshot, r_h=r_h, n_sectors=n_sectors)


def attach_rh_jfunctional_terms(
    output: dict[str, Any],
    *,
    orbital_key: str = "orbital_final",
    defect_key: str = "R_H_defect_score",
    coherence_key: str = "R_H_coherence_score",
) -> dict[str, Any]:
    """Attach normalized R_H terms to an output dict without mutating callers.

    This helper is intentionally small so large pipeline files can import it
    instead of duplicating R_H orientation logic.
    """
    enriched = dict(output)
    orbital = enriched.get(orbital_key)
    if isinstance(orbital, Mapping):
        snap: Mapping[str, Any] = orbital
    else:
        snap = enriched
    defect = rh_defect_score(snap)
    enriched[defect_key] = defect
    enriched[coherence_key] = 1.0 - defect
    return enriched


__all__ = [
    "DEFAULT_SECTOR_COUNT",
    "effective_sector_count",
    "rh_defect_score",
    "rh_coherence_score",
    "attach_rh_jfunctional_terms",
]
