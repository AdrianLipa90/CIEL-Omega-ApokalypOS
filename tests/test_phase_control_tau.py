from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"
if str(PKG) not in sys.path:
    sys.path.insert(0, str(PKG))

from ciel_omega.orbital.phase_control import build_state_manifest, recommend_control


def test_recommend_control_uses_tau_bridge_as_phase_bias() -> None:
    baseline = {
        "R_H": 0.72,
        "closure_penalty": 0.14,
        "coherent_fraction": 0.38,
        "eba_defect_mean": 0.12,
        "euler_bridge_closure_score": 0.61,
        "euler_bridge_target_phase": 1.0,
        "nonlocal_phi_berry_mean": 0.4,
        "lingo_phase_target": 1.0,
        "lingo_phase_projection": {"phase_confidence": 0.75},
    }
    tau_shifted = {
        **baseline,
        "lingo_tau_bridge": {
            "tau_gradient_mean": 0.8,
            "imaginal_drive": 0.9,
            "tau_curvature_rms": 0.2,
        },
        "lingo_tau_gradient_mean": 0.8,
        "lingo_imaginal_drive": 0.9,
        "lingo_tau_curvature_rms": 0.2,
    }

    base = recommend_control(baseline)
    biased = recommend_control(tau_shifted)

    assert biased["target_phase_shift"] != base["target_phase_shift"]
    assert biased["phase_lock_enable"] is True
    assert biased["writeback_gate"] in (True, False)


def test_build_state_manifest_exposes_tau_signals() -> None:
    manifest = build_state_manifest(
        {
            "R_H": 0.66,
            "closure_penalty": 0.11,
            "euler_bridge_target_phase": 0.5,
            "lingo_phase_target": 0.5,
            "lingo_phase_projection": {"phase_confidence": 0.71},
            "lingo_frame": {
                "summary": "CIELingo|concepts=bridge, memory|operators=through|deictic=Now:relative_anchor|unresolved=Now|factual=yes|noema_conf=0.710",
                "concept_tokens": ["bridge", "memory"],
                "operator_tokens": ["through"],
                "unresolved": ["Now"],
                "noema_route": {"confidence": 0.71, "factual_validation_required": True},
            },
            "lingo_tau_gradient_mean": 0.33,
            "lingo_imaginal_drive": 0.44,
            "lingo_tau_curvature_rms": 0.19,
        }
    )

    assert manifest["lingo_tau_gradient_mean"] == 0.33
    assert manifest["lingo_imaginal_drive"] == 0.44
    assert manifest["lingo_tau_curvature_rms"] == 0.19
    assert manifest["lingo_noema_confidence"] == 0.71
    assert manifest["lingo_summary"].startswith("CIELingo|")
    assert manifest["lingo_concept_count"] == 2
    assert manifest["lingo_operator_count"] == 1
    assert manifest["lingo_unresolved_count"] == 1
    assert manifest["lingo_factual_validation_required"] == 1
