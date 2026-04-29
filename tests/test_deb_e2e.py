"""End-to-end smoke tests for the Debian .deb package build.

These tests build the actual .deb package using ``build_deb.sh``, then
inspect the resulting archive with ``dpkg-deb`` to verify that the
package contains the expected files and metadata.

The tests are skipped automatically when ``dpkg-deb`` is not available
(e.g. on macOS or non-Debian CI runners).

To run explicitly::

    python -m pytest tests/test_deb_e2e.py -v
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "packaging" / "deb" / "build_deb.sh"

# Skip the entire module if dpkg-deb is not installed
pytestmark = pytest.mark.skipif(
    shutil.which("dpkg-deb") is None,
    reason="dpkg-deb not available on this system",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def built_deb(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the .deb package once for the whole module and return its path."""
    dist_dir = REPO_ROOT / "dist"

    result = subprocess.run(
        ["bash", str(BUILD_SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"build_deb.sh failed (rc={result.returncode}):\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    debs = sorted(dist_dir.glob("ciel-sot-agent_*.deb"))
    assert debs, f"No .deb found in {dist_dir} after build"
    return debs[-1]


@pytest.fixture(scope="module")
def deb_contents(built_deb: Path) -> str:
    """Return the full file listing of the .deb (``dpkg-deb -c``)."""
    result = subprocess.run(
        ["dpkg-deb", "-c", str(built_deb)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    return result.stdout


@pytest.fixture(scope="module")
def deb_info(built_deb: Path) -> str:
    """Return the control metadata of the .deb (``dpkg-deb -I``)."""
    result = subprocess.run(
        ["dpkg-deb", "-I", str(built_deb)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    return result.stdout


# ---------------------------------------------------------------------------
# Package metadata
# ---------------------------------------------------------------------------

class TestDebPackageMetadata:
    """Verify the metadata section of the built .deb."""

    def test_package_name(self, deb_info: str) -> None:
        assert "Package: ciel-sot-agent" in deb_info

    def test_version_matches(self, deb_info: str) -> None:
        version = (REPO_ROOT / "VERSION").read_text().strip()
        assert f"Version: {version}" in deb_info

    def test_architecture_is_not_all(self, deb_info: str) -> None:
        # Since we bundle numpy (arch-specific), the arch must NOT be "all"
        m = re.search(r"Architecture:\s*(\S+)", deb_info)
        assert m, "Architecture field not found"
        assert m.group(1) != "all", "Architecture should be host-specific, not 'all'"

    def test_depends_python_venv(self, deb_info: str) -> None:
        assert "python3-venv" in deb_info

    def test_does_not_depend_on_pip(self, deb_info: str) -> None:
        assert "python3-pip" not in deb_info


# ---------------------------------------------------------------------------
# File layout verification
# ---------------------------------------------------------------------------

class TestDebFileLayout:
    """Verify that the .deb contains all expected files."""

    @pytest.mark.parametrize(
        "path",
        [
            "/usr/bin/ciel-sot-gui",
            "/usr/bin/ciel-sot-install-model",
            "/usr/lib/systemd/system/ciel-sot-gui.service",
            "/etc/ciel-sot-agent/config.yaml",
        ],
    )
    def test_expected_file_present(self, deb_contents: str, path: str) -> None:
        assert path in deb_contents, f"{path} not found in .deb contents"

    def test_wheels_directory_present(self, deb_contents: str) -> None:
        assert "/opt/ciel-sot-agent/wheels/" in deb_contents

    def test_wheels_are_bundled(self, deb_contents: str) -> None:
        assert ".whl" in deb_contents, "No .whl files found inside the .deb"

    def test_no_gitkeep_files(self, deb_contents: str) -> None:
        assert ".gitkeep" not in deb_contents

    def test_no_build_script_inside(self, deb_contents: str) -> None:
        assert "build_deb.sh" not in deb_contents

    def test_no_constraints_inside(self, deb_contents: str) -> None:
        assert "constraints.txt" not in deb_contents

    def test_no_readme_inside(self, deb_contents: str) -> None:
        # The deb skeleton README is a developer doc, not shipped
        assert "README.md" not in deb_contents

    def test_models_directory_present(self, deb_contents: str) -> None:
        assert "/var/lib/ciel/models/" in deb_contents

    def test_maintainer_scripts_present(self, deb_info: str) -> None:
        for script in ("postinst", "prerm", "postrm"):
            assert script in deb_info, f"Maintainer script '{script}' not found"

    def test_conffiles_present(self, deb_info: str) -> None:
        assert "conffiles" in deb_info or "config.yaml" in deb_info
