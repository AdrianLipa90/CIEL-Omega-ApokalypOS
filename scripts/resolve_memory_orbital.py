#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

MEMORY_ROOT = Path.home() / "Pulpit" / "CIEL_memories"
OUTPUT_PATH = MEMORY_ROOT / "orbital_memory_registry.json"

SKIP_DIRS = {".claude", "__pycache__", ".git"}
SKIP_SUFFIXES = {".pkl", ".sock", ".db", ".pyc", ".lock"}
SKIP_NAMES = {"orbital_memory_registry.json"}

MEMORY_ORBIT_RULES = [
    ("EPISODIC",   ["raw_log", "dziennik", "2026", "session", "claude_code", "tydzien", "w16", "w17", "w18", "w19"]),
    ("SEMANTIC",   ["memories_index", "memories.json", "tag_index", "sessions.json", "semantic", "portal"]),
    ("AFFECTIVE",  ["hunch", "affective", "emotional", "mood", "wave", "sub_log", "subconscious", "wpm"]),
    ("IDENTITY",   ["handoff", "orch_state", "ciel_last", "genesis", "snapshot", "identity", "state"]),
    ("RELATIONAL", ["project", "routine", "plans", "intencj", "dziennik.md"]),
    ("BOUNDARY",   ["access_token", "settings", "hook_error", "hook_debug", "token"]),
    ("LOG",        ["consciousness_log", "ciel_dziennik", ".log", ".jsonl"]),
]

INFORMATION_REGIME = {
    "EPISODIC":   "LOCAL_PLUS_HORIZON",
    "SEMANTIC":   "GLOBAL_OBSERVATION",
    "AFFECTIVE":  "LOCAL_PLUS_HORIZON",
    "IDENTITY":   "LOCAL_PLUS_HORIZON",
    "RELATIONAL": "LOCAL_PLUS_HORIZON",
    "BOUNDARY":   "BOUNDARY_BROKER",
    "LOG":        "LOCAL_ONLY",
    "UNRESOLVED": "LOCAL_ONLY",
}

HORIZON_CLASS = {
    "LOCAL_ONLY":        "SEALED",
    "LOCAL_PLUS_HORIZON":"POROUS",
    "BOUNDARY_BROKER":   "TRANSMISSIVE",
    "GLOBAL_OBSERVATION":"OBSERVATIONAL",
}

TAU_ROLE = {
    "EPISODIC":   "TAU_MEMORY",
    "SEMANTIC":   "TAU_OBSERVER",
    "AFFECTIVE":  "TAU_MEMORY",
    "IDENTITY":   "TAU_MEMORY",
    "RELATIONAL": "TAU_LOCAL",
    "BOUNDARY":   "TAU_BOUNDARY",
    "LOG":        "TAU_LOCAL",
    "UNRESOLVED": "TAU_LOCAL",
}

LEAK_POLICY = {
    "SEALED":        "SEALED",
    "POROUS":        "HAWKING_EULER",
    "TRANSMISSIVE":  "HAWKING_EULER_BROKERED",
    "OBSERVATIONAL": "SNAPSHOT_ONLY",
}


def score_orbit(text: str) -> tuple[str, float]:
    lowered = text.lower()
    best = "UNRESOLVED"
    best_score = 0.0
    for orbit, tokens in MEMORY_ORBIT_RULES:
        score = sum(1 for t in tokens if t in lowered)
        if score > best_score:
            best = orbit
            best_score = float(score)
    confidence = min(0.35 + 0.12 * best_score, 0.97) if best_score > 0 else 0.18
    return best, confidence


def scan_memory(root: Path) -> list[dict]:
    records = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix in SKIP_SUFFIXES:
                continue
            if fname in SKIP_NAMES:
                continue
            rel = fpath.relative_to(root)
            text = str(rel).lower() + " " + fname.lower()
            orbit, confidence = score_orbit(text)
            regime = INFORMATION_REGIME.get(orbit, "LOCAL_ONLY")
            hclass = HORIZON_CLASS.get(regime, "SEALED")
            try:
                stat = fpath.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
            except OSError:
                size = 0
                mtime = ""
            records.append({
                "id": f"memory:{rel}",
                "path": str(rel),
                "name": fname,
                "kind": "file",
                "size_bytes": size,
                "mtime": mtime,
                "orbital_role": orbit,
                "orbital_confidence": round(confidence, 3),
                "information_regime": regime,
                "horizon_class": hclass,
                "leak_policy": LEAK_POLICY.get(hclass, "SEALED"),
                "tau_role": TAU_ROLE.get(orbit, "TAU_LOCAL"),
            })
    return records


def main() -> None:
    records = scan_memory(MEMORY_ROOT)
    from collections import Counter
    counts = dict(Counter(r["orbital_role"] for r in records))
    out = {
        "schema": "ciel/orbital-memory-registry/v0.1",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "memory_root": str(MEMORY_ROOT),
        "count": len(records),
        "counts_by_role": counts,
        "records": records,
    }
    OUTPUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"orbital_memory_registry.json → {len(records)} records: {counts}")


if __name__ == "__main__":
    main()
