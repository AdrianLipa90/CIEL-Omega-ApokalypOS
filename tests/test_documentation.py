"""Tests for the documentation files changed in the docs-cleanup PR.

Covers:
- README.md — top-level repository README
- docs/INDEX.md — documentation index
- docs/OPERATIONS.md — operational layer document
- packaging/README.md — packaging surfaces overview
- packaging/deb/README.md — Debian package guide

Each test class validates structure, required content, and the absence of
stale content that was intentionally removed during the cleanup.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

README = REPO_ROOT / "README.md"
INDEX = REPO_ROOT / "docs" / "INDEX.md"
OPERATIONS = REPO_ROOT / "docs" / "OPERATIONS.md"
PKG_README = REPO_ROOT / "packaging" / "README.md"
DEB_README = REPO_ROOT / "packaging" / "deb" / "README.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _headings(text: str) -> list[str]:
    """Return all Markdown heading lines (stripped) from *text*."""
    return [line.strip() for line in text.splitlines() if re.match(r"^#+\s", line)]


def _has_heading(text: str, heading: str) -> bool:
    """Return True if *heading* appears as a heading in *text* (case-insensitive)."""
    return any(heading.lower() in h.lower() for h in _headings(text))


# ---------------------------------------------------------------------------
# README.md
# ---------------------------------------------------------------------------

class TestReadme:
    """Structural and content tests for the top-level README.md."""

    @pytest.fixture(autouse=True)
    def load(self) -> None:
        self.text = README.read_text(encoding="utf-8")

    # --- required sections ---

    def test_has_role_in_ecosystem_section(self) -> None:
        assert _has_heading(self.text, "Role in the ecosystem")

    def test_has_system_architecture_section(self) -> None:
        assert _has_heading(self.text, "System architecture")

    def test_has_couplings_section(self) -> None:
        assert _has_heading(self.text, "Couplings")

    def test_has_operational_flow_section(self) -> None:
        assert _has_heading(self.text, "Operational flow")

    def test_has_main_folders_section(self) -> None:
        assert _has_heading(self.text, "Main folders")

    def test_has_existing_launchers_section(self) -> None:
        assert _has_heading(self.text, "Existing launchers")

    def test_has_existing_report_layers_section(self) -> None:
        assert _has_heading(self.text, "Existing report layers")

    def test_has_validation_layer_section(self) -> None:
        assert _has_heading(self.text, "Validation layer")

    def test_has_final_note_section(self) -> None:
        assert _has_heading(self.text, "Final note")

    # --- key content ---

    def test_describes_ciel_sot_agent_as_integration_attractor(self) -> None:
        assert "integration attractor" in self.text

    def test_mentions_ciel_omega_demo(self) -> None:
        assert "ciel-omega-demo" in self.text

    def test_mentions_metatime(self) -> None:
        assert "Metatime" in self.text

    def test_formal_reduction_chain_present(self) -> None:
        # The formal reading formula must be present
        assert "relation -> orbital state -> bridge reduction" in self.text

    def test_subsystem_integration_kernel_anchor(self) -> None:
        assert "src/ciel_sot_agent/repo_phase.py" in self.text

    def test_subsystem_gh_coupling_anchor(self) -> None:
        assert "src/ciel_sot_agent/gh_coupling.py" in self.text

    def test_subsystem_orbital_bridge_anchor(self) -> None:
        assert "src/ciel_sot_agent/orbital_bridge.py" in self.text

    def test_subsystem_sapiens_client_anchor(self) -> None:
        assert "src/ciel_sot_agent/sapiens_client.py" in self.text

    def test_subsystem_gui_anchor(self) -> None:
        assert "src/ciel_sot_agent/gui/app.py" in self.text

    def test_main_folders_lists_docs(self) -> None:
        assert "`docs/`" in self.text

    def test_main_folders_lists_integration(self) -> None:
        assert "`integration/`" in self.text

    def test_main_folders_lists_src(self) -> None:
        assert "`src/ciel_sot_agent/`" in self.text

    def test_main_folders_lists_tests(self) -> None:
        assert "`tests/`" in self.text

    def test_operational_flow_has_five_steps(self) -> None:
        # Each numbered step appears as "1.", "2.", ... "5."
        for n in range(1, 6):
            assert f"{n}. " in self.text

    def test_couplings_mentions_registry_synchronization(self) -> None:
        assert "registry" in self.text.lower()
        assert "synchronization" in self.text.lower()

    # --- removed stale content ---

    def test_direction_of_project_section_removed(self) -> None:
        assert not _has_heading(self.text, "Direction of the project")

    def test_repository_geometry_section_removed(self) -> None:
        assert not _has_heading(self.text, "Repository geometry")

    def test_entry_points_for_orientation_section_removed(self) -> None:
        assert not _has_heading(self.text, "Entry points for orientation")

    def test_execution_surfaces_section_removed(self) -> None:
        # The old "Execution surfaces" section with sub-sections is gone
        assert not _has_heading(self.text, "Execution surfaces")

    # --- regression: README must not be empty ---

    def test_readme_is_substantial(self) -> None:
        assert len(self.text.strip()) > 500


# ---------------------------------------------------------------------------
# docs/INDEX.md
# ---------------------------------------------------------------------------

class TestIndexMd:
    """Tests for docs/INDEX.md."""

    @pytest.fixture(autouse=True)
    def load(self) -> None:
        self.text = INDEX.read_text(encoding="utf-8")

    # --- required sections ---

    def test_has_core_architecture_section(self) -> None:
        assert _has_heading(self.text, "Core architecture")

    def test_has_gui_layer_section(self) -> None:
        assert _has_heading(self.text, "GUI layer")

    def test_has_scientific_section(self) -> None:
        assert _has_heading(self.text, "Scientific")

    def test_has_integration_state_section(self) -> None:
        assert _has_heading(self.text, "Integration state")

    def test_has_executable_native_layer_section(self) -> None:
        assert _has_heading(self.text, "Executable native layer")

    def test_has_gguf_model_manager_section(self) -> None:
        assert _has_heading(self.text, "GGUF model manager")

    def test_has_launchers_section(self) -> None:
        assert _has_heading(self.text, "Launchers")

    def test_has_console_entrypoints_section(self) -> None:
        assert _has_heading(self.text, "Console entrypoints")

    def test_has_report_surfaces_section(self) -> None:
        assert _has_heading(self.text, "Report surfaces")

    def test_has_validation_section(self) -> None:
        assert _has_heading(self.text, "Validation")

    def test_has_cross_reference_anchors_section(self) -> None:
        assert _has_heading(self.text, "Cross-reference anchors")

    # --- new entries added in this PR ---

    def test_agentcrossinfo_md_listed(self) -> None:
        assert "agentcrossinfo.md" in self.text

    def test_gguf_manager_entry_present(self) -> None:
        assert "src/ciel_sot_agent/gguf_manager/manager.py" in self.text

    # --- section heading text matches PR rewrite ---

    def test_core_architecture_heading_not_operating_context(self) -> None:
        # Old heading contained "operating context" — that was removed
        assert "operating context" not in self.text.lower()

    def test_gui_layer_heading_not_operator_facing(self) -> None:
        # Old heading was "GUI and operator-facing layer"
        assert not _has_heading(self.text, "GUI and operator-facing layer")

    def test_integration_state_heading_not_machine_readable_maps(self) -> None:
        # Old heading contained "machine-readable maps"
        assert not _has_heading(self.text, "Integration state and machine-readable maps")

    def test_validation_heading_not_validation_layer(self) -> None:
        # Old heading was "## Validation layer"; new is "## Validation"
        headings = _headings(self.text)
        assert any(h.lower() == "## validation" for h in headings), (
            "Expected top-level '## Validation' heading"
        )

    # --- removed entries ---

    def test_repository_machine_map_json_not_listed(self) -> None:
        assert "integration/indices/REPOSITORY_MACHINE_MAP.json" not in self.text

    def test_repository_machine_map_yaml_not_listed(self) -> None:
        assert "integration/registries/REPOSITORY_MACHINE_MAP.yaml" not in self.text

    def test_packaging_layer_section_removed(self) -> None:
        assert not _has_heading(self.text, "Packaging layer")

    def test_core_only_tool_layer_section_removed(self) -> None:
        assert not _has_heading(self.text, "Core-only tool layer")

    def test_workflow_layer_section_removed(self) -> None:
        assert not _has_heading(self.text, "Workflow layer")

    def test_launchers_heading_not_execution_surfaces(self) -> None:
        assert not _has_heading(self.text, "Launchers and execution surfaces")

    def test_console_entrypoints_not_installed_entrypoints(self) -> None:
        assert not _has_heading(self.text, "Installed console entrypoints")

    # --- key cross-reference anchors ---

    def test_cross_ref_ciel_omega_demo_present(self) -> None:
        assert "ciel_omega_demo_shell_map.json" in self.text

    def test_cross_ref_orbital_path_present(self) -> None:
        assert "orbital_bridge.py" in self.text

    def test_cross_ref_sapiens_panel_present(self) -> None:
        assert "panel_manifest.json" in self.text

    def test_cross_ref_gguf_model_management_hyphenated(self) -> None:
        # PR changed "model management layer" to "model-management layer"
        assert "model-management layer" in self.text

    def test_orbitalization_snapshot_cross_ref_removed(self) -> None:
        # The cross-reference anchor sentence for the orbitalization snapshot
        # was removed from the Cross-reference anchors section (the file-listing
        # entry in Core architecture still mentions it as a description)
        assert "orbital/panel bridge layers" not in self.text

    # --- Heisenberg/Gödel entry wording ---

    def test_heisenberg_godel_entry_updated(self) -> None:
        assert "Heisenberg/Gödel" in self.text

    # --- console entrypoints completeness ---

    def test_all_console_entrypoints_listed(self) -> None:
        expected = [
            "ciel-sot-sync",
            "ciel-sot-gh-coupling",
            "ciel-sot-orbital-bridge",
            "ciel-sot-sapiens-client",
            "ciel-sot-gui",
            "ciel-sot-install-model",
        ]
        for ep in expected:
            assert ep in self.text, f"Console entrypoint '{ep}' missing from INDEX.md"

    # --- regression ---

    def test_index_is_substantial(self) -> None:
        assert len(self.text.strip()) > 500


# ---------------------------------------------------------------------------
# docs/OPERATIONS.md
# ---------------------------------------------------------------------------

class TestOperationsMd:
    """Tests for docs/OPERATIONS.md."""

    @pytest.fixture(autouse=True)
    def load(self) -> None:
        self.text = OPERATIONS.read_text(encoding="utf-8")

    # --- required sections ---

    def test_has_purpose_section(self) -> None:
        assert _has_heading(self.text, "Purpose")

    def test_has_coupling_chain_section(self) -> None:
        assert _has_heading(self.text, "Coupling chain")

    def test_has_status_note_section(self) -> None:
        assert _has_heading(self.text, "Status note")

    def test_has_documentation_rule_section(self) -> None:
        assert _has_heading(self.text, "Documentation rule")

    def test_has_execution_surfaces_section(self) -> None:
        assert _has_heading(self.text, "Execution surfaces")

    def test_has_why_this_layer_matters_section(self) -> None:
        assert _has_heading(self.text, "Why this layer matters")

    # --- coupling chain content ---

    def test_coupling_chain_step_1_workflow(self) -> None:
        assert ".github/workflows/gh_repo_coupling.yml" in self.text

    def test_coupling_chain_step_2_script(self) -> None:
        assert "scripts/run_gh_repo_coupling.py" in self.text

    def test_coupling_chain_step_3_module(self) -> None:
        assert "src/ciel_sot_agent/gh_coupling.py" in self.text

    def test_coupling_chain_step_4_integration(self) -> None:
        assert "integration/" in self.text

    def test_coupling_chain_has_four_numbered_steps(self) -> None:
        # Steps are listed as "1.", "2.", "3.", "4."
        for n in range(1, 5):
            assert f"{n}." in self.text

    def test_documented_workflow_is_gh_repo_coupling(self) -> None:
        assert "gh_repo_coupling.yml" in self.text

    def test_documented_script_is_run_gh_repo_coupling(self) -> None:
        assert "run_gh_repo_coupling.py" in self.text

    # --- documentation rule ---

    def test_documentation_rule_mentions_workflows_readme(self) -> None:
        assert ".github/workflows/README.md" in self.text

    # --- why this layer matters ---

    def test_why_layer_matters_mentions_auditable(self) -> None:
        assert "auditable" in self.text.lower()

    # --- removed stale content ---

    def test_tools_core_only_section_removed(self) -> None:
        assert "tools/core_only" not in self.text

    def test_multiple_scripts_list_removed(self) -> None:
        # The old doc listed many scripts; now only one is mentioned
        assert "run_index_validator_v2.py" not in self.text
        assert "run_repo_sync_v2.py" not in self.text

    def test_operational_chains_section_removed(self) -> None:
        assert not _has_heading(self.text, "Operational chains")

    def test_packaging_section_removed(self) -> None:
        # Old doc had a packaging/ section
        assert not _has_heading(self.text, "packaging/")

    def test_installed_console_scripts_removed(self) -> None:
        assert "ciel-sot-sync" not in self.text

    def test_runtime_pipeline_workflow_removed(self) -> None:
        assert "runtime_pipeline.yml" not in self.text

    def test_package_workflow_removed(self) -> None:
        assert "package.yml" not in self.text

    # --- regression ---

    def test_operations_is_substantial(self) -> None:
        assert len(self.text.strip()) > 200


# ---------------------------------------------------------------------------
# packaging/README.md
# ---------------------------------------------------------------------------

class TestPackagingReadme:
    """Tests for packaging/README.md."""

    @pytest.fixture(autouse=True)
    def load(self) -> None:
        self.text = PKG_README.read_text(encoding="utf-8")

    # --- title ---

    def test_title_is_installers(self) -> None:
        first_heading = _headings(self.text)[0]
        assert first_heading.lower() == "# installers"

    # --- three-step model ---

    def test_three_step_model_step_1_install_agent(self) -> None:
        assert "install `ciel-sot-agent`" in self.text

    def test_three_step_model_step_2_llama_cpp(self) -> None:
        assert "llama-cpp-python" in self.text

    def test_three_step_model_step_3_gguf_model(self) -> None:
        assert "GGUF model" in self.text or "gguf model" in self.text.lower()

    # --- quick install examples ---

    def test_linux_macos_install_example_present(self) -> None:
        assert "install.sh" in self.text

    def test_windows_install_example_present(self) -> None:
        assert "install.ps1" in self.text

    def test_deb_section_references_deb_readme(self) -> None:
        assert "packaging/deb/README.md" in self.text

    # --- available models table ---

    def test_model_table_has_tinyllama_entry(self) -> None:
        assert "tinyllama-1.1b-chat-v1.0-q4" in self.text

    def test_model_table_has_qwen_0_5b_entry(self) -> None:
        assert "qwen2.5-0.5b-q4" in self.text

    def test_model_table_has_qwen_1_5b_entry(self) -> None:
        assert "qwen2.5-1.5b-q4" in self.text

    def test_model_table_has_phi2_entry(self) -> None:
        assert "phi-2-q4" in self.text

    def test_model_table_has_none_option(self) -> None:
        assert "`none`" in self.text

    def test_model_table_has_five_data_rows(self) -> None:
        # Count non-separator rows in the table (rows starting with |)
        data_rows = [
            line for line in self.text.splitlines()
            if line.strip().startswith("|")
            and not re.match(r"^\s*\|[-| ]+\|\s*$", line)
            and not re.match(r"^\s*\|\s*Key\s*\|", line, re.IGNORECASE)
        ]
        assert len(data_rows) == 5, f"Expected 5 model rows, got {len(data_rows)}"

    # --- model storage ---

    def test_model_storage_section_present(self) -> None:
        assert _has_heading(self.text, "Model storage")

    def test_default_model_path_is_local_share(self) -> None:
        assert "~/.local/share/ciel/models" in self.text

    def test_ciel_models_dir_env_var_mentioned(self) -> None:
        assert "CIEL_MODELS_DIR" in self.text

    # --- manual model management ---

    def test_manual_model_management_section_present(self) -> None:
        assert _has_heading(self.text, "Manual model management")

    def test_ciel_sot_install_model_mentioned(self) -> None:
        assert "ciel-sot-install-model" in self.text

    # --- contents section ---

    def test_contents_section_present(self) -> None:
        assert _has_heading(self.text, "Contents")

    def test_contents_lists_install_sh(self) -> None:
        assert "install.sh" in self.text

    def test_contents_lists_install_ps1(self) -> None:
        assert "install.ps1" in self.text

    def test_contents_lists_install_bat(self) -> None:
        assert "install.bat" in self.text

    def test_contents_lists_deb_subdir(self) -> None:
        assert "`deb/`" in self.text

    def test_contents_lists_android_subdir(self) -> None:
        assert "`android/`" in self.text

    # --- removed stale content ---

    def test_old_title_removed(self) -> None:
        assert "Packaging Surfaces" not in self.text

    def test_tinyllama_old_key_removed(self) -> None:
        # Old key was tinyllama-1.1b-chat-q4; new key has v1.0 in it
        assert "tinyllama-1.1b-chat-q4`" not in self.text

    def test_ci_packaging_section_removed(self) -> None:
        assert not _has_heading(self.text, "CI packaging")

    def test_size_column_removed_from_table(self) -> None:
        # Old table had a "Size" column with MB values
        assert "670 MB" not in self.text
        assert "397 MB" not in self.text

    # --- regression ---

    def test_packaging_readme_is_substantial(self) -> None:
        assert len(self.text.strip()) > 200


# ---------------------------------------------------------------------------
# packaging/deb/README.md
# ---------------------------------------------------------------------------

class TestDebReadme:
    """Tests for packaging/deb/README.md."""

    @pytest.fixture(autouse=True)
    def load(self) -> None:
        self.text = DEB_README.read_text(encoding="utf-8")

    # --- title ---

    def test_title_contains_debian_package(self) -> None:
        first_heading = _headings(self.text)[0]
        assert "debian" in first_heading.lower() or "Debian" in first_heading

    # --- offline install claim ---

    def test_offline_install_described(self) -> None:
        assert "offline" in self.text.lower()

    def test_model_download_is_separate_step(self) -> None:
        assert "ciel-sot-install-model" in self.text

    # --- prerequisites ---

    def test_has_prerequisites_section(self) -> None:
        assert _has_heading(self.text, "Prerequisites")

    def test_prerequisites_mentions_dpkg(self) -> None:
        assert "dpkg" in self.text

    def test_prerequisites_mentions_systemd(self) -> None:
        assert "systemd" in self.text

    # --- building ---

    def test_has_building_section(self) -> None:
        assert _has_heading(self.text, "Building")

    def test_build_command_is_bash_build_deb_sh(self) -> None:
        assert "bash build_deb.sh" in self.text

    # --- installing ---

    def test_has_installing_section(self) -> None:
        assert _has_heading(self.text, "Installing")

    def test_install_command_uses_dpkg_i(self) -> None:
        assert "dpkg -i" in self.text

    def test_apt_install_f_step_present(self) -> None:
        assert "apt install -f" in self.text

    # --- configuration ---

    def test_has_configuration_section(self) -> None:
        assert _has_heading(self.text, "Configuration")

    def test_config_file_path_present(self) -> None:
        assert "/etc/ciel-sot-agent/config.yaml" in self.text

    def test_default_gui_port_is_5050(self) -> None:
        assert "5050" in self.text

    def test_runtime_model_dir_is_var_lib_ciel(self) -> None:
        assert "/var/lib/ciel/models" in self.text

    # --- running the GUI ---

    def test_has_running_the_gui_section(self) -> None:
        assert _has_heading(self.text, "Running the GUI")

    def test_systemctl_restart_command_present(self) -> None:
        assert "systemctl restart" in self.text

    def test_systemctl_status_command_present(self) -> None:
        assert "systemctl status" in self.text

    # --- package structure ---

    def test_has_package_structure_section(self) -> None:
        assert _has_heading(self.text, "Package structure")

    def test_package_structure_shows_debian_dir(self) -> None:
        assert "DEBIAN/" in self.text

    def test_package_structure_shows_etc_dir(self) -> None:
        assert "etc/" in self.text

    def test_package_structure_shows_opt_dir(self) -> None:
        assert "opt/" in self.text

    def test_package_structure_shows_usr_bin(self) -> None:
        assert "usr/bin" in self.text or "usr/" in self.text

    def test_package_structure_shows_var_lib(self) -> None:
        assert "var/" in self.text

    def test_package_structure_shows_ciel_sot_gui_binary(self) -> None:
        assert "ciel-sot-gui" in self.text

    def test_package_structure_shows_ciel_sot_install_model_binary(self) -> None:
        assert "ciel-sot-install-model" in self.text

    def test_package_structure_shows_service_file(self) -> None:
        assert "ciel-sot-gui.service" in self.text

    # --- uninstalling ---

    def test_has_uninstalling_section(self) -> None:
        assert _has_heading(self.text, "Uninstalling")

    def test_dpkg_r_command_present(self) -> None:
        assert "dpkg -r" in self.text

    def test_dpkg_purge_command_present(self) -> None:
        assert "dpkg -P" in self.text

    # --- removed stale content ---

    def test_changing_default_port_section_removed(self) -> None:
        assert not _has_heading(self.text, "Changing the default port")

    def test_reproducible_builds_section_removed(self) -> None:
        assert not _has_heading(self.text, "Reproducible builds")

    def test_build_machine_prerequisites_table_removed(self) -> None:
        # Old doc had a table with dpkg-deb, python3, pip install columns
        assert "dpkg-deb" not in self.text

    def test_installation_layout_table_removed(self) -> None:
        # Old doc had a detailed table with path/contents columns
        assert "Installation layout" not in self.text

    def test_managing_gguf_models_section_removed(self) -> None:
        assert not _has_heading(self.text, "Managing GGUF models")

    # --- regression ---

    def test_deb_readme_is_substantial(self) -> None:
        assert len(self.text.strip()) > 300