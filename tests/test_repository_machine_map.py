"""Tests for current documentation consistency on main.

These tests verify the current repository state rather than a historical
single-PR cleanup snapshot:
- retained machine-map and documentation files that are still part of main
  remain present on disk,
- `.github/workflows/README.md` reflects the currently documented workflow
  surface,
- docs and packaging surfaces remain internally consistent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Retained files that are still part of the current repo state.
JSON_MAP_PATH = REPO_ROOT / "integration" / "indices" / "REPOSITORY_MACHINE_MAP.json"
YAML_MAP_PATH = REPO_ROOT / "integration" / "registries" / "REPOSITORY_MACHINE_MAP.yaml"
DECL_MATRIX_DOC = REPO_ROOT / "docs" / "DECLARATION_IMPLEMENTATION_MATRIX.md"
REPO_GUIDE_DOC = REPO_ROOT / "docs" / "REPOSITORY_GUIDE_HUMAN.md"
DOC_CONSISTENCY_TODO = (
    REPO_ROOT / "docs" / "operations" / "DOCUMENTATION_CONSISTENCY_AND_COVERAGE_TODO.md"
)

# Paths that were modified.
WORKFLOW_README = REPO_ROOT / ".github" / "workflows" / "README.md"
INDEX_DOC = REPO_ROOT / "docs" / "INDEX.md"
OPERATIONS_DOC = REPO_ROOT / "docs" / "OPERATIONS.md"
PACKAGING_README = REPO_ROOT / "packaging" / "README.md"
DEB_README = REPO_ROOT / "packaging" / "deb" / "README.md"
MAIN_README = REPO_ROOT / "README.md"

CURRENT_WORKFLOW_FILES = {
    "ci.yml",
    "runtime_pipeline.yml",
    "package.yml",
    "gh_repo_coupling.yml",
}
DOCUMENTED_WORKFLOW = "gh_repo_coupling.yml"


# ---------------------------------------------------------------------------
# Retained files must still exist on main
# ---------------------------------------------------------------------------


class TestRetainedFilesPresent:
    """Verify that files still used by main remain present on disk."""

    def test_json_machine_map_present(self) -> None:
        assert JSON_MAP_PATH.is_file(), f"Expected retained file missing: {JSON_MAP_PATH}"

    def test_yaml_machine_map_present(self) -> None:
        assert YAML_MAP_PATH.is_file(), f"Expected retained file missing: {YAML_MAP_PATH}"

    def test_declaration_implementation_matrix_present(self) -> None:
        assert DECL_MATRIX_DOC.is_file(), f"Expected retained file missing: {DECL_MATRIX_DOC}"

    def test_repository_guide_human_present(self) -> None:
        assert REPO_GUIDE_DOC.is_file(), f"Expected retained file missing: {REPO_GUIDE_DOC}"

    def test_documentation_consistency_todo_present(self) -> None:
        assert DOC_CONSISTENCY_TODO.is_file(), f"Expected retained file missing: {DOC_CONSISTENCY_TODO}"


# ---------------------------------------------------------------------------
# .github/workflows/README.md — current multi-workflow state
# ---------------------------------------------------------------------------


class TestWorkflowREADME:
    """Verify the current .github/workflows/README.md content."""

    @pytest.fixture(autouse=True)
    def load_content(self) -> None:
        assert WORKFLOW_README.is_file(), f"Workflow README not found: {WORKFLOW_README}"
        self.content = WORKFLOW_README.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        assert WORKFLOW_README.is_file()

    def test_documents_current_workflow_surface(self) -> None:
        for workflow in CURRENT_WORKFLOW_FILES:
            assert workflow in self.content

    def test_documents_gh_repo_coupling_workflow(self) -> None:
        assert DOCUMENTED_WORKFLOW in self.content

    def test_has_current_workflows_section(self) -> None:
        assert "Current workflows" in self.content

    def test_has_structural_rule_section(self) -> None:
        assert "Structural rule" in self.content

    def test_structural_rule_mentions_trigger(self) -> None:
        assert "trigger" in self.content.lower()

    def test_structural_rule_mentions_entrypoint(self) -> None:
        assert "entrypoint" in self.content.lower()

    def test_has_documentation_rule_section(self) -> None:
        assert "Documentation rule" in self.content

    def test_coupling_workflow_describes_schedule(self) -> None:
        assert "15 minute" in self.content.lower() or "schedule" in self.content.lower()

    def test_coupling_workflow_describes_script(self) -> None:
        assert "run_gh_repo_coupling.py" in self.content

    def test_coupling_workflow_describes_commit_behavior(self) -> None:
        assert "commit" in self.content.lower()


# ---------------------------------------------------------------------------
# docs/INDEX.md — reorganized, removed file references
# ---------------------------------------------------------------------------


class TestIndexDocumentation:
    """Verify that docs/INDEX.md no longer references deleted files and has correct structure."""

    @pytest.fixture(autouse=True)
    def load_content(self) -> None:
        assert INDEX_DOC.is_file(), f"INDEX.md not found: {INDEX_DOC}"
        self.content = INDEX_DOC.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        assert INDEX_DOC.is_file()

    def test_does_not_reference_declaration_implementation_matrix(self) -> None:
        """DECLARATION_IMPLEMENTATION_MATRIX.md must not be indexed in docs/INDEX.md."""
        assert "DECLARATION_IMPLEMENTATION_MATRIX.md" not in self.content

    def test_does_not_reference_repository_guide_human(self) -> None:
        """REPOSITORY_GUIDE_HUMAN.md must not be indexed in docs/INDEX.md."""
        assert "REPOSITORY_GUIDE_HUMAN.md" not in self.content

    def test_does_not_reference_json_machine_map(self) -> None:
        """REPOSITORY_MACHINE_MAP.json must not be indexed in docs/INDEX.md."""
        assert "REPOSITORY_MACHINE_MAP.json" not in self.content

    def test_does_not_reference_yaml_machine_map(self) -> None:
        """REPOSITORY_MACHINE_MAP.yaml must not be indexed in docs/INDEX.md."""
        assert "REPOSITORY_MACHINE_MAP.yaml" not in self.content

    def test_has_console_entrypoints_section(self) -> None:
        assert "Console entrypoints" in self.content

    def test_console_entrypoints_includes_gui(self) -> None:
        assert "ciel-sot-gui" in self.content

    def test_console_entrypoints_includes_sync(self) -> None:
        assert "ciel-sot-sync" in self.content

    def test_console_entrypoints_includes_gh_coupling(self) -> None:
        assert "ciel-sot-gh-coupling" in self.content

    def test_console_entrypoints_includes_orbital_bridge(self) -> None:
        assert "ciel-sot-orbital-bridge" in self.content

    def test_console_entrypoints_includes_sapiens_client(self) -> None:
        assert "ciel-sot-sapiens-client" in self.content

    def test_console_entrypoints_includes_runtime_evidence_ingest(self) -> None:
        assert "ciel-sot-runtime-evidence-ingest" in self.content

    def test_has_gui_layer_section(self) -> None:
        assert "## GUI layer" in self.content

    def test_gui_layer_references_app_py(self) -> None:
        assert "gui/app.py" in self.content

    def test_gui_layer_references_routes_py(self) -> None:
        assert "gui/routes.py" in self.content

    def test_has_gguf_model_manager_section(self) -> None:
        assert "GGUF model manager" in self.content

    def test_gguf_manager_references_manager_py(self) -> None:
        assert "gguf_manager/manager.py" in self.content

    def test_has_heisenberg_godel_cross_reference(self) -> None:
        assert "Heisenberg" in self.content or "heisenberg" in self.content.lower()

    def test_heisenberg_cross_reference_links_to_hypotheses(self) -> None:
        assert "HYPOTHESES.md" in self.content

    def test_has_core_architecture_section(self) -> None:
        assert "## Core architecture" in self.content

    def test_core_architecture_references_operations_doc(self) -> None:
        assert "docs/OPERATIONS.md" in self.content

    def test_has_validation_section(self) -> None:
        assert "## Validation" in self.content

    def test_validation_lists_test_files(self) -> None:
        assert "test_repo_phase.py" in self.content

    def test_integration_state_section_present(self) -> None:
        assert "## Integration state" in self.content

    def test_integration_state_references_hyperspace_index(self) -> None:
        assert "hyperspace_index.json" in self.content

    def test_integration_state_references_orbital_hyperspace_index(self) -> None:
        assert "hyperspace_index_orbital.json" in self.content

    def test_does_not_reference_tools_core_only(self) -> None:
        assert "tools/core_only" not in self.content

    def test_launchers_section_present(self) -> None:
        assert "Launchers" in self.content

    def test_launchers_references_gh_coupling_script(self) -> None:
        assert "scripts/run_gh_repo_coupling.py" in self.content


# ---------------------------------------------------------------------------
# docs/OPERATIONS.md — reduced to single workflow
# ---------------------------------------------------------------------------


class TestOperationsDocumentation:
    """Verify that docs/OPERATIONS.md reflects the reduced operational scope."""

    @pytest.fixture(autouse=True)
    def load_content(self) -> None:
        assert OPERATIONS_DOC.is_file(), f"OPERATIONS.md not found: {OPERATIONS_DOC}"
        self.content = OPERATIONS_DOC.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        assert OPERATIONS_DOC.is_file()

    def test_documents_gh_repo_coupling_workflow(self) -> None:
        assert DOCUMENTED_WORKFLOW in self.content

    def test_does_not_document_ci_yml(self) -> None:
        assert "ci.yml" not in self.content

    def test_does_not_document_runtime_pipeline_yml(self) -> None:
        assert "runtime_pipeline.yml" not in self.content

    def test_does_not_document_package_yml(self) -> None:
        assert "package.yml" not in self.content

    def test_has_coupling_chain_section(self) -> None:
        assert "Coupling chain" in self.content or "coupling chain" in self.content.lower()

    def test_coupling_chain_lists_workflow_step(self) -> None:
        assert "gh_repo_coupling.yml" in self.content

    def test_coupling_chain_lists_script_step(self) -> None:
        assert "run_gh_repo_coupling.py" in self.content

    def test_coupling_chain_lists_module_step(self) -> None:
        assert "gh_coupling.py" in self.content

    def test_coupling_chain_lists_integration_output(self) -> None:
        assert "integration/" in self.content

    def test_has_documentation_rule_section(self) -> None:
        assert "Documentation rule" in self.content

    def test_has_scripts_section(self) -> None:
        assert "scripts/" in self.content

    def test_has_github_workflows_section(self) -> None:
        assert ".github/workflows/" in self.content

    def test_does_not_mention_tools_core_only(self) -> None:
        assert "tools/core_only" not in self.content

    def test_does_not_list_console_scripts(self) -> None:
        assert "ciel-sot-sync" not in self.content
        assert "ciel-sot-gui" not in self.content

    def test_scripts_section_references_stable_entrypoint(self) -> None:
        assert "run_gh_repo_coupling.py" in self.content

    def test_has_status_note(self) -> None:
        assert "Status note" in self.content or "status note" in self.content.lower()

    def test_documentation_rule_mentions_local_folder_docs(self) -> None:
        assert "local folder" in self.content.lower() or "folder documentation" in self.content.lower()

    def test_has_github_section(self) -> None:
        assert "### `.github/`" in self.content or "### .github/" in self.content or ".github/" in self.content


# ---------------------------------------------------------------------------
# packaging/README.md — simplified installer description
# ---------------------------------------------------------------------------


class TestPackagingReadme:
    """Verify packaging/README.md reflects the simplified 3-step installer description."""

    @pytest.fixture(autouse=True)
    def load_content(self) -> None:
        assert PACKAGING_README.is_file(), f"packaging/README.md not found: {PACKAGING_README}"
        self.content = PACKAGING_README.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        assert PACKAGING_README.is_file()

    def test_title_is_installers(self) -> None:
        assert "Installers" in self.content

    def test_describes_three_install_steps(self) -> None:
        assert "1." in self.content and "2." in self.content and "3." in self.content

    def test_step_1_installs_package(self) -> None:
        assert "ciel-sot-agent" in self.content

    def test_step_2_installs_llama_cpp_python(self) -> None:
        assert "llama-cpp-python" in self.content

    def test_step_3_downloads_gguf_model(self) -> None:
        assert "GGUF" in self.content or "gguf" in self.content.lower()

    def test_has_available_models_table(self) -> None:
        assert "tinyllama" in self.content.lower() or "TinyLlama" in self.content

    def test_models_table_includes_qwen_0_5b(self) -> None:
        assert "qwen2.5-0.5b-q4" in self.content

    def test_models_table_includes_qwen_1_5b(self) -> None:
        assert "qwen2.5-1.5b-q4" in self.content

    def test_models_table_includes_phi2(self) -> None:
        assert "phi-2-q4" in self.content

    def test_none_model_option_documented(self) -> None:
        assert "`none`" in self.content or "none" in self.content

    def test_has_quick_install_section(self) -> None:
        assert "Quick install" in self.content

    def test_quick_install_linux_macos_section(self) -> None:
        assert "Linux" in self.content and ("macOS" in self.content or "Mac" in self.content or "bash" in self.content)

    def test_quick_install_windows_section(self) -> None:
        assert "Windows" in self.content
        assert "install.ps1" in self.content

    def test_quick_install_deb_section(self) -> None:
        assert "deb" in self.content.lower() or ".deb" in self.content

    def test_mentions_ciel_sot_install_model(self) -> None:
        assert "ciel-sot-install-model" in self.content

    def test_model_storage_path_documented(self) -> None:
        assert "~/.local/share/ciel/models" in self.content or "CIEL_MODELS_DIR" in self.content

    def test_ciel_models_dir_env_var_documented(self) -> None:
        assert "CIEL_MODELS_DIR" in self.content

    def test_has_manual_model_management_section(self) -> None:
        assert "Manual model management" in self.content or "model management" in self.content.lower()

    def test_has_contents_section(self) -> None:
        assert "Contents" in self.content

    def test_contents_lists_install_sh(self) -> None:
        assert "install.sh" in self.content

    def test_contents_lists_install_ps1(self) -> None:
        assert "install.ps1" in self.content

    def test_windows_skip_model_option(self) -> None:
        assert "-Model none" in self.content

    def test_no_separate_three_surface_sections(self) -> None:
        assert "Packaging surfaces" not in self.content

    def test_no_ci_packaging_workflow_reference(self) -> None:
        assert "package.yml" not in self.content


# ---------------------------------------------------------------------------
# packaging/deb/README.md — updated Debian install instructions
# ---------------------------------------------------------------------------


class TestPackagingDebReadme:
    """Verify packaging/deb/README.md reflects the updated Debian install instructions."""

    @pytest.fixture(autouse=True)
    def load_content(self) -> None:
        assert DEB_README.is_file(), f"packaging/deb/README.md not found: {DEB_README}"
        self.content = DEB_README.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        assert DEB_README.is_file()

    def test_states_no_internet_required(self) -> None:
        assert "No internet" in self.content or "no internet" in self.content.lower() or "offline" in self.content.lower()

    def test_install_section_targets_linux_mint(self) -> None:
        assert "Linux Mint" in self.content

    def test_install_instructions_include_apt_install_f(self) -> None:
        assert "apt install -f" in self.content or "apt-get install -f" in self.content

    def test_mentions_ciel_sot_install_model(self) -> None:
        assert "ciel-sot-install-model" in self.content

    def test_model_storage_at_var_lib_ciel(self) -> None:
        assert "/var/lib/ciel/models" in self.content

    def test_no_longer_has_explicit_no_auto_download_paragraph(self) -> None:
        assert "the package does **not** automatically download a GGUF model" not in self.content

    def test_no_longer_has_removed_offline_clarification_block(self) -> None:
        assert "Important clarification" not in self.content

    def test_has_prerequisites_section(self) -> None:
        assert "Prerequisites" in self.content

    def test_has_building_section(self) -> None:
        assert "Building" in self.content or "building" in self.content.lower()

    def test_has_configuration_section(self) -> None:
        assert "Configuration" in self.content

    def test_has_running_gui_section(self) -> None:
        assert "Running the GUI" in self.content or "Running" in self.content

    def test_has_uninstalling_section(self) -> None:
        assert "Uninstalling" in self.content

    def test_uninstall_documents_dpkg_r(self) -> None:
        assert "dpkg -r ciel-sot-agent" in self.content

    def test_uninstall_documents_dpkg_purge(self) -> None:
        assert "dpkg -P ciel-sot-agent" in self.content

    def test_gui_served_on_port_5050(self) -> None:
        assert "5050" in self.content

    def test_package_structure_section_present(self) -> None:
        assert "Package structure" in self.content

    def test_postinst_mentioned(self) -> None:
        assert "postinst" in self.content

    def test_systemd_service_mentioned(self) -> None:
        assert "systemd" in self.content or "ciel-sot-gui.service" in self.content


# ---------------------------------------------------------------------------
# README.md — main repo README restructured
# ---------------------------------------------------------------------------


class TestMainReadme:
    """Verify main README.md reflects its post-PR restructured content."""

    @pytest.fixture(autouse=True)
    def load_content(self) -> None:
        assert MAIN_README.is_file(), f"README.md not found: {MAIN_README}"
        self.content = MAIN_README.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        assert MAIN_README.is_file()

    def test_new_subtitle_present(self) -> None:
        assert "General Quantum Consciousness System" in self.content

    def test_ciel_sot_agent_name_present(self) -> None:
        assert "CIEL-_SOT_Agent" in self.content

    def test_has_system_architecture_section(self) -> None:
        assert "System architecture" in self.content or "system architecture" in self.content.lower()

    def test_has_integration_kernel_subsystem(self) -> None:
        assert "Integration kernel" in self.content

    def test_has_github_coupling_subsystem(self) -> None:
        assert "GitHub coupling" in self.content or "github coupling" in self.content.lower()

    def test_has_orbital_runtime_subsystem(self) -> None:
        assert "Orbital runtime" in self.content or "orbital runtime" in self.content.lower()

    def test_has_orbital_bridge_subsystem(self) -> None:
        assert "Orbital bridge" in self.content or "orbital bridge" in self.content.lower()

    def test_has_sapiens_subsystem(self) -> None:
        assert "Sapiens" in self.content

    def test_has_gui_subsystem(self) -> None:
        assert "GUI" in self.content

    def test_has_role_in_ecosystem_section(self) -> None:
        assert "Role in the ecosystem" in self.content or "ecosystem" in self.content.lower()

    def test_lists_canon_repo(self) -> None:
        assert "canon" in self.content.lower() or "Seed of the Worlds" in self.content

    def test_lists_ciel_omega_demo(self) -> None:
        assert "ciel-omega-demo" in self.content

    def test_has_operational_flow_section(self) -> None:
        assert "Operational flow" in self.content or "operational flow" in self.content.lower()

    def test_operational_flow_describes_reduction_chain(self) -> None:
        assert "orbital state" in self.content.lower() or "bridge reduction" in self.content.lower()

    def test_has_couplings_section(self) -> None:
        assert "Couplings" in self.content or "couplings" in self.content.lower()

    def test_no_longer_has_repository_geometry_heading(self) -> None:
        assert "## Repository geometry" not in self.content

    def test_no_longer_has_four_numbered_layer_sections(self) -> None:
        assert "### 1. Native package layer" not in self.content

    def test_has_main_folders_section(self) -> None:
        assert "## Main folders" in self.content

    def test_main_folders_mentions_integration(self) -> None:
        assert "integration/" in self.content

    def test_main_folders_mentions_src(self) -> None:
        assert "src/ciel_sot_agent/" in self.content

    def test_has_existing_launchers_section(self) -> None:
        assert "Existing launchers" in self.content or "launchers" in self.content.lower()

    def test_existing_launchers_includes_gh_coupling_script(self) -> None:
        assert "run_gh_repo_coupling.py" in self.content

    def test_has_report_layers_section(self) -> None:
        assert "report layer" in self.content.lower() or "Existing report layers" in self.content

    def test_has_validation_layer_section(self) -> None:
        assert "Validation layer" in self.content or "validation" in self.content.lower()

    def test_integration_attractor_description_present(self) -> None:
        assert "Integration attractor" in self.content or "integration attractor" in self.content.lower()

    def test_final_note_present(self) -> None:
        assert "Final note" in self.content

    def test_live_integration_manifold_statement(self) -> None:
        assert "live integration manifold" in self.content

    def test_does_not_have_entry_points_for_orientation_section(self) -> None:
        assert "Entry points for orientation" not in self.content

    def test_does_not_list_all_old_execution_entrypoints(self) -> None:
        assert "ciel-sot-sync-v2" not in self.content or "Installed console entrypoints" not in self.content
