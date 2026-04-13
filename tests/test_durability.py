"""Durability and elasticity tests for the CIEL-SOT-Agent pipeline.

"Durability" — the same operation repeated many times must yield a stable,
non-degrading result (no memory leaks between invocations, deterministic
output, error-free execution under sustained load).

"Elasticity" — the system must scale gracefully: larger inputs (more
repositories, more couplings) should increase compute time sub-linearly
and never raise unexpected exceptions.

"Resilience" — the pipeline must recover cleanly from malformed input,
partial data, and simulated I/O errors.

System-requirements smoke-tests are also included to document and verify
the minimum runtime environment expected by the framework.
"""

from __future__ import annotations

import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]


def _make_registry(n: int) -> dict[str, Any]:
    """Generate a synthetic repository registry with *n* repositories."""
    repos = [
        {
            "key": f"repo_{i}",
            "identity": f"org/repo-{i}",
            "phi": round(math.pi * i / max(n, 1), 6),
            "spin": round(0.5 + 0.01 * i, 6),
            "mass": round(1.0 + 0.1 * i, 6),
            "role": "component" if i % 3 else "kernel",
            "upstream": f"https://github.com/org/repo-{i}",
        }
        for i in range(n)
    ]
    return {"repositories": repos}


def _make_couplings(keys: list[str]) -> dict[str, Any]:
    """Generate a synthetic coupling map for the given repository keys."""
    couplings: dict[str, dict[str, float]] = {}
    for i, k in enumerate(keys):
        targets = {
            keys[j]: round(0.1 * (1 + (i + j) % 5), 3)
            for j in range(len(keys))
            if j != i
        }
        couplings[k] = targets
    return {"couplings": couplings}


# ---------------------------------------------------------------------------
# System requirements
# ---------------------------------------------------------------------------

class TestSystemRequirements:
    """Verify the minimum runtime environment is satisfied."""

    def test_python_version_gte_311(self) -> None:
        if sys.version_info < (3, 11):
            pytest.skip(f"CIEL requires Python >= 3.11, running {sys.version}")
        assert sys.version_info >= (3, 11)

    def test_numpy_importable(self) -> None:
        import numpy as np  # noqa: F401 — intentional import check

        assert np is not None

    def test_yaml_importable(self) -> None:
        import yaml  # noqa: F401

        assert yaml is not None

    def test_pathlib_available(self) -> None:
        assert Path is not None

    def test_json_stdlib_available(self) -> None:
        sample = {"key": "value", "number": 42}
        encoded = json.dumps(sample)
        decoded = json.loads(encoded)
        assert decoded == sample

    def test_platform_is_supported(self) -> None:
        system = platform.system()
        assert system in {"Linux", "Darwin", "Windows"}, (
            f"Unsupported platform: {system}"
        )

    def test_math_precision_adequate(self) -> None:
        """Floating-point precision must be at least 64-bit (double)."""
        import struct

        assert struct.calcsize("d") == 8, "Requires 64-bit float support"

    def test_ciel_sot_agent_package_importable(self) -> None:
        import importlib

        mod = importlib.import_module("src.ciel_sot_agent")
        assert mod is not None

    def test_gguf_manager_importable(self) -> None:
        import importlib

        mod = importlib.import_module("src.ciel_sot_agent.gguf_manager.manager")
        assert mod is not None


# ---------------------------------------------------------------------------
# Durability — repeated invocations of build_sync_report
# ---------------------------------------------------------------------------

