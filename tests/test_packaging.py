"""Tests for the CIEL SOT Agent platform packaging.

These tests verify:
- The Debian package structure is complete and well-formed
- The Android Buildozer spec is valid and contains required fields
- The Android Kivy main module is importable and has the expected API
- The build_deb.sh script exists and is a valid shell script
"""

from __future__ import annotations

import re
import stat
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DEB_DIR = REPO_ROOT / "packaging" / "deb"
ANDROID_DIR = REPO_ROOT / "packaging" / "android"


# ---------------------------------------------------------------------------
# Debian package structure
# ---------------------------------------------------------------------------

class TestDebianPackageStructure:
    def test_debian_dir_exists(self):
        assert (DEB_DIR / "DEBIAN").is_dir()

    def test_control_file_exists(self):
        assert (DEB_DIR / "DEBIAN" / "control").is_file()

    def test_postinst_exists(self):
        assert (DEB_DIR / "DEBIAN" / "postinst").is_file()

    def test_prerm_exists(self):
        assert (DEB_DIR / "DEBIAN" / "prerm").is_file()

    def test_postrm_exists(self):
        assert (DEB_DIR / "DEBIAN" / "postrm").is_file()

    def test_launcher_exists(self):
        assert (DEB_DIR / "usr" / "bin" / "ciel-sot-gui").is_file()

    def test_model_installer_launcher_exists(self):
        assert (DEB_DIR / "usr" / "bin" / "ciel-sot-install-model").is_file()

    def test_service_file_exists(self):
        assert (DEB_DIR / "usr" / "lib" / "systemd" / "system" / "ciel-sot-gui.service").is_file()

    def test_wheels_dir_exists(self):
        assert (DEB_DIR / "opt" / "ciel-sot-agent" / "wheels").is_dir()

    def test_models_dir_exists(self):
        assert (DEB_DIR / "var" / "lib" / "ciel" / "models").is_dir()

    def test_readme_exists(self):
        assert (DEB_DIR / "README.md").is_file()

    def test_build_script_exists(self):
        assert (DEB_DIR / "build_deb.sh").is_file()


class TestDebianControlFile:
    @pytest.fixture(autouse=True)
    def load_control(self):
        self.content = (DEB_DIR / "DEBIAN" / "control").read_text()

    def _field(self, name: str) -> str:
        m = re.search(rf"^{name}:\s*(.+)$", self.content, re.MULTILINE)
        assert m, f"Field '{name}' not found in DEBIAN/control"
        return m.group(1).strip()

    def test_package_name(self):
        assert self._field("Package") == "ciel-sot-agent"

    def test_version_present(self):
        version = self._field("Version")
        assert re.match(r"\d+\.\d+\.\d+", version), f"Unexpected version: {version}"

    def test_architecture(self):
        assert self._field("Architecture") == "all"

    def test_depends_python(self):
        depends = self._field("Depends")
        assert "python3" in depends

    def test_depends_python_venv(self):
        depends = self._field("Depends")
        assert "python3-venv" in depends

    def test_does_not_depend_on_pip(self):
        depends = self._field("Depends")
        assert "python3-pip" not in depends

    def test_description_not_empty(self):
        assert len(self._field("Description")) > 10


class TestDebianScripts:
    def test_postinst_is_shell_script(self):
        content = (DEB_DIR / "DEBIAN" / "postinst").read_text()
        assert content.startswith("#!/bin/sh") or content.startswith("#!/usr/bin/env sh")

    def test_postinst_creates_venv(self):
        content = (DEB_DIR / "DEBIAN" / "postinst").read_text()
        assert "python3 -m venv" in content

    def test_postinst_contains_pip_install(self):
        content = (DEB_DIR / "DEBIAN" / "postinst").read_text()
        # pip is invoked via the venv path (e.g. "${VENV_DIR}/bin/pip" install)
        # or as a global pip; accept either form
        assert re.search(r'/pip["\']?\s+install|pip3?\s+install', content)

    def test_postinst_installs_offline(self):
        content = (DEB_DIR / "DEBIAN" / "postinst").read_text()
        assert "--no-index" in content

    def test_postinst_uses_bundled_wheels(self):
        content = (DEB_DIR / "DEBIAN" / "postinst").read_text()
        assert "--find-links" in content

    def test_postinst_does_not_global_pip_install(self):
        content = (DEB_DIR / "DEBIAN" / "postinst").read_text()
        # A bare (global) pip install starts the line with pip3 or pip
        assert not re.search(r"^\s*pip3?\s+install", content, re.MULTILINE)

    def test_postinst_installs_into_opt_venv(self):
        content = (DEB_DIR / "DEBIAN" / "postinst").read_text()
        assert "/opt/ciel-sot-agent" in content

    def test_prerm_is_shell_script(self):
        content = (DEB_DIR / "DEBIAN" / "prerm").read_text()
        assert content.startswith("#!/bin/sh") or content.startswith("#!/usr/bin/env sh")

    def test_prerm_stops_service(self):
        content = (DEB_DIR / "DEBIAN" / "prerm").read_text()
        assert "systemctl stop" in content

    def test_prerm_disables_service(self):
        content = (DEB_DIR / "DEBIAN" / "prerm").read_text()
        assert "systemctl disable" in content

    def test_postrm_is_shell_script(self):
        content = (DEB_DIR / "DEBIAN" / "postrm").read_text()
        assert content.startswith("#!/bin/sh") or content.startswith("#!/usr/bin/env sh")

    def test_postrm_cleans_up_venv(self):
        content = (DEB_DIR / "DEBIAN" / "postrm").read_text()
        assert "/opt/ciel-sot-agent" in content
        assert "rm -rf" in content or "purge" in content


