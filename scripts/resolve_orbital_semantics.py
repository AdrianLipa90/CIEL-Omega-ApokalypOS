#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ORBIT_RULES = [
    ("IDENTITY", ["identity", "profile", "soul", "self", "state_geometry", "omega"]),
    ("CONSTITUTIVE", ["memory", "registry", "archive", "log", "manifest", "schema", "contract"]),
    ("DYNAMIC", ["runtime", "step", "evolve", "field", "phase", "coherence", "update", "loop"]),
    ("INTERACTION", ["client", "bridge", "adapter", "chat", "audio", "voice", "packet", "panel"]),
    ("OBSERVATION", ["ui", "view", "cockpit", "probe", "report", "diagnostic", "telemetry", "observe"]),
    ("BOUNDARY", ["policy", "guard", "boundary", "ethic", "validate", "check", "rule"]),
    ("EDUCATION", ["learn", "education", "tutorial", "curriculum", "teacher", "training"]),
]

CARD_SCHEMA = "ciel/orbital-object-card/v0.2"
GLOBAL_ATTRACTOR_REF = "GLOBAL_ATTRACTOR:PRIMARY_INFORMATION_SOURCE"

PARENT_ORBIT_ROLE = {
    "IDENTITY": "GLOBAL_ATTRACTOR",
    "CONSTITUTIVE": "IDENTITY",
    "DYNAMIC": "IDENTITY",
    "INTERACTION": "BOUNDARY",
    "OBSERVATION": "BOUNDARY",
    "BOUNDARY": "IDENTITY",
    "EDUCATION": "OBSERVATION",
    "UNRESOLVED": "IDENTITY",
}

INFORMATION_REGIME = {
    "IDENTITY": "LOCAL_PLUS_HORIZON",
    "CONSTITUTIVE": "LOCAL_PLUS_HORIZON",
    "DYNAMIC": "LOCAL_PLUS_HORIZON",
    "INTERACTION": "BOUNDARY_BROKER",
    "OBSERVATION": "GLOBAL_OBSERVATION",
    "BOUNDARY": "BOUNDARY_BROKER",
    "EDUCATION": "GLOBAL_OBSERVATION",
    "UNRESOLVED": "LOCAL_ONLY",
}

HORIZON_CLASS = {
    "LOCAL_ONLY": "SEALED",
    "LOCAL_PLUS_HORIZON": "POROUS",
    "BOUNDARY_BROKER": "TRANSMISSIVE",
    "GLOBAL_OBSERVATION": "OBSERVATIONAL",
}

TAU_ROLE = {
    "IDENTITY": "TAU_MEMORY",
    "CONSTITUTIVE": "TAU_MEMORY",
    "DYNAMIC": "TAU_LOCAL",
    "INTERACTION": "TAU_LOCAL",
    "OBSERVATION": "TAU_OBSERVER",
    "BOUNDARY": "TAU_BOUNDARY",
    "EDUCATION": "TAU_OBSERVER",
    "UNRESOLVED": "TAU_LOCAL",
}


def score_orbit(text: str) -> tuple[str, float]:
    lowered = text.lower()
    best_orbit = "UNRESOLVED"
    best_score = 0.0
    for orbit, tokens in ORBIT_RULES:
        score = sum(1 for t in tokens if t in lowered)
        if score > best_score:
            best_orbit = orbit
            best_score = float(score)
    confidence = min(0.35 + 0.12 * best_score, 0.97) if best_score > 0 else 0.18
    return best_orbit, confidence


def semantic_role(rec: dict[str, Any], orbit: str) -> str:
    base = f"{orbit.lower()}-{rec['kind']}"
    lowered = f"{rec.get('path','')} {rec.get('qualname','')}".lower()
    if "runtime20" in lowered:
        return "omega-runtime-core"
    if "orbital_cockpit" in lowered:
        return "orbital-observation-shell"
    if "sapiens_client" in lowered:
        return "packet-memory-bridge"
    if "gguf" in lowered:
        return "gguf-language-bridge"
    if "audio" in lowered:
        return f"audio-{rec['kind']}"
    return base


def container_card_id(rec: dict[str, Any]) -> str | None:
    if rec.get("kind") == "file":
        return None
    return f"file:{rec['path']}"


def derive_lagrange_roles(rec: dict[str, Any]) -> list[str]:
    lowered = f"{rec.get('path','')} {rec.get('qualname','')} {rec.get('semantic_role','')}".lower()
    roles: list[str] = []
    if any(token in lowered for token in ["bridge", "adapter", "client", "packet", "panel", "gateway", "router"]):
        roles.append("TRANSFER_NODE")
    if any(token in lowered for token in ["report", "probe", "view", "telemetry", "observe", "cockpit"]):
        roles.append("OBSERVATION_POINT")
    if any(token in lowered for token in ["registry", "manifest", "schema", "index", "anchor"]):
        roles.append("ANCHOR_POINT")
    if any(token in lowered for token in ["guard", "policy", "validate", "check", "rule", "boundary"]):
        roles.append("BOUNDARY_GATE")
    return sorted(set(roles))