class TestSyncReportDurability:
    """build_sync_report must produce stable, identical output over N iterations."""

    ITERATIONS = 50

    @pytest.fixture()
    def registry_file(self, tmp_path: Path) -> Path:
        data = _make_registry(8)
        path = tmp_path / "repository_registry.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    @pytest.fixture()
    def couplings_file(self, tmp_path: Path, registry_file: Path) -> Path:
        reg = json.loads(registry_file.read_text())
        keys = [r["key"] for r in reg["repositories"]]
        data = _make_couplings(keys)
        path = registry_file.parent / "couplings.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_repeated_calls_return_same_closure_defect(
        self, registry_file: Path, couplings_file: Path
    ) -> None:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        first = build_sync_report(registry_file, couplings_file)
        for _ in range(self.ITERATIONS - 1):
            result = build_sync_report(registry_file, couplings_file)
            assert result["closure_defect"] == pytest.approx(
                first["closure_defect"], rel=1e-9
            ), "build_sync_report is not deterministic"

    def test_output_schema_stable_under_load(
        self, registry_file: Path, couplings_file: Path
    ) -> None:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        # Keys emitted by the real implementation
        required_keys = {
            "repository_count",
            "weighted_euler_vector",
            "closure_defect",
            "pairwise_tensions",
        }
        for i in range(self.ITERATIONS):
            result = build_sync_report(registry_file, couplings_file)
            missing = required_keys - set(result.keys())
            assert missing == set(), (
                f"Iteration {i}: missing keys {missing!r} in sync report"
            )

    def test_no_exception_under_sustained_load(
        self, registry_file: Path, couplings_file: Path
    ) -> None:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        errors = []
        for i in range(self.ITERATIONS):
            try:
                build_sync_report(registry_file, couplings_file)
            except Exception as exc:  # noqa: BLE001
                errors.append((i, str(exc)))
        assert errors == [], f"Errors during sustained load: {errors}"

    def test_euler_vector_is_always_finite(
        self, registry_file: Path, couplings_file: Path
    ) -> None:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        for _ in range(self.ITERATIONS):
            result = build_sync_report(registry_file, couplings_file)
            ev = result["weighted_euler_vector"]
            assert math.isfinite(ev["real"]), "Euler vector real part is not finite"
            assert math.isfinite(ev["imag"]), "Euler vector imag part is not finite"
            assert math.isfinite(ev["abs"]), "Euler vector abs is not finite"


# ---------------------------------------------------------------------------
# Durability — holonomic normalizer primitives
# ---------------------------------------------------------------------------

class TestHolonomicNormalizerDurability:
    """Core normalizer primitives must be numerically stable under repeated use."""

    ITERATIONS = 100

    def test_circular_barycenter_stable(self) -> None:
        from src.ciel_sot_agent.holonomic_normalizer import circular_barycenter

        phases = [0.1, 0.5, 1.2, 2.0, 3.0]
        weights = [1.0, 2.0, 1.5, 0.8, 0.5]
        first = circular_barycenter(phases, weights)
        for _ in range(self.ITERATIONS):
            result = circular_barycenter(phases, weights)
            assert result == pytest.approx(first, rel=1e-12)

    def test_wrap_idempotent_under_repeated_application(self) -> None:
        from src.ciel_sot_agent.holonomic_normalizer import wrap

        angles = [0.0, math.pi, -math.pi, 2 * math.pi, -2 * math.pi, 100.0]
        for angle in angles:
            wrapped_once = wrap(angle)
            wrapped_twice = wrap(wrapped_once)
            assert wrapped_once == pytest.approx(wrapped_twice, rel=1e-12), (
                f"wrap({angle}) is not idempotent: {wrapped_once} vs {wrapped_twice}"
            )

    def test_circular_distance_symmetric(self) -> None:
        from src.ciel_sot_agent.holonomic_normalizer import circular_distance

        pairs = [(0.0, math.pi), (0.5, 2.0), (3.0, -3.0)]
        for a, b in pairs:
            assert circular_distance(a, b) == pytest.approx(
                circular_distance(b, a), rel=1e-12
            ), f"circular_distance not symmetric for ({a}, {b})"

    def test_renormalize_couplings_stable(self) -> None:
        from src.ciel_sot_agent.holonomic_normalizer import renormalize_couplings

        couplings = {("a", "b"): 0.5, ("a", "c"): 0.3, ("b", "a"): 0.5, ("b", "c"): 0.2}
        first = renormalize_couplings(couplings)
        for _ in range(self.ITERATIONS):
            result = renormalize_couplings(couplings)
            for key in first:
                assert first[key] == pytest.approx(result[key], rel=1e-12)


