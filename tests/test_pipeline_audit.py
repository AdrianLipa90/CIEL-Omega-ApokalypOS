"""Pipeline audit tests — verify every source module has a defined role
and that no orphaned scripts exist without a corresponding entry point.

These tests reflect the "testy popeliny" requirement: confirm the full
pipeline topology is coherent, each file belongs to the system, and
no loose scripts hang without a clear integration path.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import re
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_PKG = _REPO_ROOT / "src" / "ciel_sot_agent"
_SCRIPTS_DIR = _REPO_ROOT / "scripts"


def _collect_source_modules() -> list[Path]:
    """Return all .py source files under src/ciel_sot_agent/."""
    return sorted(
        p
        for p in _SRC_PKG.rglob("*.py")
        if "__pycache__" not in p.parts
    )


def _collect_scripts() -> list[Path]:
    """Return all .py scripts under scripts/."""
    return sorted(
        p for p in _SCRIPTS_DIR.glob("*.py") if not p.name.startswith("_")
    )


def _has_module_docstring(path: Path) -> bool:
    """Return True if the module has a top-level docstring."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    return bool(ast.get_docstring(tree))


def _has_callable(path: Path, name: str) -> bool:
    """Return True if the module defines a top-level callable with the given name."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == name:
                return True
    return False


def _imports_ciel_module(path: Path) -> bool:
    """Return True if the script integrates with ciel_sot_agent or the integration/ layer."""
    text = path.read_text(encoding="utf-8")
    return bool(
        re.search(r"from\s+(src\.)?ciel_sot_agent", text)
        or re.search(r"import\s+(src\.)?ciel_sot_agent", text)
        or re.search(r"from\s+integration\.", text)
        # Scripts that operate on integration/ paths (path-based, not import-based)
        or re.search(r"['\"]integration[/\\]", text)
        or re.search(r"integration['\"]", text)
        or re.search(r"\bintegration\b.*\bOrbital\b", text)
    )


# ---------------------------------------------------------------------------
# Pipeline topology: every module must have a clear purpose
# ---------------------------------------------------------------------------

EXPECTED_MODULES: dict[str, str] = {
    "__init__.py": "package init",
    "__main__.py": "CLI entry point",
    "paths.py": "project root resolution",
    "ciel_pipeline.py": "CIEL/Ω pipeline adapter — routes orbital state through CielEngine",
    "repo_phase.py": "repository phase state and sync report",
    "synchronize.py": "synchronize entry point (v1)",
    "synchronize_v2.py": "synchronize entry point (v2)",
    "gh_coupling.py": "GitHub coupling subsystem (v1)",
    "gh_coupling_v2.py": "GitHub coupling subsystem (v2)",
    "holonomic_normalizer.py": "holonomic phase normalizer",
    "index_validator.py": "index validation (v1)",
    "index_validator_v2.py": "index validation (v2)",
    "orbital_bridge.py": "orbital bridge / global pass runner",
    "phased_state.py": "phased state model",
    "runtime_evidence_ingest.py": "runtime evidence ingest pipeline",
    "sapiens_client.py": "Sapiens client packet interface",
    "sapiens_surface_policy.py": "Sapiens surface policy engine",
    "integration_mirror.py": "integration mirror sync runner",
    "pipeline_maintenance.py": "maintenance pipeline orchestrator",
    "control_panel_app.py": "standalone control panel application",
}


class TestModulePresence:
    """Each expected source module must be physically present."""

    @pytest.mark.parametrize("module_name", list(EXPECTED_MODULES.keys()))
    def test_module_file_exists(self, module_name: str) -> None:
        candidates = list(_SRC_PKG.rglob(module_name))
        assert candidates, (
            f"Expected source module {module_name!r} not found under {_SRC_PKG}"
        )

    def test_no_unexpected_top_level_py_files(self) -> None:
        """Top-level .py files in the package must all be known modules."""
        known = set(EXPECTED_MODULES.keys()) | {"SAPIENS_RUNTIME_PATCH.md", "AGENT1.md"}
        top_level = {p.name for p in _SRC_PKG.glob("*.py") if not p.name.startswith("_")}
        known_py = {k for k in known if k.endswith(".py")}
        # All top-level .py files (excluding __*.py) must be in the known set
        dunder_excluded = {p.name for p in _SRC_PKG.glob("*.py") if p.name.startswith("__")}
        non_dunder = top_level - dunder_excluded
        unexpected = non_dunder - known_py
        assert unexpected == set(), (
            f"Unexpected top-level modules in package: {unexpected!r}"
        )


class TestModuleDocstrings:
    """Core source modules must have module-level docstrings or __all__ exports."""

    # These modules are well-defined but may omit a docstring (init files, etc.)
    DOCSTRING_OPTIONAL = {"__init__.py", "__main__.py"}

    @pytest.mark.parametrize(
        "rel_path",
        [
            "paths.py",
            "ciel_pipeline.py",
            "repo_phase.py",
            "synchronize.py",
            "synchronize_v2.py",
            "gh_coupling.py",
            "gh_coupling_v2.py",
            "holonomic_normalizer.py",
            "index_validator.py",
            "index_validator_v2.py",
            "orbital_bridge.py",
            "phased_state.py",
            "runtime_evidence_ingest.py",
            "sapiens_client.py",
            "sapiens_surface_policy.py",
            "gguf_manager/manager.py",
        ],
    )
    def test_has_module_docstring(self, rel_path: str) -> None:
        path = _SRC_PKG / rel_path
        assert path.exists(), f"Module file not found: {path}"
        assert _has_module_docstring(path), (
            f"{rel_path} lacks a module-level docstring — every module must "
            "document its purpose."
        )


class TestEntryPoints:
    """Every module that is a console-script entry point must export main()."""

    ENTRY_POINT_MODULES = [
        "synchronize.py",
        "synchronize_v2.py",
        "gh_coupling.py",
        "gh_coupling_v2.py",
        "index_validator.py",
        "index_validator_v2.py",
        "orbital_bridge.py",
        "ciel_pipeline.py",
        "sapiens_client.py",
        "runtime_evidence_ingest.py",
    ]

    @pytest.mark.parametrize("module_name", ENTRY_POINT_MODULES)
    def test_module_exports_main(self, module_name: str) -> None:
        path = _SRC_PKG / module_name
        assert path.exists(), f"Module not found: {path}"
        assert _has_callable(path, "main"), (
            f"{module_name} is a console-script entry point but does not define main()"
        )

    def test_gui_exports_main(self) -> None:
        gui_app = _SRC_PKG / "gui" / "app.py"
        assert gui_app.exists()
        assert _has_callable(gui_app, "main"), "gui/app.py must define main()"

    def test_gguf_manager_exports_download_helper(self) -> None:
        manager = _SRC_PKG / "gguf_manager" / "manager.py"
        assert manager.exists()
        assert _has_callable(manager, "download_default_model"), (
            "gguf_manager/manager.py must export download_default_model()"
        )


# ---------------------------------------------------------------------------
# Scripts — no orphaned/loose scripts
# ---------------------------------------------------------------------------

class TestScriptsIntegrity:
    """Every script in scripts/ must integrate with the package (no orphan scripts)."""

    def test_all_scripts_import_ciel_modules(self) -> None:
        loose = [
            s.name
            for s in _collect_scripts()
            if not _imports_ciel_module(s)
        ]
        assert loose == [], (
            f"Orphaned scripts (no ciel_sot_agent or integration import): {loose!r}"
        )

    def test_all_run_scripts_have_if_main_guard(self) -> None:
        """Scripts prefixed with 'run_' must have an if __name__ == '__main__' guard."""
        missing_guard = []
        for s in _collect_scripts():
            if s.name.startswith("run_"):
                text = s.read_text(encoding="utf-8")
                if '__name__' not in text or '__main__' not in text:
                    missing_guard.append(s.name)
        assert missing_guard == [], (
            f"run_* scripts missing __main__ guard: {missing_guard!r}"
        )

    def test_scripts_have_no_hardcoded_absolute_paths(self) -> None:
        """Scripts must not hardcode absolute paths like /home/... or /Users/..."""
        offenders = []
        for s in _collect_scripts():
            text = s.read_text(encoding="utf-8")
            # Exclude comment lines and string literals that are clearly comments
            code_lines = [
                ln for ln in text.splitlines()
                if not ln.strip().startswith("#")
            ]
            code_text = "\n".join(code_lines)
            if re.search(r'["\'](?:/home/|/Users/|/root/)', code_text):
                offenders.append(s.name)
        assert offenders == [], (
            f"Scripts contain hardcoded absolute paths: {offenders!r}"
        )

    def test_integration_scripts_have_correct_structure(self) -> None:
        """Integration orbital scripts must import from integration.Orbital or stdlib."""
        orbital_scripts = _REPO_ROOT / "integration" / "Orbital" / "main" / "scripts"
        if not orbital_scripts.exists():
            pytest.skip("Orbital scripts directory not found")
        for s in orbital_scripts.glob("*.py"):
            text = s.read_text(encoding="utf-8")
            # Must at least import something (not empty)
            assert re.search(r"^import |^from ", text, re.MULTILINE), (
                f"Orbital script {s.name} has no imports — appears to be empty/loose"
            )


# ---------------------------------------------------------------------------
# Package import smoke-test (every public module must be importable)
# ---------------------------------------------------------------------------

PUBLIC_MODULES = [
    "src.ciel_sot_agent",
    "src.ciel_sot_agent.paths",
    "src.ciel_sot_agent.ciel_pipeline",
    "src.ciel_sot_agent.repo_phase",
    "src.ciel_sot_agent.synchronize",
    "src.ciel_sot_agent.synchronize_v2",
    "src.ciel_sot_agent.gh_coupling",
    "src.ciel_sot_agent.gh_coupling_v2",
    "src.ciel_sot_agent.holonomic_normalizer",
    "src.ciel_sot_agent.index_validator",
    "src.ciel_sot_agent.index_validator_v2",
    "src.ciel_sot_agent.orbital_bridge",
    "src.ciel_sot_agent.phased_state",
    "src.ciel_sot_agent.runtime_evidence_ingest",
    "src.ciel_sot_agent.sapiens_client",
    "src.ciel_sot_agent.sapiens_surface_policy",
    "src.ciel_sot_agent.gguf_manager.manager",
    "src.ciel_sot_agent.gui.app",
]


class TestModuleImportability:
    """Every public module must import without error."""

    @pytest.mark.parametrize("module_name", PUBLIC_MODULES)
    def test_module_importable(self, module_name: str) -> None:
        try:
            mod = importlib.import_module(module_name)
        except ImportError as exc:
            pytest.fail(f"Cannot import {module_name!r}: {exc}")
        assert mod is not None

    def test_sapiens_panel_submodules_importable(self) -> None:
        submodules = [
            "src.ciel_sot_agent.sapiens_panel",
            "src.ciel_sot_agent.sapiens_panel.models",
            "src.ciel_sot_agent.sapiens_panel.controller",
            "src.ciel_sot_agent.sapiens_panel.communication",
            "src.ciel_sot_agent.sapiens_panel.reduction",
            "src.ciel_sot_agent.sapiens_panel.render_schema",
            "src.ciel_sot_agent.sapiens_panel.settings_store",
            "src.ciel_sot_agent.sapiens_panel.support",
        ]
        for mod_name in submodules:
            try:
                mod = importlib.import_module(mod_name)
            except ImportError as exc:
                pytest.fail(f"Cannot import {mod_name!r}: {exc}")
            assert mod is not None
