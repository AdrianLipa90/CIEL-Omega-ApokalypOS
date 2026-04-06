"""CIEL pipeline adapter — routes orbital state through the CIEL/Ω engine.

Provides ``run_ciel_pipeline`` which:
  1. Adds the CIEL/Ω omega root to ``sys.path`` (idempotent).
  2. Instantiates a fresh ``CielEngine`` per call.
  3. Encodes the orbital state as a context string.
  4. Runs ``CielEngine.step()`` → returns the enriched result.

This is the bottom-to-top integration point that wires the orbital physics
layer (``integration/Orbital/main/``) up through the full CIEL consciousness
pipeline (``integration/Orbital/main/data/source/CIEL_OMEGA_COMPLETE_SYSTEM``).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .paths import resolve_project_root

_CIEL_OMEGA_SUBPATH = (
    Path("integration")
    / "Orbital"
    / "main"
    / "data"
    / "source"
    / "CIEL_OMEGA_COMPLETE_SYSTEM"
)


def _ensure_ciel_omega_on_path(root: Path) -> None:
    omega_root = str((root / _CIEL_OMEGA_SUBPATH).resolve())
    if omega_root not in sys.path:
        sys.path.insert(0, omega_root)


def _get_engine(root: Path) -> Any:
    """Return a fresh CielEngine instance.

    A fresh instance is used on every call because the CIEL/Ω memory subsystem
    contains a bounded deque that fills during initialisation; reusing the same
    engine across unrelated pipeline calls would cause the deque to overflow.
    """
    _ensure_ciel_omega_on_path(root)
    from ciel_omega.ciel.engine import CielEngine  # noqa: PLC0415

    return CielEngine()


def _orbital_state_to_context(orbital_state: dict[str, Any]) -> str:
    """Encode key orbital scalars as a compact context string for the engine."""
    r_h = orbital_state.get("R_H", 0.0)
    closure = orbital_state.get("closure_penalty", 0.0)
    chirality = orbital_state.get("Lambda_glob", 0.0)
    mode = orbital_state.get("mode", "standard")
    return (
        f"orbital|mode={mode}|R_H={r_h:.4f}"
        f"|closure={closure:.4f}|chirality={chirality:.4f}"
    )


def run_ciel_pipeline(
    orbital_state: dict[str, Any],
    context: str = "orbital",
    *,
    root: Path | str | None = None,
) -> dict[str, Any]:
    """Run orbital state through the CIEL/Ω pipeline.

    Parameters
    ----------
    orbital_state:
        Dict produced by ``orbital_bridge.build_orbital_bridge`` (or any dict
        that contains at least the bridge_metrics / state_manifest sub-keys).
    context:
        Logical context label forwarded to ``CielEngine.step``.
    root:
        Project root path.  Resolved automatically when *None*.

    Returns
    -------
    dict with keys:
        ``ciel_status``, ``dominant_emotion``, ``mood``, ``soul_invariant``,
        ``ethical_score``, ``orbital_context``, ``ciel_raw``
    """
    if root is None:
        root = resolve_project_root(Path(__file__))
    root = Path(root)

    engine = _get_engine(root)

    # Build a compact text encoding from orbital metrics so that CielEngine
    # receives meaningful semantic input grounded in the system's geometry.
    bridge_metrics = orbital_state.get("bridge_metrics", {})
    state_manifest = orbital_state.get("state_manifest", {})
    merged: dict[str, Any] = {
        "R_H": bridge_metrics.get("orbital_R_H", state_manifest.get("R_H", 0.0)),
        "closure_penalty": bridge_metrics.get(
            "orbital_closure_penalty", state_manifest.get("closure_penalty", 0.0)
        ),
        "Lambda_glob": bridge_metrics.get(
            "topological_charge_global", state_manifest.get("Lambda_glob", 0.0)
        ),
        "mode": orbital_state.get("recommended_control", {}).get("mode", "standard"),
    }

    orbital_context = _orbital_state_to_context(merged)
    full_context = f"{context}|{orbital_context}"

    raw = engine.step(orbital_context, context=full_context)

    return {
        "ciel_status": raw.get("status", "ok"),
        "dominant_emotion": raw.get("dominant_emotion"),
        "mood": float(raw.get("mood", 0.0)),
        "soul_invariant": float(raw.get("soul_invariant", 0.0)),
        "ethical_score": float(raw.get("ethical_score", 0.0)),
        "orbital_context": orbital_context,
        "ciel_raw": raw,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a minimal orbital state through the CIEL/Ω pipeline."
    )
    parser.add_argument(
        "--orbital-json",
        default=None,
        help="Path to an orbital bridge JSON report (optional; uses empty state if absent).",
    )
    args = parser.parse_args()

    orbital_state: dict[str, Any] = {}
    if args.orbital_json:
        with open(args.orbital_json, encoding="utf-8") as fh:
            orbital_state = json.load(fh)

    result = run_ciel_pipeline(orbital_state)
    print(json.dumps({k: v for k, v in result.items() if k != "ciel_raw"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
