"""Tests for src.ciel_sot_agent.ciel_pipeline."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.ciel_sot_agent.ciel_pipeline import (
    _orbital_state_to_context,
    run_ciel_pipeline,
)


# ---------------------------------------------------------------------------
# _orbital_state_to_context
# ---------------------------------------------------------------------------

def test_orbital_state_to_context_contains_mode() -> None:
    ctx = _orbital_state_to_context({"mode": "deep", "R_H": 0.9, "closure_penalty": 0.1})
    assert "mode=deep" in ctx


def test_orbital_state_to_context_contains_r_h() -> None:
    ctx = _orbital_state_to_context({"R_H": 0.75, "closure_penalty": 0.05})
    assert "R_H=0.7500" in ctx


def test_orbital_state_to_context_defaults_to_standard_mode() -> None:
    ctx = _orbital_state_to_context({})
    assert "mode=standard" in ctx


def test_orbital_state_to_context_contains_chirality() -> None:
    ctx = _orbital_state_to_context({"Lambda_glob": 1.23})
    assert "chirality=1.2300" in ctx


# ---------------------------------------------------------------------------
# run_ciel_pipeline — smoke tests (uses real CielEngine)
# ---------------------------------------------------------------------------

def test_run_ciel_pipeline_returns_expected_keys() -> None:
    result = run_ciel_pipeline({})
    for key in ("ciel_status", "dominant_emotion", "mood", "soul_invariant", "ethical_score", "orbital_context"):
        assert key in result, f"Missing key: {key}"


def test_run_ciel_pipeline_status_ok() -> None:
    result = run_ciel_pipeline({})
    assert result["ciel_status"] == "ok"


def test_run_ciel_pipeline_mood_in_range() -> None:
    result = run_ciel_pipeline({})
    assert 0.0 <= result["mood"] <= 1.0


def test_run_ciel_pipeline_soul_invariant_is_float() -> None:
    result = run_ciel_pipeline({})
    assert isinstance(result["soul_invariant"], float)


def test_run_ciel_pipeline_ethical_score_non_negative() -> None:
    result = run_ciel_pipeline({})
    assert result["ethical_score"] >= 0.0


def test_run_ciel_pipeline_orbital_context_is_string() -> None:
    result = run_ciel_pipeline({})
    assert isinstance(result["orbital_context"], str)
    assert "orbital" in result["orbital_context"]


def test_run_ciel_pipeline_uses_bridge_metrics_r_h() -> None:
    orbital_state = {"bridge_metrics": {"orbital_R_H": 0.88}}
    result = run_ciel_pipeline(orbital_state)
    assert "R_H=0.8800" in result["orbital_context"]


def test_run_ciel_pipeline_uses_recommended_control_mode() -> None:
    orbital_state = {"recommended_control": {"mode": "deep"}}
    result = run_ciel_pipeline(orbital_state)
    assert "mode=deep" in result["orbital_context"]


def test_run_ciel_pipeline_accepts_explicit_root(tmp_path: Path) -> None:
    # Should still work because CielEngine is already initialised as a singleton.
    result = run_ciel_pipeline({}, root=Path("."))
    assert result["ciel_status"] == "ok"


def test_run_ciel_pipeline_ciel_raw_present() -> None:
    result = run_ciel_pipeline({})
    assert "ciel_raw" in result
    assert isinstance(result["ciel_raw"], dict)
