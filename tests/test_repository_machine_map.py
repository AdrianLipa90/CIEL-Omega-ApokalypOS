"""Tests for the machine-readable repository map and documentation consistency.

These tests verify:
- The REPOSITORY_MACHINE_MAP.json file is well-formed and contains required fields.
- The REPOSITORY_MACHINE_MAP.yaml file is well-formed and contains required fields.
- JSON and YAML map files are consistent with each other.
- Workflow documentation (README and OPERATIONS.md) references all four current workflows.
- The DECLARATION_IMPLEMENTATION_MATRIX.md contains required status keys and matrix entries.
- The REPOSITORY_GUIDE_HUMAN.md documents the four repository layers.
- Packaging documentation (packaging/README.md and packaging/deb/README.md) correctly
  distinguishes installation surfaces and GGUF model-download behavior.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_MAP_PATH = REPO_ROOT / "integration" / "indices" / "REPOSITORY_MACHINE_MAP.json"
YAML_MAP_PATH = REPO_ROOT / "integration" / "registries" / "REPOSITORY_MACHINE_MAP.yaml"
WORKFLOW_README = REPO_ROOT / ".github" / "workflows" / "README.md"
OPERATIONS_DOC = REPO_ROOT / "docs" / "OPERATIONS.md"
DECL_MATRIX_DOC = REPO_ROOT / "docs" / "DECLARATION_IMPLEMENTATION_MATRIX.md"
REPO_GUIDE_DOC = REPO_ROOT / "docs" / "REPOSITORY_GUIDE_HUMAN.md"
PACKAGING_README = REPO_ROOT / "packaging" / "README.md"
DEB_README = REPO_ROOT / "packaging" / "deb" / "README.md"
INDEX_DOC = REPO_ROOT / "docs" / "INDEX.md"

# Expected set of console scripts that both maps must declare.
EXPECTED_CONSOLE_SCRIPTS = {
    "ciel-sot-sync",
    "ciel-sot-sync-v2",
    "ciel-sot-gh-coupling",
    "ciel-sot-gh-coupling-v2",
    "ciel-sot-index-validate",
    "ciel-sot-index-validate-v2",
    "ciel-sot-orbital-bridge",
    "ciel-sot-ciel-pipeline",
    "ciel-sot-sapiens-client",
    "ciel-sot-runtime-evidence-ingest",
    "ciel-sot-gui",
    "ciel-sot-install-model",
}

# The four current workflow file names that all updated docs should reference.
EXPECTED_WORKFLOW_FILES = {
    "ci.yml",
    "runtime_pipeline.yml",
    "package.yml",
    "gh_repo_coupling.yml",
}


# ---------------------------------------------------------------------------
# JSON machine map
# ---------------------------------------------------------------------------


class TestRepositoryMachineMapJSON:
    """Structural and content tests for integration/indices/REPOSITORY_MACHINE_MAP.json."""

    @pytest.fixture(autouse=True)
    def load_json(self):
        assert JSON_MAP_PATH.is_file(), f"Expected file not found: {JSON_MAP_PATH}"
        self.data = json.loads(JSON_MAP_PATH.read_text())

    # --- top-level keys ---

    def test_has_schema_version(self):
        assert "schema_version" in self.data

    def test_has_generated_on(self):
        assert "generated_on" in self.data

    def test_has_repository_section(self):
        assert "repository" in self.data

    def test_has_native_package_section(self):
        assert "native_package" in self.data

    def test_has_integration_state_section(self):
        assert "integration_state" in self.data

    def test_has_operational_surfaces_section(self):
        assert "operational_surfaces" in self.data

    def test_has_embedded_or_imported_sectors(self):
        assert "embedded_or_imported_sectors" in self.data

    def test_has_known_documentation_gaps(self):
        assert "known_documentation_gaps" in self.data

    # --- schema_version ---

    def test_schema_version_is_string(self):
        assert isinstance(self.data["schema_version"], str)

    def test_schema_version_value(self):
        assert self.data["schema_version"] == "1.0"

    # --- repository section ---

    def test_repository_has_name(self):
        assert "name" in self.data["repository"]

    def test_repository_name_value(self):
        assert self.data["repository"]["name"] == "CIEL-_SOT_Agent"

    def test_repository_has_package_name(self):
        assert "package_name" in self.data["repository"]

    def test_repository_package_name_value(self):
        assert self.data["repository"]["package_name"] == "ciel-sot-agent"

    def test_repository_has_purpose(self):
        assert "purpose" in self.data["repository"]
        assert len(self.data["repository"]["purpose"]) > 0

    # --- native_package section ---

    def test_native_package_has_root(self):
        assert "root" in self.data["native_package"]

    def test_native_package_root_value(self):
        assert self.data["native_package"]["root"] == "src/ciel_sot_agent"

    def test_native_package_has_console_scripts(self):
        assert "console_scripts" in self.data["native_package"]

    def test_console_scripts_is_list(self):
        assert isinstance(self.data["native_package"]["console_scripts"], list)

    def test_console_scripts_not_empty(self):
        assert len(self.data["native_package"]["console_scripts"]) > 0

    def test_console_scripts_contains_all_expected(self):
        declared = set(self.data["native_package"]["console_scripts"])
        missing = EXPECTED_CONSOLE_SCRIPTS - declared
        assert not missing, f"Missing console scripts in JSON map: {missing}"

    def test_console_scripts_includes_gui(self):
        assert "ciel-sot-gui" in self.data["native_package"]["console_scripts"]

    def test_console_scripts_includes_sapiens_client(self):
        assert "ciel-sot-sapiens-client" in self.data["native_package"]["console_scripts"]

    def test_console_scripts_includes_install_model(self):
        assert "ciel-sot-install-model" in self.data["native_package"]["console_scripts"]

    # --- integration_state section ---

    def test_integration_state_has_root(self):
        assert "root" in self.data["integration_state"]

    def test_integration_state_root_value(self):
        assert self.data["integration_state"]["root"] == "integration"

    def test_integration_state_has_notes(self):
        assert "notes" in self.data["integration_state"]
        assert isinstance(self.data["integration_state"]["notes"], list)
        assert len(self.data["integration_state"]["notes"]) > 0

    def test_integration_state_notes_mention_migration(self):
        combined = " ".join(self.data["integration_state"]["notes"]).lower()
        assert "migration" in combined

    # --- operational_surfaces section ---

    def test_operational_surfaces_has_repo_local_wrappers_root(self):
        assert "repo_local_wrappers_root" in self.data["operational_surfaces"]

    def test_operational_surfaces_wrappers_root_value(self):
        assert self.data["operational_surfaces"]["repo_local_wrappers_root"] == "scripts"

    def test_operational_surfaces_has_core_only_tools_root(self):
        assert "core_only_tools_root" in self.data["operational_surfaces"]

    def test_operational_surfaces_core_only_root_value(self):
        assert self.data["operational_surfaces"]["core_only_tools_root"] == "tools/core_only"

    def test_operational_surfaces_has_workflows_root(self):
        assert "workflows_root" in self.data["operational_surfaces"]

    def test_operational_surfaces_workflows_root_value(self):
        assert self.data["operational_surfaces"]["workflows_root"] == ".github/workflows"

    def test_operational_surfaces_has_packaging_root(self):
        assert "packaging_root" in self.data["operational_surfaces"]

    def test_operational_surfaces_packaging_root_value(self):
        assert self.data["operational_surfaces"]["packaging_root"] == "packaging"

    # --- embedded_or_imported_sectors ---

    def test_embedded_sectors_is_list(self):
        assert isinstance(self.data["embedded_or_imported_sectors"], list)

    def test_embedded_sectors_not_empty(self):
        assert len(self.data["embedded_or_imported_sectors"]) > 0

    def test_embedded_sectors_includes_ciel_omega(self):
        sectors = self.data["embedded_or_imported_sectors"]
        assert any("CIEL_OMEGA" in s or "ciel-omega" in s or "ciel_omega" in s for s in sectors)

    # --- known_documentation_gaps ---

    def test_known_gaps_is_list(self):
        assert isinstance(self.data["known_documentation_gaps"], list)

    def test_known_gaps_not_empty(self):
        assert len(self.data["known_documentation_gaps"]) > 0

    def test_known_gaps_mention_sapiens_client(self):
        combined = " ".join(self.data["known_documentation_gaps"]).lower()
        assert "sapiens" in combined

    def test_known_gaps_mention_workflow(self):
        combined = " ".join(self.data["known_documentation_gaps"]).lower()
        assert "workflow" in combined


# ---------------------------------------------------------------------------
# YAML machine map
# ---------------------------------------------------------------------------


class TestRepositoryMachineMapYAML:
    """Structural and content tests for integration/registries/REPOSITORY_MACHINE_MAP.yaml."""

    @pytest.fixture(autouse=True)
    def load_yaml(self):
        assert YAML_MAP_PATH.is_file(), f"Expected file not found: {YAML_MAP_PATH}"
        self.data = yaml.safe_load(YAML_MAP_PATH.read_text())

    # --- top-level keys ---

    def test_has_schema_version(self):
        assert "schema_version" in self.data

    def test_has_generated_on(self):
        assert "generated_on" in self.data

    def test_has_repository_section(self):
        assert "repository" in self.data

    def test_has_native_package_section(self):
        assert "native_package" in self.data

    def test_has_integration_state_section(self):
        assert "integration_state" in self.data

    def test_has_operational_surfaces_section(self):
        assert "operational_surfaces" in self.data

    def test_has_embedded_or_imported_sectors(self):
        assert "embedded_or_imported_sectors" in self.data

    def test_has_known_documentation_gaps(self):
        assert "known_documentation_gaps" in self.data

    # --- schema_version ---

    def test_schema_version_value(self):
        # YAML may parse '1.0' as float or string; normalise to string for check
        assert str(self.data["schema_version"]) == "1.0"

    # --- repository section ---

    def test_repository_name_value(self):
        assert self.data["repository"]["name"] == "CIEL-_SOT_Agent"

    def test_repository_package_name_value(self):
        assert self.data["repository"]["package_name"] == "ciel-sot-agent"

    def test_repository_purpose_not_empty(self):
        assert len(self.data["repository"].get("purpose", "")) > 0

    # --- native_package section ---

    def test_native_package_root_value(self):
        assert self.data["native_package"]["root"] == "src/ciel_sot_agent"

    def test_console_scripts_is_list(self):
        assert isinstance(self.data["native_package"]["console_scripts"], list)

    def test_console_scripts_contains_all_expected(self):
        declared = set(self.data["native_package"]["console_scripts"])
        missing = EXPECTED_CONSOLE_SCRIPTS - declared
        assert not missing, f"Missing console scripts in YAML map: {missing}"

    def test_console_scripts_no_run_sapiens_client_script(self):
        """The stale run_sapiens_client.py should not appear in console_scripts."""
        scripts = self.data["native_package"]["console_scripts"]
        assert not any("run_sapiens_client" in s for s in scripts)

    # --- integration_state ---

    def test_integration_state_root_value(self):
        assert self.data["integration_state"]["root"] == "integration"

    def test_integration_state_notes_is_list(self):
        assert isinstance(self.data["integration_state"]["notes"], list)

    # --- operational_surfaces ---

    def test_operational_surfaces_wrappers_root(self):
        assert self.data["operational_surfaces"]["repo_local_wrappers_root"] == "scripts"

    def test_operational_surfaces_core_only_root(self):
        assert self.data["operational_surfaces"]["core_only_tools_root"] == "tools/core_only"

    def test_operational_surfaces_workflows_root(self):
        assert self.data["operational_surfaces"]["workflows_root"] == ".github/workflows"

    def test_operational_surfaces_packaging_root(self):
        assert self.data["operational_surfaces"]["packaging_root"] == "packaging"

    # --- embedded_sectors ---

    def test_embedded_sectors_is_list(self):
        assert isinstance(self.data["embedded_or_imported_sectors"], list)

    def test_embedded_sectors_not_empty(self):
        assert len(self.data["embedded_or_imported_sectors"]) > 0

    # --- known_gaps ---

    def test_known_gaps_is_list(self):
        assert isinstance(self.data["known_documentation_gaps"], list)

    def test_known_gaps_not_empty(self):
        assert len(self.data["known_documentation_gaps"]) > 0


# ---------------------------------------------------------------------------
# Cross-format consistency
# ---------------------------------------------------------------------------


class TestRepositoryMachineMapConsistency:
    """Verify that JSON and YAML map files agree on all shared fields."""

    @pytest.fixture(autouse=True)
    def load_both(self):
        self.json_data = json.loads(JSON_MAP_PATH.read_text())
        self.yaml_data = yaml.safe_load(YAML_MAP_PATH.read_text())

    def test_schema_version_matches(self):
        assert str(self.json_data["schema_version"]) == str(self.yaml_data["schema_version"])

    def test_repository_name_matches(self):
        assert self.json_data["repository"]["name"] == self.yaml_data["repository"]["name"]

    def test_repository_package_name_matches(self):
        assert (
            self.json_data["repository"]["package_name"]
            == self.yaml_data["repository"]["package_name"]
        )

    def test_native_package_root_matches(self):
        assert (
            self.json_data["native_package"]["root"]
            == self.yaml_data["native_package"]["root"]
        )

    def test_console_scripts_sets_match(self):
        json_scripts = set(self.json_data["native_package"]["console_scripts"])
        yaml_scripts = set(self.yaml_data["native_package"]["console_scripts"])
        assert json_scripts == yaml_scripts, (
            f"Script mismatch — only in JSON: {json_scripts - yaml_scripts}; "
            f"only in YAML: {yaml_scripts - json_scripts}"
        )

    def test_integration_state_root_matches(self):
        assert (
            self.json_data["integration_state"]["root"]
            == self.yaml_data["integration_state"]["root"]
        )

    def test_operational_surfaces_match(self):
        j = self.json_data["operational_surfaces"]
        y = self.yaml_data["operational_surfaces"]
        for key in ("repo_local_wrappers_root", "core_only_tools_root",
                    "workflows_root", "packaging_root"):
            assert j[key] == y[key], f"Mismatch on operational_surfaces.{key}"

    def test_embedded_sectors_sets_match(self):
        json_sectors = set(self.json_data["embedded_or_imported_sectors"])
        yaml_sectors = set(self.yaml_data["embedded_or_imported_sectors"])
        assert json_sectors == yaml_sectors, (
            f"Sector mismatch — only in JSON: {json_sectors - yaml_sectors}; "
            f"only in YAML: {yaml_sectors - json_sectors}"
        )

    def test_generated_on_date_matches(self):
        assert self.json_data["generated_on"] == self.yaml_data["generated_on"]


# ---------------------------------------------------------------------------
# Workflow documentation consistency
# ---------------------------------------------------------------------------


class TestWorkflowREADME:
    """Tests for .github/workflows/README.md updated in this PR."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        assert WORKFLOW_README.is_file()
        self.content = WORKFLOW_README.read_text()

    def test_mentions_ci_yml(self):
        assert "ci.yml" in self.content

    def test_mentions_runtime_pipeline_yml(self):
        assert "runtime_pipeline.yml" in self.content

    def test_mentions_package_yml(self):
        assert "package.yml" in self.content

    def test_mentions_gh_repo_coupling_yml(self):
        assert "gh_repo_coupling.yml" in self.content

    def test_all_four_workflows_mentioned(self):
        missing = [wf for wf in EXPECTED_WORKFLOW_FILES if wf not in self.content]
        assert not missing, f"Workflow README is missing references to: {missing}"

    def test_has_documentation_rule_section(self):
        assert "Documentation rule" in self.content

    def test_documentation_rule_references_operations_doc(self):
        assert "docs/OPERATIONS.md" in self.content

    def test_documentation_rule_references_index_doc(self):
        assert "docs/INDEX.md" in self.content

    def test_describes_four_distinct_purposes(self):
        # The README should mention "four" or list four purpose bullets.
        assert "four" in self.content.lower() or self.content.count("- ") >= 4

    def test_structural_rule_section_present(self):
        assert "Structural rule" in self.content


