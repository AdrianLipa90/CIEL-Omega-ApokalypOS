from __future__ import annotations

from pathlib import Path

from src.ciel_sot_agent import state_db


def test_save_bridge_snapshot_persists_lingo_metrics(tmp_path: Path) -> None:
    db_path = tmp_path / "ciel_state.db"
    old_db_path = state_db._DB_PATH
    old_initialized = set(state_db._schema_initialized)
    try:
        state_db._DB_PATH = db_path
        state_db._schema_initialized.clear()

        summary = {
            "schema": "test",
            "memory_projection": {
                "projection_error": 0.12,
                "projection_confidence": 0.88,
                "projection_residual": 0.12,
                "j_noema": 0.34,
            },
        }
        runtime_gating = {}
        health_manifest = {"system_health": 0.74, "closure_penalty": 0.22}
        state_manifest = {"coherence_index": 0.81}
        ciel_pipe = {
            "cycle_index": 3,
            "identity_phase": 0.42,
            "ethical_score": 0.9,
            "mood": 0.1,
            "dominant_emotion": "calm",
            "J_functional": 0.2,
            "J_memory": 0.12,
            "j_noema": 0.34,
            "J_euler": 0.05,
            "J_total": 0.18,
            "euler_residual": 0.05,
            "lingo_frame": {
                "summary": "CIELingo|concepts=bridge, memory|operators=through|deictic=Now:relative_anchor|unresolved=Now|factual=yes|noema_conf=0.710",
                "concept_tokens": ["bridge", "memory"],
                "operator_tokens": ["through"],
                "unresolved": ["Now"],
                "phase_projection": {
                    "target_phase": 0.5,
                    "target_phase_shift": 0.1,
                    "phase_confidence": 0.71,
                },
                "tau_bridge": {
                    "tau_gradient_mean": 0.33,
                    "imaginal_drive": 0.44,
                    "tau_curvature_rms": 0.19,
                },
                "noema_route": {
                    "confidence": 0.71,
                    "factual_validation_required": True,
                },
            },
            "jokeheal_mnemonic_atlas": {
                "mnemonic_pressure": 0.52,
                "symbolic_pull": 0.37,
                "recurrence_pressure": 0.61,
            },
        }

        state_db.save_bridge_snapshot(summary, runtime_gating, health_manifest, state_manifest, ciel_pipe)
        row = state_db.load_metrics_history(1)[0]

        assert row["lingo_summary"].startswith("CIELingo|")
        assert row["lingo_concept_count"] == 2
        assert row["lingo_operator_count"] == 1
        assert row["lingo_unresolved_count"] == 1
        assert row["lingo_phase_target"] == 0.5
        assert row["lingo_phase_shift"] == 0.1
        assert row["lingo_phase_confidence"] == 0.71
        assert row["lingo_noema_confidence"] == 0.71
        assert row["lingo_tau_gradient_mean"] == 0.33
        assert row["lingo_imaginal_drive"] == 0.44
        assert row["lingo_tau_curvature_rms"] == 0.19
        assert row["lingo_factual_validation_required"] == 1
        assert row["jokeheal_mnemonic_pressure"] == 0.52
        assert row["jokeheal_symbolic_pull"] == 0.37
        assert row["jokeheal_recurrence_pressure"] == 0.61
    finally:
        state_db._DB_PATH = old_db_path
        state_db._schema_initialized.clear()
        state_db._schema_initialized.update(old_initialized)
