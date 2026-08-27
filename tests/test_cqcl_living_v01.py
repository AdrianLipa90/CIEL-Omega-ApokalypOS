import copy
import hashlib
import json

import pytest

from emotion.cqcl.living_compiler_v01 import CQCLLivingError, compile_living_program


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def fixture():
    crystal = {
        "schema": "PNV-T36-CRYSTAL-CONTEXT/0.1",
        "crystal_id": "11" * 32,
        "configuration_sha256": "22" * 32,
        "genesis_anchor_commitment": "33" * 32,
        "boot_epoch": 4,
        "phase_index": 18,
        "spinor_sheet": 0,
    }
    active = [{
        "term_id": f"CLX2-T-{i:03d}",
        "name": f"Term {i}",
        "phase_index": i + 1,
        "coherence": 0.96 - 0.002 * i,
        "phase": 0.01 * i,
        "informational_action": 0.001 + 1e-5 * i,
        "angular_distance": 0.2 + 0.001 * i,
        "semantic_equivalence": False,
        "authority_grant": False,
    } for i in range(16)]
    activation_core = {
        "schema": "PNV-NEXUS-ACTIVATION/0.1",
        "authority_class": "DERIVED_WORKING_STATE_BINDING",
        "authority_grant": False,
        "semantic_equivalence_grant": False,
        "nexus_generation_id": "44" * 32,
        "nexus_coherence": 0.91,
        "mean_informational_action": 0.00087,
        "crystal": {
            "crystal_id": crystal["crystal_id"],
            "configuration_sha256": crystal["configuration_sha256"],
            "boot_epoch": crystal["boot_epoch"],
            "phase_index": crystal["phase_index"],
            "spinor_sheet": crystal["spinor_sheet"],
            "source_object_id": "55" * 32,
        },
        "dictionary": {
            "repository": "AdrianLipa90/The-Consciousness-Dictionary",
            "branch": "feat/t36-identity-nexus-projection",
            "commit": "3aa1651da9735d94d2a9cbffec13203eeeedd502",
            "states": 548,
            "relations": 306,
            "state_sha256": "56d758c54f27323ef7edcf5164d224801f182ec83cda04216953cfaeda135501",
            "relation_sha256": "8484cd1314df4b18c21207b7fe234e71007e5c4c59aaf356cffd4abea0d36e8a",
        },
        "active_terms": active,
    }
    activation = {
        **activation_core,
        "activation_binding_id": hashlib.sha256(
            b"PNV-NEXUS-ACTIVATION/v0.1\x00" + canonical(activation_core)
        ).hexdigest(),
    }
    checkpoint = {
        "object_id": "66" * 32,
        "state_id": "77" * 32,
        "relation": "NEXUS_ACTIVATION",
        "metadata": {"t36_identity": crystal, "nexus_activation": activation},
    }
    htri = {
        "schema": "CQCL-LIVE-HTRI-BINDING/0.1",
        "source_class": "NATURAL_SYSTEM_STATE",
        "generation_id": "88" * 32,
        "coherence": 0.81,
        "heartbeat_age_ms": 12.0,
        "max_heartbeat_age_ms": 100.0,
        "live": True,
        "authority_grant": False,
    }
    return checkpoint, htri


def test_observation_only_compiles_without_fabricated_intention():
    cp, htri = fixture()
    p = compile_living_program(nexus_activation_checkpoint=cp, htri_binding=htri)
    assert p.status == "OBSERVATION_ONLY"
    assert p.intention_candidate is None
    assert p.execution_admitted is False
    assert p.authority_grant is False
    assert p.state_variables["coupled_coherence_candidate"] == pytest.approx((0.91 * 0.81) ** 0.5)
    assert len(p.active_terms) == 16


def test_structured_gremlin_candidate_remains_non_authoritative():
    cp, htri = fixture()
    p = compile_living_program(
        nexus_activation_checkpoint=cp,
        htri_binding=htri,
        intention_candidate={"source": "GREMLIN", "payload": {"relation": "candidate-path"}, "authority_grant": False},
    )
    assert p.status == "CANDIDATE_COMPILED"
    assert p.intention_candidate["source"] == "GREMLIN"
    assert p.intention_candidate["authority_grant"] is False
    assert p.execution_admitted is False


def test_program_id_is_deterministic():
    cp, htri = fixture()
    a = compile_living_program(nexus_activation_checkpoint=cp, htri_binding=htri)
    b = compile_living_program(nexus_activation_checkpoint=copy.deepcopy(cp), htri_binding=copy.deepcopy(htri))
    assert a.program_id == b.program_id


def test_stale_htri_fails_closed_without_default_coherence():
    cp, htri = fixture(); htri["heartbeat_age_ms"] = 101.0
    with pytest.raises(CQCLLivingError, match="stale"):
        compile_living_program(nexus_activation_checkpoint=cp, htri_binding=htri)


def test_non_natural_htri_source_fails_closed():
    cp, htri = fixture(); htri["source_class"] = "SYNTHETIC"
    with pytest.raises(CQCLLivingError, match="NATURAL_SYSTEM_STATE"):
        compile_living_program(nexus_activation_checkpoint=cp, htri_binding=htri)


def test_activation_tamper_fails_closed():
    cp, htri = fixture(); cp["metadata"]["nexus_activation"]["nexus_coherence"] = 0.2
    with pytest.raises(CQCLLivingError, match="binding hash"):
        compile_living_program(nexus_activation_checkpoint=cp, htri_binding=htri)


def test_candidate_authority_attempt_fails_closed():
    cp, htri = fixture()
    with pytest.raises(CQCLLivingError, match="authority"):
        compile_living_program(
            nexus_activation_checkpoint=cp,
            htri_binding=htri,
            intention_candidate={"source": "GREMLIN", "payload": {}, "authority_grant": True},
        )