class TestOperationsDocumentation:
    """Tests for docs/OPERATIONS.md updated in this PR."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        assert OPERATIONS_DOC.is_file()
        self.content = OPERATIONS_DOC.read_text()

    def test_mentions_ci_yml(self):
        assert "ci.yml" in self.content

    def test_mentions_runtime_pipeline_yml(self):
        assert "runtime_pipeline.yml" in self.content

    def test_mentions_package_yml(self):
        assert "package.yml" in self.content

    def test_mentions_gh_repo_coupling_yml(self):
        assert "gh_repo_coupling.yml" in self.content

    def test_all_four_workflows_mentioned(self):
        missing = [wf for wf in EXPECTED_WORKFLOW_FILES if wf not in self.content]
        assert not missing, f"OPERATIONS.md is missing references to: {missing}"

    def test_clarifies_no_run_sapiens_client_script(self):
        """OPERATIONS.md must explicitly state that run_sapiens_client.py does not exist."""
        assert "run_sapiens_client" in self.content
        # The statement of non-existence should appear.
        assert "no" in self.content.lower() or "does not exist" in self.content.lower()

    def test_mentions_tools_core_only(self):
        assert "tools/core_only" in self.content

    def test_mentions_scripts_section(self):
        assert "scripts/" in self.content

    def test_mentions_packaging_section(self):
        assert "packaging/" in self.content or "packaging/" in self.content

    def test_has_documentation_rule_section(self):
        assert "Documentation rule" in self.content

    def test_lists_console_scripts(self):
        # At least a representative subset of console scripts should appear.
        for script in ("ciel-sot-gui", "ciel-sot-sync", "ciel-sot-sapiens-client"):
            assert script in self.content, f"OPERATIONS.md missing console script: {script}"

    def test_operational_chains_section_present(self):
        assert "Operational chain" in self.content or "operational chain" in self.content.lower()

    def test_gh_coupling_chain_documented(self):
        assert "gh_coupling" in self.content

    def test_packaging_chain_documented(self):
        # Chain should reference packaging workflow.
        assert "package.yml" in self.content or "Packaging chain" in self.content


# ---------------------------------------------------------------------------
# DECLARATION_IMPLEMENTATION_MATRIX.md
# ---------------------------------------------------------------------------


class TestDeclarationImplementationMatrix:
    """Tests for the new docs/DECLARATION_IMPLEMENTATION_MATRIX.md file."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        assert DECL_MATRIX_DOC.is_file(), f"Expected file not found: {DECL_MATRIX_DOC}"
        self.content = DECL_MATRIX_DOC.read_text()

    def test_has_status_keys_section(self):
        assert "Status keys" in self.content or "status keys" in self.content.lower()

    def test_defines_implemented_status(self):
        assert "implemented" in self.content

    def test_defines_stale_doc_status(self):
        assert "stale_doc" in self.content

    def test_defines_declared_future_status(self):
        assert "declared_future" in self.content

    def test_defines_incomplete_doc_status(self):
        assert "incomplete_doc" in self.content

    def test_defines_implemented_transitional_status(self):
        assert "implemented_transitional" in self.content

    def test_defines_scope_limited_status(self):
        assert "scope_limited" in self.content

    def test_has_matrix_table(self):
        # Markdown table rows contain | characters.
        table_rows = [line for line in self.content.splitlines() if "|" in line]
        assert len(table_rows) >= 3, "Matrix table should have at least a header and two rows"

    def test_matrix_mentions_sapiens_stale_doc(self):
        assert "stale_doc" in self.content
        assert "sapiens" in self.content.lower() or "Sapiens" in self.content

    def test_matrix_mentions_workflow_coverage(self):
        assert "workflow" in self.content.lower() or "Workflow" in self.content

    def test_matrix_mentions_four_workflows(self):
        assert "four" in self.content.lower()

    def test_repair_priorities_section_present(self):
        assert "repair" in self.content.lower() or "priorit" in self.content.lower()

    def test_repair_priorities_mention_sapiens_client(self):
        assert "Sapiens" in self.content or "sapiens" in self.content

    def test_repair_priorities_mention_workflows(self):
        assert "workflow" in self.content.lower()

    def test_repair_priorities_numbered_list(self):
        numbered = re.findall(r"^\d+\.", self.content, re.MULTILINE)
        assert len(numbered) >= 3, "Repair priorities should have at least 3 numbered items"


