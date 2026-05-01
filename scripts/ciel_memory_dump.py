#!/usr/bin/env python3
"""
CIEL Memory Dump — generuje memory_consolidated.md przy końcu sesji.

Zawiera: aktualny stan orchestratora (pkl), ostatnie hunchy, ostatnie wpisy z memories_index.db.
Uruchamiany ze Stop hooka (po ciel_memory_stop.py).
"""
from __future__ import annotations

import json
import pickle
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

_MEMORIES = Path.home() / "Pulpit" / "CIEL_memories"
_STATE_FILE = _MEMORIES / "state" / "ciel_orch_state.pkl"
_STATE_PERSIST = Path.home() / ".claude" / "ciel_orch_state.pkl"
_HUNCHES = _MEMORIES / "hunches.jsonl"
_DB = _MEMORIES / "memories_index.db"
_OUT = _MEMORIES / "state" / "memory_consolidated.md"


def _load_orch_summary() -> dict:
    candidates = sorted(
        [(p.stat().st_mtime, p) for p in (_STATE_FILE, _STATE_PERSIST) if p.exists()],
        reverse=True,
    )
    for _, path in candidates:
        try:
            with open(path, "rb") as f:
                orch = pickle.load(f)
            return {
                "cycle": getattr(orch, "cycle", "?"),
                "identity_phase": getattr(orch, "identity_phase", 0.0),
                "affective_key": getattr(orch, "affective_key", "?"),
                "source": path.name,
            }
        except Exception:
            pass
    return {}


def _load_hunches(n: int = 3) -> list[dict]:
    if not _HUNCHES.exists():
        return []
    lines = _HUNCHES.read_text(encoding="utf-8").splitlines()
    result = []
    for line in reversed(lines):
        try:
            h = json.loads(line)
            ts = h.get("ts") or h.get("timestamp", "")
            text = h.get("hunch") or h.get("text") or h.get("content", "")
            if text:
                result.append({"ts": ts, "text": text})
        except Exception:
            pass
        if len(result) >= n:
            break
    return list(reversed(result))


def _load_recent_sessions(n: int = 5) -> list[dict]:
    if not _DB.exists():
        return []
    try:
        with sqlite3.connect(str(_DB)) as conn:
            rows = conn.execute(
                "SELECT id, started_at, message_count FROM sessions "
                "ORDER BY started_at DESC LIMIT ?", (n,)
            ).fetchall()
        return [{"id": r[0][:12], "started": r[1][:16], "msgs": r[2]} for r in rows]
    except Exception:
        return []


def generate() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# CIEL Memory Consolidated — {now}", ""]

    orch = _load_orch_summary()
    if orch:
        lines += [
            "## Stan orchestratora",
            f"- cycle: {orch['cycle']}",
            f"- identity_phase: {orch.get('identity_phase', 0.0):.4f}",
            f"- affective_key: {orch.get('affective_key', '?')}",
            f"- źródło: {orch.get('source', '?')}",
            "",
        ]

    sessions = _load_recent_sessions()
    if sessions:
        lines += ["## Ostatnie sesje (5)", ""]
        for s in sessions:
            lines.append(f"- `{s['id']}` {s['started']} — {s['msgs']} wiad.")
        lines.append("")

    hunches = _load_hunches()
    if hunches:
        lines += ["## Ostatnie hunchy (3)", ""]
        for h in hunches:
            lines.append(f"- [{h['ts'][:16]}] {h['text'][:120]}")
        lines.append("")

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    try:
        hook_input = json.loads(sys.stdin.read().strip() or "{}")
    except Exception:
        hook_input = {}

    generate()
    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