class TestDebianServiceFile:
    @pytest.fixture(autouse=True)
    def load_service(self):
        self.content = (
            DEB_DIR / "usr" / "lib" / "systemd" / "system" / "ciel-sot-gui.service"
        ).read_text()

    def test_has_unit_section(self):
        assert "[Unit]" in self.content

    def test_has_service_section(self):
        assert "[Service]" in self.content

    def test_has_install_section(self):
        assert "[Install]" in self.content

    def test_exec_start_present(self):
        assert "ExecStart=" in self.content

    def test_exec_start_uses_launcher(self):
        assert "ciel-sot-gui" in self.content


class TestDebianLauncher:
    def test_launcher_is_shell_script(self):
        content = (DEB_DIR / "usr" / "bin" / "ciel-sot-gui").read_text()
        assert content.startswith("#!/bin/sh") or content.startswith("#!/usr/bin/env sh")

    def test_launcher_invokes_gui_module(self):
        content = (DEB_DIR / "usr" / "bin" / "ciel-sot-gui").read_text()
        assert "ciel_sot_agent.gui" in content or "ciel-sot-gui" in content

    def test_launcher_uses_venv(self):
        content = (DEB_DIR / "usr" / "bin" / "ciel-sot-gui").read_text()
        assert "/opt/ciel-sot-agent/venv" in content

    def test_model_installer_launcher_is_shell_script(self):
        content = (DEB_DIR / "usr" / "bin" / "ciel-sot-install-model").read_text()
        assert content.startswith("#!/bin/sh") or content.startswith("#!/usr/bin/env sh")

    def test_model_installer_launcher_uses_venv(self):
        content = (DEB_DIR / "usr" / "bin" / "ciel-sot-install-model").read_text()
        assert "/opt/ciel-sot-agent/venv" in content


class TestBuildScript:
    def test_build_script_is_bash(self):
        content = (DEB_DIR / "build_deb.sh").read_text()
        assert "#!/usr/bin/env bash" in content or "#!/bin/bash" in content

    def test_build_script_calls_dpkg_deb(self):
        content = (DEB_DIR / "build_deb.sh").read_text()
        assert "dpkg-deb" in content

    def test_build_script_references_version_file(self):
        content = (DEB_DIR / "build_deb.sh").read_text()
        assert "VERSION" in content

    def test_build_script_bundles_wheels(self):
        content = (DEB_DIR / "build_deb.sh").read_text()
        assert "pip wheel" in content or "pip download" in content

    def test_build_script_uses_staging_dir(self):
        content = (DEB_DIR / "build_deb.sh").read_text()
        assert "STAGING" in content or "mktemp" in content


# ---------------------------------------------------------------------------
# Android packaging
# ---------------------------------------------------------------------------

class TestAndroidPackagingStructure:
    def test_android_dir_exists(self):
        assert ANDROID_DIR.is_dir()

    def test_main_py_exists(self):
        assert (ANDROID_DIR / "main.py").is_file()

    def test_buildozer_spec_exists(self):
        assert (ANDROID_DIR / "buildozer.spec").is_file()

    def test_readme_exists(self):
        assert (ANDROID_DIR / "README.md").is_file()


class TestBuildozerSpec:
    @pytest.fixture(autouse=True)
    def load_spec(self):
        self.content = (ANDROID_DIR / "buildozer.spec").read_text()

    def _value(self, key: str) -> str:
        m = re.search(rf"^{re.escape(key)}\s*=\s*(.+)$", self.content, re.MULTILINE)
        assert m, f"Key '{key}' not found in buildozer.spec"
        return m.group(1).strip()

    def test_title_present(self):
        assert self._value("title")

    def test_package_name_present(self):
        assert self._value("package.name")

    def test_version_present(self):
        version = self._value("version")
        assert re.match(r"\d+\.\d+\.\d+", version), f"Unexpected version: {version}"

    def test_requirements_include_kivy(self):
        reqs = self._value("requirements")
        assert "kivy" in reqs.lower()

    def test_android_minapi(self):
        minapi = int(self._value("android.minapi"))
        assert minapi >= 26, "Minimum Android API should be at least 26 (Android 8.0)"

    def test_android_api(self):
        api = int(self._value("android.api"))
        assert api >= 33, "Target Android API should be at least 33 (Android 13)"

    def test_internet_permission(self):
        perms = self._value("android.permissions")
        assert "INTERNET" in perms

    def test_archs_present(self):
        archs = self._value("android.archs")
        assert "arm64-v8a" in archs or "armeabi-v7a" in archs


class TestAndroidMainModule:
    """Import-level tests for the Kivy Android app (no actual Kivy required)."""

    def test_main_py_is_valid_python(self):
        import ast
        source = (ANDROID_DIR / "main.py").read_text()
        # Should parse without errors
        tree = ast.parse(source)
        assert tree is not None

    def test_main_py_defines_ciel_orbital_app(self):
        source = (ANDROID_DIR / "main.py").read_text()
        assert "class CIELOrbitalApp" in source

    def test_main_py_defines_main_function(self):
        source = (ANDROID_DIR / "main.py").read_text()
        assert "def main()" in source

    def test_main_py_defines_server_url(self):
        source = (ANDROID_DIR / "main.py").read_text()
        assert "SERVER_URL" in source

    def test_main_py_polls_api_status(self):
        source = (ANDROID_DIR / "main.py").read_text()
        assert "/api/status" in source

    def test_main_py_has_refresh_interval(self):
        source = (ANDROID_DIR / "main.py").read_text()
        assert "schedule_interval" in source or "Clock" in source
