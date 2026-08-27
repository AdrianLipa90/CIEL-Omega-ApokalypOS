"""CQCL vNext: compile current living state into a bounded intention-program candidate.

Inputs are explicit State Memory / Identity NEXUS evidence plus an admitted live HTRI
binding. There is no filesystem fallback and no default coherence value.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping, Optional, Sequence

from .living_program_v01 import CQCL_Living_Program


SCHEMA = "CQCL-LIVING-PROGRAM/0.1"
HTRI_SCHEMA = "CQCL-LIVE-HTRI-BINDING/0.1"
ACTIVATION_SCHEMA = "PNV-NEXUS-ACTIVATION/0.1"
MAX_ACTIVE_TERMS = 16


class CQCLLivingError(ValueError):
    pass


def _canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hex(value: str, nbytes: int, name: str) -> str:
    v = str(value).lower()
    if len(v) != nbytes * 2:
        raise CQCLLivingError(f"{name} must encode {nbytes} bytes")
    try:
        bytes.fromhex(v)
    except ValueError as exc:
        raise CQCLLivingError(f"{name} must be hex") from exc
    return v


def _finite(value: Any, name: str) -> float:
    x = float(value)
    if not math.isfinite(x):
        raise CQCLLivingError(f"{name} must be finite")
    return x


def _validate_active_terms(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if len(rows) > MAX_ACTIVE_TERMS:
        raise CQCLLivingError("NEXUS activation active set exceeds v0.1 bound")
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for raw in rows:
        term_id = str(raw["term_id"])
        if not term_id or term_id in seen:
            raise CQCLLivingError("active term IDs must be non-empty and unique")
        seen.add(term_id)
        coherence = _finite(raw["coherence"], f"{term_id}.coherence")
        distance = _finite(raw["angular_distance"], f"{term_id}.angular_distance")
        if not 0.0 <= coherence <= 1.0:
            raise CQCLLivingError("active coherence outside [0,1]")
        if distance < 0.0:
            raise CQCLLivingError("active angular distance must be non-negative")
        if bool(raw.get("authority_grant", False)):
            raise CQCLLivingError("active term attempted authority grant")
        if bool(raw.get("semantic_equivalence", False)):
            raise CQCLLivingError("active term attempted semantic equivalence")
        out.append({
            "term_id": term_id,
            "name": str(raw.get("name", term_id)),
            "phase_index": int(raw.get("phase_index", 0)),
            "coherence": coherence,
            "phase": _finite(raw["phase"], f"{term_id}.phase"),
            "informational_action": _finite(raw["informational_action"], f"{term_id}.informational_action"),
            "angular_distance": distance,
            "semantic_equivalence": False,
            "authority_grant": False,
        })
    return out


def _verify_activation_binding(raw: Mapping[str, Any]) -> dict[str, Any]:
    if raw.get("schema") != ACTIVATION_SCHEMA:
        raise CQCLLivingError("unsupported NEXUS activation schema")
    if raw.get("authority_class") != "DERIVED_WORKING_STATE_BINDING":
        raise CQCLLivingError("invalid NEXUS activation authority class")
    if raw.get("authority_grant") is not False or raw.get("semantic_equivalence_grant") is not False:
        raise CQCLLivingError("NEXUS activation attempted promotion")
    core = dict(raw)
    supplied = _hex(core.pop("activation_binding_id"), 32, "activation_binding_id")
    expected = hashlib.sha256(b"PNV-NEXUS-ACTIVATION/v0.1\x00" + _canonical(core)).hexdigest()
    if supplied != expected:
        raise CQCLLivingError("NEXUS activation binding hash mismatch")
    dictionary = raw["dictionary"]
    _hex(dictionary["commit"], 20, "dictionary.commit")
    _hex(dictionary["state_sha256"], 32, "dictionary.state_sha256")
    _hex(dictionary["relation_sha256"], 32, "dictionary.relation_sha256")
    if int(dictionary["states"]) <= 0 or int(dictionary["relations"]) < 0:
        raise CQCLLivingError("invalid Dictionary counts")
    _validate_active_terms(raw.get("active_terms", ()))
    return dict(raw)


def _activation_checkpoint(checkpoint: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if checkpoint.get("relation") != "NEXUS_ACTIVATION":
        raise CQCLLivingError("State Memory checkpoint must be NEXUS_ACTIVATION")
    object_id = _hex(checkpoint["object_id"], 32, "activation checkpoint object_id")
    try:
        crystal = dict(checkpoint["metadata"]["t36_identity"])
        activation = _verify_activation_binding(checkpoint["metadata"]["nexus_activation"])
    except (KeyError, TypeError) as exc:
        raise CQCLLivingError("State Memory checkpoint is missing living-memory bindings") from exc
    if crystal.get("schema") != "PNV-T36-CRYSTAL-CONTEXT/0.1":
        raise CQCLLivingError("unsupported T36 crystal context")
    phase_index = int(crystal["phase_index"])
    if int(crystal.get("spinor_sheet", phase_index & 1)) != (phase_index & 1):
        raise CQCLLivingError("T36 spinor sheet mismatch")
    if activation["crystal"]["crystal_id"] != crystal["crystal_id"]:
        raise CQCLLivingError("activation/crystal CRYSTAL_ID mismatch")
    if activation["crystal"]["configuration_sha256"] != crystal["configuration_sha256"]:
        raise CQCLLivingError("activation/crystal configuration mismatch")
    if int(activation["crystal"]["boot_epoch"]) != int(crystal["boot_epoch"]):
        raise CQCLLivingError("activation/crystal boot epoch mismatch")
    if int(activation["crystal"]["phase_index"]) != phase_index:
        raise CQCLLivingError("activation/crystal phase index mismatch")
    if int(activation["crystal"].get("spinor_sheet", phase_index & 1)) != (phase_index & 1):
        raise CQCLLivingError("activation/crystal spinor sheet mismatch")
    return {"object_id": object_id, **dict(checkpoint)}, activation


def _htri(binding: Mapping[str, Any]) -> dict[str, Any]:
    if binding.get("schema") != HTRI_SCHEMA:
        raise CQCLLivingError("unsupported live HTRI binding schema")
    if binding.get("source_class") != "NATURAL_SYSTEM_STATE":
        raise CQCLLivingError("HTRI source must be NATURAL_SYSTEM_STATE")
    if binding.get("live") is not True:
        raise CQCLLivingError("HTRI binding is not live")
    if binding.get("authority_grant") is not False:
        raise CQCLLivingError("HTRI binding attempted authority grant")
    coherence = _finite(binding["coherence"], "htri.coherence")
    if not 0.0 <= coherence <= 1.0:
        raise CQCLLivingError("htri.coherence outside [0,1]")
    age = _finite(binding["heartbeat_age_ms"], "htri.heartbeat_age_ms")
    max_age = _finite(binding["max_heartbeat_age_ms"], "htri.max_heartbeat_age_ms")
    if age < 0.0 or max_age <= 0.0 or age > max_age:
        raise CQCLLivingError("HTRI heartbeat is stale")
    return {
        "schema": HTRI_SCHEMA,
        "source_class": "NATURAL_SYSTEM_STATE",
        "generation_id": _hex(binding["generation_id"], 32, "htri.generation_id"),
        "coherence": coherence,
        "heartbeat_age_ms": age,
        "max_heartbeat_age_ms": max_age,
        "live": True,
        "authority_grant": False,
    }


def _candidate(candidate: Optional[Mapping[str, Any]]) -> Optional[dict[str, Any]]:
    if candidate is None:
        return None
    if bool(candidate.get("authority_grant", False)):
        raise CQCLLivingError("intention candidate attempted authority grant")
    source = str(candidate.get("source", ""))
    if source not in {"GREMLIN", "EXPLICIT_CONTEXT", "NEXUS"}:
        raise CQCLLivingError("unsupported intention candidate source")
    payload = candidate.get("payload")
    if not isinstance(payload, Mapping):
        raise CQCLLivingError("intention candidate payload must be a mapping")
    core = {"source": source, "payload": dict(payload), "authority_grant": False}
    return {**core, "candidate_id": hashlib.sha256(b"CQCL-CANDIDATE/v0.1\x00" + _canonical(core)).hexdigest()}


def compile_living_program(
    *,
    nexus_activation_checkpoint: Mapping[str, Any],
    htri_binding: Mapping[str, Any],
    intention_candidate: Optional[Mapping[str, Any]] = None,
) -> CQCL_Living_Program:
    checkpoint, activation = _activation_checkpoint(nexus_activation_checkpoint)
    htri = _htri(htri_binding)
    candidate = _candidate(intention_candidate)

    active_terms = _validate_active_terms(activation.get("active_terms", ()))
    values = [row["coherence"] for row in active_terms]
    active_mean = math.fsum(values) / len(values) if values else 0.0
    active_max = max(values) if values else 0.0

    nexus_coherence = _finite(activation["nexus_coherence"], "nexus_coherence")
    if not 0.0 <= nexus_coherence <= 1.0:
        raise CQCLLivingError("nexus_coherence outside [0,1]")
    # Parameter-free bounded coupling statistic. It remains evidence only.
    coupled_coherence = math.sqrt(nexus_coherence * htri["coherence"])

    crystal = dict(activation["crystal"])
    dictionary = dict(activation["dictionary"])
    semantic_tree = {
        "root": "CURRENT_RELATIONAL_INTENTION_STATE",
        "source_activation_object_id": checkpoint["object_id"],
        "nexus_generation_id": activation["nexus_generation_id"],
        "active_term_ids": [row["term_id"] for row in active_terms],
        "candidate_id": None if candidate is None else candidate["candidate_id"],
        "dictionary_compile": {
            "commit": dictionary["commit"],
            "state_sha256": dictionary["state_sha256"],
            "relation_sha256": dictionary["relation_sha256"],
        },
    }
    state_variables = {
        "nexus_coherence": nexus_coherence,
        "htri_coherence": htri["coherence"],
        "coupled_coherence_candidate": coupled_coherence,
        "active_mean_coherence": active_mean,
        "active_max_coherence": active_max,
        "mean_informational_action": _finite(activation["mean_informational_action"], "mean_informational_action"),
        "active_term_count": float(len(active_terms)),
    }
    status = "OBSERVATION_ONLY" if candidate is None else "CANDIDATE_COMPILED"
    core = {
        "schema": SCHEMA,
        "status": status,
        "source_state_object_id": crystal["source_object_id"],
        "nexus_activation_object_id": checkpoint["object_id"],
        "crystal": crystal,
        "nexus": {
            "generation_id": activation["nexus_generation_id"],
            "coherence": nexus_coherence,
            "activation_binding_id": activation["activation_binding_id"],
        },
        "dictionary": dictionary,
        "htri": htri,
        "active_terms": active_terms,
        "semantic_tree": semantic_tree,
        "state_variables": state_variables,
        "intention_candidate": candidate,
        "computation_path": [
            "STATE_MEMORY_NEXUS_ACTIVATION",
            "LIVE_HTRI_BINDING",
            "CQCL_RELATIONAL_STATE_COMPILE",
        ],
        "execution_trace": [],
        "authority_grant": False,
        "execution_admitted": False,
    }
    program_id = hashlib.sha256(b"CQCL-LIVING-PROGRAM/v0.1\x00" + _canonical(core)).hexdigest()
    return CQCL_Living_Program(program_id=program_id, **core)


__all__ = ["CQCLLivingError", "CQCL_Living_Program", "compile_living_program"]