def derive_manybody_role(rec: dict[str, Any], orbit: str, lagrange_roles: list[str]) -> str:
    if rec.get("kind") == "file":
        return "SUBSYSTEM_BOARD"
    if "TRANSFER_NODE" in lagrange_roles:
        return "TRANSFER_NODE"
    if orbit == "OBSERVATION":
        return "OBSERVER"
    if orbit == "BOUNDARY":
        return "BOUNDARY_GATE"
    return "OSCILLATOR"


def derive_subsystem_kind(rec: dict[str, Any]) -> str:
    return "BOARD" if rec.get("kind") == "file" else "NODE"


def derive_horizon_id(rec: dict[str, Any]) -> str:
    return f"horizon:{rec['path']}"


def derive_visible_scopes(regime: str, rec: dict[str, Any]) -> list[str]:
    base = ["self"]
    if rec.get("kind") != "file":
        base.append("container")
    if regime == "LOCAL_ONLY":
        base.append("local-orbit")
    elif regime == "LOCAL_PLUS_HORIZON":
        base.extend(["local-orbit", "horizon-leak"])
    elif regime == "BOUNDARY_BROKER":
        base.extend(["local-orbit", "adjacent-horizon", "broker-leak"])
    elif regime == "GLOBAL_OBSERVATION":
        base.extend(["local-orbit", "orbit-snapshot", "global-snapshot"])
    return base


def derive_leak_policy(regime: str) -> str:
    return {
        "LOCAL_ONLY": "SEALED",
        "LOCAL_PLUS_HORIZON": "HAWKING_EULER",
        "BOUNDARY_BROKER": "HAWKING_EULER_BROKERED",
        "GLOBAL_OBSERVATION": "SNAPSHOT_ONLY",
    }.get(regime, "SEALED")


def count_values(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rec in records:
        value = rec.get(key)
        if value is None:
            continue
        counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def count_list_values(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rec in records:
        for value in rec.get(key, []) or []:
            counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    in_path = repo_root / "integration" / "registries" / "definitions" / "definition_registry.json"
    raw = json.loads(in_path.read_text(encoding="utf-8"))
    records = raw["records"]

    enriched = []
    orbit_counts: dict[str, int] = {}
    for rec in records:
        text = " ".join([
            rec.get("path", ""),
            rec.get("name", ""),
            rec.get("qualname", ""),
            rec.get("doc", ""),
            rec.get("signature", ""),
        ])
        orbit, confidence = score_orbit(text)
        regime = INFORMATION_REGIME.get(orbit, "LOCAL_ONLY")
        lagrange = derive_lagrange_roles(rec | {"semantic_role": semantic_role(rec, orbit)})
        rec2 = rec | {
            "card_schema": CARD_SCHEMA,
            "global_attractor_ref": GLOBAL_ATTRACTOR_REF,
            "orbital_role": orbit,
            "orbital_confidence": round(confidence, 3),
            "semantic_role": semantic_role(rec, orbit),
            "container_card_id": container_card_id(rec),
            "subsystem_kind": derive_subsystem_kind(rec),
            "manybody_role": derive_manybody_role(rec, orbit, lagrange),
            "parent_orbital_role": PARENT_ORBIT_ROLE.get(orbit, "IDENTITY"),
            "horizon_id": derive_horizon_id(rec),
            "horizon_class": HORIZON_CLASS.get(regime, "SEALED"),
            "information_regime": regime,
            "visible_scopes": derive_visible_scopes(regime, rec),
            "leak_policy": derive_leak_policy(regime),
            "tau_role": TAU_ROLE.get(orbit, "TAU_LOCAL"),
            "lagrange_roles": lagrange,
        }
        enriched.append(rec2)
        orbit_counts[orbit] = orbit_counts.get(orbit, 0) + 1

    out_dir = repo_root / "integration" / "registries" / "definitions"
    reg_path = out_dir / "orbital_definition_registry.json"
    report_path = out_dir / "orbital_assignment_report.json"
    reg_payload = {
        "schema": "ciel/orbital-definition-registry-enriched/v0.2",
        "card_schema": CARD_SCHEMA,
        "global_attractor_ref": GLOBAL_ATTRACTOR_REF,
        "count": len(enriched),
        "records": enriched,
    }
    report_payload = {
        "schema": "ciel/orbital-assignment-report/v0.2",
        "card_schema": CARD_SCHEMA,
        "count": len(enriched),
        "orbit_counts": orbit_counts,
        "unresolved": orbit_counts.get("UNRESOLVED", 0),
        "information_regime_counts": count_values(enriched, "information_regime"),
        "horizon_class_counts": count_values(enriched, "horizon_class"),
        "tau_role_counts": count_values(enriched, "tau_role"),
        "manybody_role_counts": count_values(enriched, "manybody_role"),
        "lagrange_role_counts": count_list_values(enriched, "lagrange_roles"),
    }
    reg_path.write_text(json.dumps(reg_payload, indent=2), encoding="utf-8")
    report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    print(json.dumps(report_payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
