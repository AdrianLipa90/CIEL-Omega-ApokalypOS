"""Pipeline J-functional adapter with corrected R_H orientation.

This module exists so the large ``ciel_pipeline.py`` entrypoint can be wired
with a small import/hook instead of duplicating metric logic in multiple files.

R_H is a holonomic closure defect: lower is better.  It contributes to J as a
bounded defect score ``R_H / (N + R_H)``, never as raw ``1 - R_H``.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .rh_jfunctional import rh_defect_score


def _float_from(mapping: Mapping[str, Any], key: str, previous: Mapping[str, Any], default: float = 0.0) -> float:
    try:
        return float(mapping.get(key, previous.get(key, default)))
    except (TypeError, ValueError):
        return default


def compute_pipeline_j_functional(output: Mapping[str, Any], previous: Mapping[str, Any] | None = None) -> float:
    """Compute the pipeline fallback J-functional with bounded R_H defect.

    Parameters
    ----------
    output:
        Current pipeline output dict.  ``orbital_final`` is preferred as the
        source of raw R_H when present; otherwise ``output`` itself is used.
    previous:
        Previous persisted metrics dict used as fallback for legacy fields.

    Returns
    -------
    float
        Weighted J-functional value.  The result is not rounded so callers can
        decide their own persistence precision.
    """
    previous = previous or {}

    # Imported lazily to preserve the existing pipeline failure mode: if the
    # normalizer is unavailable, callers can catch and fall back to prior J.
    from .holonomic_normalizer import (  # noqa: PLC0415
        _I0_TOPOLOGICAL,
        _W_B_DEMO,
        _W_B_PLACEHOLDER,
        _W_B_SEAM,
        _W_D_AFFECT,
        _W_D_MEMORY,
        _W_D_REPO,
        _W_E_PHI,
        _W_P_DIST,
        _W_T_MEAN,
    )

    w_r_h = 0.9

    d_repo = _float_from(output, "closure_defect", previous)
    t_mean = _float_from(output, "mean_tension", previous)
    e_phi = _float_from(output, "closure_penalty", previous)
    d_aff = _float_from(output, "affect_decoherence", previous)
    d_mem = _float_from(output, "memory_decoherence", previous)
    b_seam = _float_from(output, "B_seam", previous)
    p_dist = _float_from(output, "P_dist", previous)
    b_demo = _float_from(output, "B_demo", previous)
    b_placeholder = _float_from(output, "B_placeholder", previous)

    orbital = output.get("orbital_final", output)
    if not isinstance(orbital, Mapping):
        orbital = output
    r_h_defect = rh_defect_score(orbital)

    return (
        _W_D_REPO * d_repo
        + _W_T_MEAN * t_mean
        + _W_E_PHI * e_phi
        + w_r_h * r_h_defect
        + _W_D_AFFECT * d_aff
        + _W_D_MEMORY * d_mem
        + _W_B_SEAM * b_seam
        + _W_P_DIST * p_dist
        + _W_B_PLACEHOLDER * b_placeholder
        + _W_B_DEMO * b_demo
        + _I0_TOPOLOGICAL * (d_repo + e_phi + r_h_defect + d_aff)
    )


__all__ = ["compute_pipeline_j_functional"]
