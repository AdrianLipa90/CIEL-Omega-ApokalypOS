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
        rec2 = rec | {
            "orbital_role": orbit,
            "orbital_confidence": round(confidence, 3),
            "semantic_role": semantic_role(rec, orbit),
        }
        enriched.append(rec2)
        orbit_counts[orbit] = orbit_counts.get(orbit, 0) + 1

    out_dir = repo_root / "integration" / "registries" / "definitions"
    reg_path = out_dir / "orbital_definition_registry.json"
    report_path = out_dir / "orbital_assignment_report.json"
    reg_payload = {
        "schema": "ciel/orbital-definition-registry-enriched/v0.1",
        "count": len(enriched),
        "records": enriched,
    }
    report_payload = {
        "schema": "ciel/orbital-assignment-report/v0.1",
        "count": len(enriched),
        "orbit_counts": orbit_counts,
        "unresolved": orbit_counts.get("UNRESOLVED", 0),
    }
    reg_path.write_text(json.dumps(reg_payload, indent=2), encoding="utf-8")
    report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    print(json.dumps(report_payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
