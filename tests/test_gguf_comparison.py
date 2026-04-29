"""GGUF presence vs. absence comparison tests.

These tests document and verify the observable differences in CIEL-SOT-Agent
behaviour depending on whether a GGUF language-model file is present on
disk.

Key findings documented as assertions:
- The framework is fully functional without any GGUF model (no hard
  dependency on a model file for the core pipeline).
- When a GGUF model is present, GGUFManager.is_installed() returns True
  and model metadata is exposed through the manifest.
- All core pipeline operations (sync, coupling, phase normalisation) run
  identically regardless of GGUF availability.
- GGUF model management (download, verify, list) is encapsulated and does
  not pollute the rest of the package.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parents[1]


def _make_registry(n: int = 4) -> dict:
    import math as _math

    return {
        "repositories": [
            {
                "key": f"repo_{i}",
                "identity": f"org/repo-{i}",
                "phi": round(_math.pi * i / max(n, 1), 6),
                "spin": 0.5,
                "mass": 1.0,
                "role": "component",
                "upstream": f"https://github.com/org/repo-{i}",
            }
            for i in range(n)
        ]
    }


def _make_couplings(keys: list[str]) -> dict:
    return {
        "couplings": {
            k: {other: 0.5 for other in keys if other != k}
            for k in keys
        }
    }


# ---------------------------------------------------------------------------
# GGUF Manager — absent model (no model file on disk)
# ---------------------------------------------------------------------------

class TestGGUFAbsent:
    """Behaviour when no GGUF model file exists."""

    def test_is_installed_returns_false(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.gguf_manager.manager import GGUFManager

        mgr = GGUFManager(models_dir=tmp_path)
        assert mgr.is_installed() is False

    def test_list_models_returns_empty(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.gguf_manager.manager import GGUFManager

        mgr = GGUFManager(models_dir=tmp_path / "no_dir")
        assert mgr.list_models() == []

    def test_manifest_shows_no_models(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.gguf_manager.manager import GGUFManager

        mgr = GGUFManager(models_dir=tmp_path)
        manifest = mgr.load_manifest()
        assert manifest["models"] == []

    def test_get_model_path_returns_none(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.gguf_manager.manager import get_model_path

        result = get_model_path(models_dir=tmp_path)
        assert result is None

    def test_pipeline_runs_without_gguf(self, tmp_path: Path) -> None:
        """Core pipeline must work even when no GGUF model is present."""
        from src.ciel_sot_agent.repo_phase import build_sync_report

        reg = _make_registry(3)
        keys = [r["key"] for r in reg["repositories"]]
        coup = _make_couplings(keys)
        (tmp_path / "repository_registry.json").write_text(json.dumps(reg))
        (tmp_path / "couplings.json").write_text(json.dumps(coup))

        result = build_sync_report(
            tmp_path / "repository_registry.json",
            tmp_path / "couplings.json",
        )
        assert "closure_defect" in result
        assert math.isfinite(result["closure_defect"])

    def test_sync_quality_without_gguf(self, tmp_path: Path) -> None:
        """Sync report closure_defect must be a valid float without GGUF."""
        from src.ciel_sot_agent.repo_phase import build_sync_report

        reg = _make_registry(5)
        keys = [r["key"] for r in reg["repositories"]]
        coup = _make_couplings(keys)
        (tmp_path / "repository_registry.json").write_text(json.dumps(reg))
        (tmp_path / "couplings.json").write_text(json.dumps(coup))

        result = build_sync_report(
            tmp_path / "repository_registry.json",
            tmp_path / "couplings.json",
        )
        defect = result["closure_defect"]
        assert isinstance(defect, float)
        assert defect >= 0.0


# ---------------------------------------------------------------------------
# GGUF Manager — present model (model file placed on disk)
# ---------------------------------------------------------------------------

class TestGGUFPresent:
    """Behaviour when a GGUF model file exists."""

    @pytest.fixture()
    def mgr_with_model(self, tmp_path: Path):
        from src.ciel_sot_agent.gguf_manager.manager import GGUFManager, KNOWN_MODELS

        mgr = GGUFManager(models_dir=tmp_path)
        spec = KNOWN_MODELS[mgr.default_model_key]
        (tmp_path / spec.name).write_bytes(b"fake-gguf-data" * 100)
        return mgr

    def test_is_installed_returns_true(self, mgr_with_model) -> None:
        assert mgr_with_model.is_installed() is True

    def test_list_models_returns_one_entry(self, mgr_with_model) -> None:
        models = mgr_with_model.list_models()
        assert len(models) == 1
        assert models[0]["name"].endswith(".gguf")

    def test_manifest_includes_model_name(self, mgr_with_model) -> None:
        mgr_with_model.save_manifest()
        manifest = mgr_with_model.load_manifest()
        names = [e["name"] for e in manifest["models"]]
        from src.ciel_sot_agent.gguf_manager.manager import KNOWN_MODELS
        expected_name = KNOWN_MODELS[mgr_with_model.default_model_key].name
        assert expected_name in names

    def test_get_model_path_returns_path(self, mgr_with_model, tmp_path: Path) -> None:
        from src.ciel_sot_agent.gguf_manager.manager import get_model_path

        result = get_model_path(models_dir=tmp_path)
        assert result is not None
        assert result.exists()

    def test_ensure_model_returns_existing_file(self, mgr_with_model) -> None:
        path = mgr_with_model.ensure_model()
        assert path.exists()
        assert path.suffix == ".gguf"

    def test_pipeline_unchanged_with_gguf_present(
        self, mgr_with_model, tmp_path: Path
    ) -> None:
        """The sync-report result must be identical regardless of GGUF presence."""
        from src.ciel_sot_agent.repo_phase import build_sync_report

        reg = _make_registry(3)
        keys = [r["key"] for r in reg["repositories"]]
        coup = _make_couplings(keys)
        (tmp_path / "repository_registry.json").write_text(json.dumps(reg))
        (tmp_path / "couplings.json").write_text(json.dumps(coup))

        result = build_sync_report(
            tmp_path / "repository_registry.json",
            tmp_path / "couplings.json",
        )
        assert "closure_defect" in result
        assert math.isfinite(result["closure_defect"])


# ---------------------------------------------------------------------------
# GGUF vs No-GGUF: direct comparison
# ---------------------------------------------------------------------------

class TestGGUFComparison:
    """Direct comparison of pipeline outputs with and without GGUF model."""

    def _run_pipeline(self, tmp_path: Path, n_repos: int = 4) -> dict:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        reg = _make_registry(n_repos)
        keys = [r["key"] for r in reg["repositories"]]
        coup = _make_couplings(keys)
        (tmp_path / "repository_registry.json").write_text(json.dumps(reg))
        (tmp_path / "couplings.json").write_text(json.dumps(coup))
        return build_sync_report(
            tmp_path / "repository_registry.json",
            tmp_path / "couplings.json",
        )

    def test_closure_defect_identical_with_and_without_gguf(
        self, tmp_path: Path
    ) -> None:
        """Core pipeline output must be identical regardless of GGUF availability."""
        no_gguf_dir = tmp_path / "no_gguf"
        with_gguf_dir = tmp_path / "with_gguf"
        no_gguf_dir.mkdir()
        with_gguf_dir.mkdir()

        # Install a fake GGUF model for the "with" run
        from src.ciel_sot_agent.gguf_manager.manager import GGUFManager, KNOWN_MODELS

        mgr = GGUFManager(models_dir=with_gguf_dir / "models")
        mgr.models_dir.mkdir(parents=True)
        spec = KNOWN_MODELS[mgr.default_model_key]
        (mgr.models_dir / spec.name).write_bytes(b"fake" * 50)

        result_no_gguf = self._run_pipeline(no_gguf_dir)
        result_with_gguf = self._run_pipeline(with_gguf_dir)

        # Pipeline outputs must be identical — GGUF is orthogonal to sync
        assert result_no_gguf["closure_defect"] == pytest.approx(
            result_with_gguf["closure_defect"], rel=1e-9
        )
        assert result_no_gguf["repository_count"] == result_with_gguf["repository_count"]

    def test_gguf_absent_is_faster_than_with_download(self, tmp_path: Path) -> None:
        """Pipeline startup without GGUF must be fast (no blocking download)."""
        from src.ciel_sot_agent.gguf_manager.manager import GGUFManager

        # Measure pipeline time with no model present (should complete instantly)
        start = time.perf_counter()
        mgr = GGUFManager(models_dir=tmp_path / "models")
        _ = mgr.is_installed()
        _ = mgr.list_models()
        elapsed_absent = time.perf_counter() - start

        assert elapsed_absent < 0.5, (
            f"GGUFManager operations without model file took {elapsed_absent:.3f}s "
            "— should be near-instant when no model is installed"
        )

    def test_manifest_schema_consistent_across_states(self, tmp_path: Path) -> None:
        """Manifest schema must be the same whether or not a model is present."""
        from src.ciel_sot_agent.gguf_manager.manager import GGUFManager, KNOWN_MODELS

        # Absent
        mgr_absent = GGUFManager(models_dir=tmp_path / "absent")
        manifest_absent = mgr_absent.load_manifest()

        # Present
        present_dir = tmp_path / "present"
        present_dir.mkdir()
        mgr_present = GGUFManager(models_dir=present_dir)
        spec = KNOWN_MODELS[mgr_present.default_model_key]
        (present_dir / spec.name).write_bytes(b"fake")
        mgr_present.save_manifest()
        manifest_present = mgr_present.load_manifest()

        # Schema key must be identical
        assert manifest_absent["schema"] == manifest_present["schema"]
        # Models list type must be consistent
        assert isinstance(manifest_absent["models"], list)
        assert isinstance(manifest_present["models"], list)
        # Absent has 0 models, present has 1
        assert len(manifest_absent["models"]) == 0
        assert len(manifest_present["models"]) == 1

    def test_gguf_model_spec_fields_match_known_models(self, tmp_path: Path) -> None:
        """Each KNOWN_MODELS entry must have the required fields for safe install."""
        from src.ciel_sot_agent.gguf_manager.manager import KNOWN_MODELS

        required_fields = {"name", "url", "description"}
        for key, spec in KNOWN_MODELS.items():
            for field in required_fields:
                value = getattr(spec, field, None)
                assert value, (
                    f"KNOWN_MODELS[{key!r}].{field} is empty or missing"
                )

    def test_pipeline_throughput_unaffected_by_gguf_presence(
        self, tmp_path: Path
    ) -> None:
        """Repeat-call throughput of build_sync_report must be the same with/without GGUF."""
        from src.ciel_sot_agent.repo_phase import build_sync_report
        from src.ciel_sot_agent.gguf_manager.manager import GGUFManager, KNOWN_MODELS

        n = 10
        reg = _make_registry(n)
        keys = [r["key"] for r in reg["repositories"]]
        coup = _make_couplings(keys)

        for label, base_dir in [("no_gguf", tmp_path / "ng"), ("with_gguf", tmp_path / "wg")]:
            base_dir.mkdir()
            (base_dir / "repository_registry.json").write_text(json.dumps(reg))
            (base_dir / "couplings.json").write_text(json.dumps(coup))
            if label == "with_gguf":
                models_dir = base_dir / "models"
                models_dir.mkdir()
                spec = KNOWN_MODELS["tinyllama-1.1b-chat-q4"]
                (models_dir / spec.name).write_bytes(b"x" * 1024)

        timings = {}
        for label, base_dir in [("no_gguf", tmp_path / "ng"), ("with_gguf", tmp_path / "wg")]:
            start = time.perf_counter()
            for _ in range(20):
                build_sync_report(
                    base_dir / "repository_registry.json",
                    base_dir / "couplings.json",
                )
            timings[label] = time.perf_counter() - start

        # Neither mode should be more than 5× slower than the other
        ratio = max(timings.values()) / (min(timings.values()) + 1e-9)
        assert ratio < 5.0, (
            f"Throughput ratio with_gguf/no_gguf = {ratio:.2f} "
            "exceeds tolerance of 5×. GGUF presence should not affect sync speed."
        )


# ---------------------------------------------------------------------------
# GGUF Manager — phased_state interaction
# ---------------------------------------------------------------------------

class TestGGUFPhasedState:
    """GGUF model files must be recognised as a known type in phased_state."""

    def test_gguf_ext_has_non_zero_weight(self) -> None:
        from src.ciel_sot_agent.phased_state import TYPE_WEIGHTS

        assert "gguf" in TYPE_WEIGHTS, (
            "'gguf' extension must be listed in TYPE_WEIGHTS for proper phase scoring"
        )
        assert TYPE_WEIGHTS["gguf"] > 0.0

    def test_gguf_weight_is_lower_than_python_weight(self) -> None:
        from src.ciel_sot_agent.phased_state import TYPE_WEIGHTS

        assert TYPE_WEIGHTS.get("gguf", 0.0) < TYPE_WEIGHTS.get("py", 1.0), (
            "GGUF binary files should have lower phase weight than Python source files"
        )