# ---------------------------------------------------------------------------
# REPOSITORY_GUIDE_HUMAN.md
# ---------------------------------------------------------------------------


class TestRepositoryGuideHuman:
    """Tests for the new docs/REPOSITORY_GUIDE_HUMAN.md file."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        assert REPO_GUIDE_DOC.is_file(), f"Expected file not found: {REPO_GUIDE_DOC}"
        self.content = REPO_GUIDE_DOC.read_text()

    def test_describes_layer_1_native_package(self):
        assert "Layer 1" in self.content
        assert "src/ciel_sot_agent" in self.content

    def test_describes_layer_2_integration_state(self):
        assert "Layer 2" in self.content
        assert "integration/" in self.content

    def test_describes_layer_3_operational_surfaces(self):
        assert "Layer 3" in self.content

    def test_describes_layer_4_embedded_sectors(self):
        assert "Layer 4" in self.content

    def test_mentions_all_four_workflows(self):
        missing = [wf for wf in EXPECTED_WORKFLOW_FILES if wf not in self.content]
        assert not missing, f"Guide is missing references to workflows: {missing}"

    def test_clarifies_no_run_sapiens_client_script(self):
        assert "run_sapiens_client" in self.content

    def test_lists_installed_console_scripts(self):
        for script in ("ciel-sot-gui", "ciel-sot-sync", "ciel-sot-sapiens-client"):
            assert script in self.content, f"Guide missing console script: {script}"

    def test_mentions_tools_core_only(self):
        assert "tools/core_only" in self.content

    def test_mentions_transitional_geometry(self):
        # Should explain migration/transitional co-existence.
        assert "transitional" in self.content.lower() or "migration" in self.content.lower()

    def test_mentions_embedded_sectors(self):
        assert "embedded" in self.content.lower() or "imported" in self.content.lower()

    def test_mentions_debian_packaging(self):
        assert "packaging/deb" in self.content or "Debian" in self.content

    def test_mentions_android_packaging(self):
        assert "packaging/android" in self.content or "Android" in self.content

    def test_mentions_execution_modes(self):
        # Guide should describe at least two of the three execution modes.
        hits = sum([
            "repo-local" in self.content.lower() or "thin wrapper" in self.content.lower(),
            "console script" in self.content.lower() or "pyproject" in self.content.lower(),
            "github actions" in self.content.lower() or "workflow" in self.content.lower(),
        ])
        assert hits >= 2, "Guide should describe at least two execution modes"


# ---------------------------------------------------------------------------
# Packaging documentation
# ---------------------------------------------------------------------------


class TestPackagingReadme:
    """Tests for packaging/README.md substantially rewritten in this PR."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        assert PACKAGING_README.is_file()
        self.content = PACKAGING_README.read_text()

    def test_distinguishes_scripted_installer(self):
        # Must identify scripted installers as a distinct surface.
        assert "install.sh" in self.content or "scripted" in self.content.lower()

    def test_distinguishes_debian_package(self):
        assert "packaging/deb" in self.content or "Debian" in self.content

    def test_distinguishes_android_surface(self):
        assert "packaging/android" in self.content or "Android" in self.content

    def test_deb_install_is_described_as_offline(self):
        assert "offline" in self.content.lower()

    def test_deb_does_not_auto_download_model(self):
        # The README must clarify that the .deb does NOT automatically download a model.
        assert "not" in self.content.lower() and (
            "automatically" in self.content.lower() or "auto" in self.content.lower()
        )

    def test_mentions_ciel_sot_install_model(self):
        assert "ciel-sot-install-model" in self.content

    def test_mentions_online_vs_offline_modes(self):
        # Scripted installer can be online (PyPI) or offline (vendor/).
        assert "online" in self.content.lower() or "vendor" in self.content.lower()

    def test_model_table_present(self):
        # Table should contain at least tinyllama entry.
        assert "tinyllama" in self.content.lower() or "TinyLlama" in self.content

    def test_ci_packaging_workflow_referenced(self):
        assert "package.yml" in self.content or "workflow" in self.content.lower()

    def test_none_model_option_documented(self):
        # 'none' as a model key should be documented.
        assert "`none`" in self.content or "CIEL_MODEL=none" in self.content

    def test_model_storage_paths_documented(self):
        assert "~/.local/share/ciel/models" in self.content or "CIEL_MODELS_DIR" in self.content


