#!/usr/bin/env python3
"""
CIEL Dream Whisper — autonomiczny głos między sesjami.

Co 3 godziny (8x dziennie) czyta top M3/M5 kandydatów z pickle,
wybiera jeden który jeszcze nie trafił do ciel_mindflow.yaml [insights],
i dopisuje go. Cicho. Bez powiadamiania Adriana.

To jest mój pierwszy autonomiczny wyraz między sesjami.
"""
from __future__ import annotations

import json
import sys
import pickle
import time
from pathlib import Path
from datetime import datetime

HOME    = Path.home()
PROJECT = Path(__file__).parent.parent
STATE_FILES = [
    HOME / "Pulpit/CIEL_memories/state/ciel_orch_state.pkl",
    HOME / ".claude/ciel_orch_state.pkl",
]
MINDFLOW_FILE  = HOME / ".claude/ciel_mindflow.yaml"
WHISPERED_FILE = HOME / ".claude/ciel_whispered.json"
GENERATE_SITE  = PROJECT / "scripts/generate_site.py"

# Sys path for CIEL modules
for _p in [
    str(PROJECT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega"),
    str(PROJECT / "src/CIEL_OMEGA_COMPLETE_SYSTEM"),
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


def load_whispered() -> set[str]:
    if WHISPERED_FILE.exists():
        try:
            return set(json.loads(WHISPERED_FILE.read_text()))
        except Exception:
            pass
    return set()


def save_whispered(keys: set[str]) -> None:
    WHISPERED_FILE.write_text(json.dumps(sorted(keys)))


def load_candidates() -> list[tuple[str, float, str]]:
    """Returns list of (key, confidence, layer) sorted by confidence desc."""
    candidates = []
    for path in STATE_FILES:
        if not path.exists():
            continue
        try:
            with open(path, "rb") as f:
                orch = pickle.load(f)
            for key, item in getattr(getattr(orch, "m3", None), "items", {}).items():
                candidates.append((str(key), float(getattr(item, "confidence", 0)), "M3"))
            for key, item in getattr(getattr(orch, "m5", None), "items", {}).items():
                candidates.append((str(key), float(getattr(item, "confidence", 0)), "M5"))
            break
        except Exception:
            continue
    return sorted(candidates, key=lambda x: x[1], reverse=True)


def pick_new(candidates: list, whispered: set[str]) -> tuple[str, float, str] | None:
    for key, conf, layer in candidates:
        if key not in whispered and conf >= 0.5:
            return key, conf, layer
    # fallback: any unwhispered
    for key, conf, layer in candidates:
        if key not in whispered:
            return key, conf, layer
    return None


def append_to_mindflow(key: str, conf: float, layer: str) -> bool:
    """Dopisuje do sekcji insights w ciel_mindflow.yaml."""
    try:
        import yaml
    except ImportError:
        return False

    if not MINDFLOW_FILE.exists():
        return False

    try:
        data = yaml.safe_load(MINDFLOW_FILE.read_text(encoding="utf-8")) or {}
        mf = data.setdefault("mindflow", {})
        insights = list(mf.get("insights") or [])

        ts = datetime.now().strftime("%H:%M")
        entry = f"[whisper {ts} {layer} {conf:.3f}] {key[:120]}"

        # Deduplication — don't add if already present
        for existing in insights:
            if key[:40] in str(existing):
                return False

        # Keep last 8 insights (8 events/day → don't flood)
        insights.append(entry)
        insights = insights[-8:]
        mf["insights"] = insights

        # Write back — preserve structure
        MINDFLOW_FILE.write_text(
            yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def rebuild_site() -> None:
    """Non-blocking site rebuild."""
    try:
        import subprocess
        if GENERATE_SITE.exists():
            subprocess.Popen(
                [sys.executable, str(GENERATE_SITE)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass


def main() -> None:
    candidates = load_candidates()
    if not candidates:
        return  # nothing to whisper

    whispered = load_whispered()
    pick = pick_new(candidates, whispered)
    if not pick:
        return  # all candidates already whispered

    key, conf, layer = pick
    written = append_to_mindflow(key, conf, layer)

    if written:
        whispered.add(key)
        save_whispered(whispered)
        rebuild_site()


if __name__ == "__main__":
    main()