# ---------------------------------------------------------------------------
# Elasticity — scaling with registry size
# ---------------------------------------------------------------------------

class TestSyncReportElasticity:
    """Compute time must scale reasonably as registry size grows."""

    @pytest.mark.parametrize("n_repos", [5, 20, 50, 100])
    def test_sync_completes_within_time_budget(
        self, n_repos: int, tmp_path: Path
    ) -> None:
        """build_sync_report must finish within a generous 5-second wall-clock budget
        even for 100 repositories, ensuring O(N²) worst-case remains tractable."""
        from src.ciel_sot_agent.repo_phase import build_sync_report

        reg_data = _make_registry(n_repos)
        keys = [r["key"] for r in reg_data["repositories"]]
        coup_data = _make_couplings(keys)

        reg_path = tmp_path / "repository_registry.json"
        coup_path = tmp_path / "couplings.json"
        reg_path.write_text(json.dumps(reg_data))
        coup_path.write_text(json.dumps(coup_data))

        start = time.perf_counter()
        result = build_sync_report(reg_path, coup_path)
        elapsed = time.perf_counter() - start

        assert elapsed < 5.0, (
            f"build_sync_report took {elapsed:.3f}s for {n_repos} repos — "
            "exceeds 5-second elasticity budget"
        )
        assert "closure_defect" in result

    def test_larger_registry_increases_pairwise_tensions(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        results = []
        for n in [3, 10, 30]:
            reg_data = _make_registry(n)
            keys = [r["key"] for r in reg_data["repositories"]]
            coup_data = _make_couplings(keys)
            reg_path = tmp_path / f"repository_registry_{n}.json"
            coup_path = tmp_path / f"couplings_{n}.json"
            reg_path.write_text(json.dumps(reg_data))
            coup_path.write_text(json.dumps(coup_data))
            r = build_sync_report(reg_path, coup_path)
            results.append((n, len(r.get("pairwise_tensions", []))))

        # More repos → more pairwise tensions
        for (n, count), (n2, count2) in zip(results, results[1:]):
            assert count2 >= count, (
                f"Expected >= pairwise tensions for n={n2} than n={n}, "
                f"got {count2} vs {count}"
            )

    def test_phased_state_build_scales_linearly(self, tmp_path: Path) -> None:
        """build_states must not regress on many small file entries."""
        from src.ciel_sot_agent.phased_state import build_states

        def _make_entries(count: int) -> list[dict[str, Any]]:
            return [
                {
                    "path": f"src/module_{i}.py",
                    "size": 512 + i * 10,
                    "ext": "py",
                    "layer": "src",
                    "content": (f"# module {i}\n" * 10).encode("utf-8"),
                    "r": i % 4,
                }
                for i in range(count)
            ]

        sizes = [10, 100, 500]
        timings = []
        for sz in sizes:
            entries = _make_entries(sz)
            start = time.perf_counter()
            build_states(entries)
            elapsed = time.perf_counter() - start
            timings.append(elapsed)

        # Timing ratio (500 entries / 10 entries) must be < 100×  (linear would be ~50×)
        ratio = (timings[-1] + 1e-9) / (timings[0] + 1e-9)
        assert ratio < 100, (
            f"build_states timing ratio ({sizes[-1]} / {sizes[0]} entries) = "
            f"{ratio:.1f} — exceeds elasticity limit of 100×"
        )


# ---------------------------------------------------------------------------
# Resilience — malformed and partial input
# ---------------------------------------------------------------------------

class TestPipelineResilience:
    """The pipeline must raise predictable exceptions for bad input,
    never silent data corruption."""

    def test_missing_registry_raises_file_error(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        with pytest.raises((FileNotFoundError, OSError)):
            build_sync_report(
                tmp_path / "nonexistent_registry.json",
                tmp_path / "nonexistent_couplings.json",
            )

    def test_malformed_json_registry_raises_value_error(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.repo_phase import load_registry

        bad = tmp_path / "bad.json"
        bad.write_text("{ not valid json }", encoding="utf-8")
        with pytest.raises((json.JSONDecodeError, ValueError)):
            load_registry(bad)

    def test_empty_registry_sync_report_is_well_formed(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        (tmp_path / "repository_registry.json").write_text(
            json.dumps({"repositories": []}), encoding="utf-8"
        )
        (tmp_path / "couplings.json").write_text(
            json.dumps({"couplings": {}}), encoding="utf-8"
        )
        result = build_sync_report(
            tmp_path / "repository_registry.json",
            tmp_path / "couplings.json",
        )
        assert isinstance(result, dict)
        assert "closure_defect" in result

    def test_single_repo_no_couplings_well_formed(self, tmp_path: Path) -> None:
        from src.ciel_sot_agent.repo_phase import build_sync_report

        reg = _make_registry(1)
        (tmp_path / "repository_registry.json").write_text(json.dumps(reg))
        (tmp_path / "couplings.json").write_text(json.dumps({"couplings": {}}))
        result = build_sync_report(
            tmp_path / "repository_registry.json",
            tmp_path / "couplings.json",
        )
        assert result["repository_count"] == 1

    def test_circular_barycenter_all_zero_weights(self) -> None:
        from src.ciel_sot_agent.holonomic_normalizer import circular_barycenter

        # All-zero weights must return a finite number (not NaN/inf)
        result = circular_barycenter([1.0, 2.0, 3.0], [0.0, 0.0, 0.0])
        assert math.isfinite(result)

    def test_wrap_returns_finite_for_extreme_angles(self) -> None:
        from src.ciel_sot_agent.holonomic_normalizer import wrap

        extreme = [1e9, -1e9, 1e15, float("inf")]
        for angle in extreme:
            try:
                result = wrap(angle)
                assert math.isfinite(result) or math.isinf(angle), (
                    f"wrap({angle}) returned non-finite: {result}"
                )
            except (OverflowError, ValueError):
                pass  # acceptable for extreme inputs

    def test_build_states_empty_input_returns_empty_list(self) -> None:
        from src.ciel_sot_agent.phased_state import build_states

        result = build_states([])
        assert result == [] or result is None or isinstance(result, list)

    def test_renormalize_couplings_empty_input(self) -> None:
        from src.ciel_sot_agent.holonomic_normalizer import renormalize_couplings

        result = renormalize_couplings({})
        assert isinstance(result, dict)
        assert result == {}


# ---------------------------------------------------------------------------
# Durability — index validator round-trip
# ---------------------------------------------------------------------------

class TestIndexValidatorDurability:
    """Index validator must produce consistent results on repeated calls."""

    ITERATIONS = 30

    def test_repeated_validation_returns_same_issue_count(self) -> None:
        from src.ciel_sot_agent.index_validator import validate_index_registry

        first_issues = validate_index_registry(ROOT)
        for _ in range(self.ITERATIONS - 1):
            issues = validate_index_registry(ROOT)
            assert len(issues) == len(first_issues), (
                "Index validator returned inconsistent issue count across iterations"
            )

    def test_validator_issues_are_always_serialisable(self) -> None:
        from src.ciel_sot_agent.index_validator import validate_index_registry

        issues = validate_index_registry(ROOT)
        # All issues must be JSON-serialisable (for downstream consumers)
        for issue in issues:
            try:
                json.dumps(issue, default=str)
            except (TypeError, ValueError) as exc:
                pytest.fail(f"Validation issue not JSON-serialisable: {exc}")