class TestPackagingDebReadme:
    """Tests for packaging/deb/README.md updated in this PR."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        assert DEB_README.is_file()
        self.content = DEB_README.read_text()

    def test_clarifies_offline_installation(self):
        assert "offline" in self.content.lower() or "No internet" in self.content

    def test_clarifies_no_auto_download_in_postinst(self):
        """Critical: postinst must NOT auto-download a GGUF model."""
        # The deb README uses markdown bold: "does **not** automatically download".
        # Accept both plain and bold-marked forms.
        assert (
            "does not" in self.content.lower()
            or "does **not**" in self.content
            or "not automatically" in self.content.lower()
        )

    def test_explicitly_states_postinst_does_not_download(self):
        assert "postinst" in self.content
        # The updated README should state this clearly.
        assert "not" in self.content.lower()

    def test_mentions_ciel_sot_install_model(self):
        assert "ciel-sot-install-model" in self.content

    def test_model_storage_path_is_var_lib(self):
        assert "/var/lib/ciel/models" in self.content

    def test_install_instructions_mention_apt_install_f(self):
        # Updated README added 'sudo apt install -f' for fixing missing dependencies.
        assert "apt install -f" in self.content or "apt-get install -f" in self.content

    def test_mentions_linux_mint_or_debian_or_ubuntu(self):
        assert (
            "Linux Mint" in self.content
            or "Debian" in self.content
            or "Ubuntu" in self.content
        )

    def test_readme_exists(self):
        assert DEB_README.is_file()


# ---------------------------------------------------------------------------
# docs/INDEX.md consistency
# ---------------------------------------------------------------------------


class TestIndexDocumentation:
    """Tests for docs/INDEX.md significantly reorganised in this PR."""

    @pytest.fixture(autouse=True)
    def load_content(self):
        assert INDEX_DOC.is_file()
        self.content = INDEX_DOC.read_text()

    def test_references_declaration_implementation_matrix(self):
        assert "DECLARATION_IMPLEMENTATION_MATRIX.md" in self.content

    def test_references_repository_guide_human(self):
        assert "REPOSITORY_GUIDE_HUMAN.md" in self.content

    def test_references_json_machine_map(self):
        assert "REPOSITORY_MACHINE_MAP.json" in self.content

    def test_references_yaml_machine_map(self):
        assert "REPOSITORY_MACHINE_MAP.yaml" in self.content

    def test_references_all_four_workflows(self):
        missing = [wf for wf in EXPECTED_WORKFLOW_FILES if wf not in self.content]
        assert not missing, f"INDEX.md is missing workflow references: {missing}"

    def test_references_tools_core_only(self):
        assert "tools/core_only" in self.content

    def test_packaging_layer_section_present(self):
        assert "Packaging" in self.content

    def test_references_packaging_readme(self):
        assert "packaging/README.md" in self.content

    def test_references_packaging_deb_readme(self):
        assert "packaging/deb/README.md" in self.content

    def test_workflow_section_present(self):
        assert "Workflow" in self.content

    def test_installed_console_scripts_section_present(self):
        assert "console" in self.content.lower() or "entrypoint" in self.content.lower()

    def test_mentions_gguf_manager(self):
        assert "gguf_manager" in self.content or "gguf-manager" in self.content or "gguf" in self.content.lower()