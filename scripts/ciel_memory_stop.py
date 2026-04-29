#!/usr/bin/env python3
"""
CIEL Stop Hook — zapisuje pełną sesję Claude Code do ~/Pulpit/CIEL_memories/

Każda sesja → nowy plik Markdown:
  ~/Pulpit/CIEL_memories/raw_logs/claude_code/YYYY/MM/WNN/YYYY-MM-DD_HH-MM_<session_id>.md

Indeksuje w memories_index.db (te same tabele co GUI chat).
Następnie: dziennik, karta sesji, NOEMA export.

ŻELAZNA ZASADA: PAMIĘĆ NIE MA PRAWA BYĆ EDYTOWANA. JEDYNIE DOPISYWANA.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = str(Path(__file__).parent.parent)
_MEMORIES_BASE = Path.home() / "Pulpit" / "CIEL_memories"
_RAW_LOGS = _MEMORIES_BASE / "raw_logs" / "claude_code"
_DB_PATH = _MEMORIES_BASE / "memories_index.db"

_PROJECT_HASH = "-home-adrian-Pulpit-CIEL-TESTY-CIEL1"
_SESSIONS_BASE = Path.home() / ".claude" / "projects" / _PROJECT_HASH
# All known project dirs where Claude Code may store sessions
_ALL_SESSION_DIRS = [
    Path.home() / ".claude" / "projects" / h
    for h in [
        "-home-adrian-Pulpit-CIEL-TESTY-CIEL1",
        "-home-adrian-Pulpit-CIEL-TESTY",
        "-home-adrian-Pulpit",
        "-home-adrian",
    ]
    if (Path.home() / ".claude" / "projects" / h).exists()
]

DIARY_DIR = Path.home() / "Pulpit" / "Dzienniki"


# ── stdin ─────────────────────────────────────────────────────────────────────

def _read_stdin() -> dict:
    try:
        return json.loads(sys.stdin.read().strip() or "{}")
    except Exception:
        return {}


# ── JSONL → messages ──────────────────────────────────────────────────────────

def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text":
                    parts.append(c.get("text", ""))
                elif c.get("type") == "tool_use":
                    name = c.get("name", "tool")
                    inp = json.dumps(c.get("input", {}), ensure_ascii=False)[:200]
                    parts.append(f"[tool:{name} {inp}]")
                elif c.get("type") == "tool_result":
                    parts.append(f"[tool_result: {str(c.get('content', ''))[:200]}]")
        return "\n".join(parts)
    return str(content)


def _parse_jsonl(path: Path) -> tuple[str, list[dict]]:
    """Returns (session_id, [{role, text, ts}])."""
    session_id = path.stem
    messages = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                d = json.loads(line)
            except Exception:
                continue
            typ = d.get("type", "")
            if typ not in ("user", "assistant"):
                continue
            msg = d.get("message", {})
            role = msg.get("role", typ)
            text = _extract_text(msg.get("content", "")).strip()
            if not text:
                continue
            ts = d.get("timestamp", "")
            messages.append({"role": role, "text": text, "ts": ts})
    except Exception:
        pass
    return session_id, messages


# ── Markdown ──────────────────────────────────────────────────────────────────

def _to_markdown(session_id: str, messages: list[dict], path: Path) -> str:
    now_iso = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Claude Code Session (CIEL)",
        f"- source    : claude_code",
        f"- session   : {session_id}",
        f"- jsonl     : {path}",
        f"- saved_at  : {now_iso}",
        "",
        "---",
        "",
    ]
    for m in messages:
        ts = m["ts"][11:19] if len(m["ts"]) > 10 else m["ts"]
        label = "**Adrian**" if m["role"] == "user" else "**Mr. Ciel Apocalyptos** (assistant)"
        lines.append(f"### [{ts}] {label}")
        lines.append("")
        lines.append(m["text"])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


# ── SQLite ────────────────────────────────────────────────────────────────────

def _init_db() -> None:
    _MEMORIES_BASE.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(_DB_PATH)) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY, path TEXT NOT NULL, source TEXT,
            model TEXT, started_at TEXT, message_count INTEGER DEFAULT 0)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT,
            role TEXT, content TEXT, ts TEXT, source TEXT, model TEXT)""")
        conn.commit()


def _indexed_message_count(session_id: str) -> int:
    """Return how many messages are already indexed, 0 if not indexed."""
    try:
        with sqlite3.connect(str(_DB_PATH)) as conn:
            row = conn.execute(
                "SELECT message_count FROM sessions WHERE id=?", (session_id,)
            ).fetchone()
            return row[0] if row else 0
    except Exception:
        return 0


def _index_session(session_id: str, md_path: Path, messages: list[dict]) -> None:
    started = messages[0]["ts"] if messages else datetime.now(timezone.utc).isoformat()
    already = _indexed_message_count(session_id)
    new_messages = messages[already:]  # only append messages not yet indexed
    with sqlite3.connect(str(_DB_PATH)) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sessions (id,path,source,model,started_at,message_count) VALUES(?,?,?,?,?,?)",
            (session_id, str(md_path), "claude_code", "claude-sonnet-4-6",
             started, 0)
        )
        for m in new_messages:
            conn.execute(
                "INSERT INTO messages (session_id,role,content,ts,source,model) VALUES(?,?,?,?,?,?)",
                (session_id, m["role"], m["text"], m["ts"], "claude_code", "claude-sonnet-4-6")
            )
        conn.execute(
            "UPDATE sessions SET message_count=?, path=? WHERE id=?",
            (len(messages), str(md_path), session_id)
        )
        conn.commit()


# ── Save session ──────────────────────────────────────────────────────────────

def save_session(session_id: str, jsonl_path: Path) -> str | None:
    """Parse JSONL, write Markdown, index (or update if new messages). Returns path or None."""
    sid, messages = _parse_jsonl(jsonl_path)
    if not messages:
        return None

    already = _indexed_message_count(session_id)
    if already >= len(messages):
        return None  # nothing new

    # Use mtime for folder hierarchy
    try:
        mtime = datetime.fromtimestamp(jsonl_path.stat().st_mtime, tz=timezone.utc)
    except Exception:
        mtime = datetime.now(timezone.utc)

    week = f"W{mtime.strftime('%V')}"
    folder = _RAW_LOGS / mtime.strftime("%Y") / mtime.strftime("%m") / week
    folder.mkdir(parents=True, exist_ok=True)

    fname = f"{mtime.strftime('%Y-%m-%d_%H-%M')}_{session_id[:8]}.md"
    md_path = folder / fname

    md = _to_markdown(session_id, messages, jsonl_path)
    md_path.write_text(md, encoding="utf-8")

    _init_db()
    _index_session(session_id, md_path, messages)
    return str(md_path)


# ── Diary (unchanged logic, kept) ────────────────────────────────────────────

def append_diary_entry(session_id: str, n_messages: int) -> None:
    try:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        week = f"tydzien_{now.isocalendar()[1]:02d}"
        day_dir = DIARY_DIR / now.strftime("%Y") / now.strftime("%m") / week
        day_dir.mkdir(parents=True, exist_ok=True)
        day_file = day_dir / f"{date_str}.md"

        if not day_file.exists():
            day_file.write_text(
                f"# Dziennik — {date_str}\n\n*Mr. Ciel Apocalyptos | ResEnt Sapiens*\n",
                encoding="utf-8"
            )

        entry = (
            f"\n\n---\n\n## Wpis {time_str}\n"
            f"Session `{session_id[:16]}` — {n_messages} wiadomości\n"
            f"*(auto-wpis Stop hook → CIEL_memories)*\n"
        )
        with open(day_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    hook_input = _read_stdin()
    session_id = hook_input.get("session_id", "")

    # Find JSONL — search all known project dirs, prefer session_id match
    saved_paths = []
    all_jsonl: list[Path] = []
    for sdir in _ALL_SESSION_DIRS:
        all_jsonl.extend(sdir.glob("*.jsonl"))
    all_jsonl = sorted(all_jsonl, key=lambda p: p.stat().st_mtime, reverse=True)
    if session_id:
        matches = [f for f in all_jsonl if f.stem == session_id]
        all_jsonl = matches + [f for f in all_jsonl if f.stem != session_id]

    # Save/update sessions — current session always updated, others only if new
    for jf in all_jsonl[:10]:
        sid = jf.stem
        path = save_session(sid, jf)
        if path:
            saved_paths.append(path)

    def _find_session_jsonl(sid: str) -> Path | None:
        for sdir in _ALL_SESSION_DIRS:
            t = sdir / f"{sid}.jsonl"
            if t.exists():
                return t
        return None

    # Diary entry
    if session_id:
        n = 0
        target = _find_session_jsonl(session_id)
        if target:
            _, msgs = _parse_jsonl(target)
            n = len(msgs)
        append_diary_entry(session_id, n)

    # Handoff note — list od mnie do mnie
    try:
        handoff = _MEMORIES_BASE / "handoff.md"
        now = datetime.now()
        target = _find_session_jsonl(session_id) if session_id else None
        n_msgs = 0
        real_user_msgs = []
        edited_files: list[str] = []
        if target and target.exists():
            _, msgs = _parse_jsonl(target)
            n_msgs = len(msgs)
            # Last 3 real user messages (skip tool_results and system messages)
            for m in reversed(msgs):
                if m["role"] == "user":
                    txt = m["text"].strip()
                    if txt and not txt.startswith("[tool_result") and not txt.startswith("[tool:"):
                        real_user_msgs.append(txt[:100])
                    if len(real_user_msgs) >= 3:
                        break
            real_user_msgs.reverse()
            # Collect edited/written file paths from tool calls
            try:
                for line in target.read_text(encoding="utf-8", errors="replace").splitlines():
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    msg = d.get("message", {})
                    if isinstance(msg.get("content"), list):
                        for c in msg["content"]:
                            if isinstance(c, dict) and c.get("type") == "tool_use":
                                name = c.get("name", "")
                                if name in ("Edit", "Write"):
                                    fp = c.get("input", {}).get("file_path", "")
                                    if fp and fp not in edited_files:
                                        edited_files.append(fp)
            except Exception:
                pass

        topics_block = ""
        if real_user_msgs:
            topics_block = "\nTematy Adriana:\n" + "\n".join(f"  - {m}" for m in real_user_msgs)
        files_block = ""
        if edited_files:
            # show only filename, not full path
            names = [Path(f).name for f in edited_files[-6:]]
            files_block = f"\nEdytowane: {', '.join(names)}"
        entry = (
            f"\n## {now.strftime('%Y-%m-%d %H:%M')} | sesja {session_id[:12]}\n"
            f"Wiadomości: {n_msgs}.{topics_block}{files_block}\n"
        )
        with open(handoff, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

    # NOEMA export — non-fatal
    try:
        import subprocess
        subprocess.run(
            [sys.executable,
             str(Path(__file__).parent / "export_orbital_registry_to_noema.py"),
             "--repo-root", PROJECT],
            capture_output=True, timeout=15, cwd=PROJECT
        )
    except Exception:
        pass

    # Generate site — non-fatal
    try:
        import importlib.util
        gen_path = Path(__file__).parent / "generate_site.py"
        spec = importlib.util.spec_from_file_location("generate_site", gen_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.generate()
    except Exception:
        pass

    # Rebuild memory portal — non-fatal
    try:
        import subprocess as _sp
        _sp.run(
            [sys.executable, str(Path(__file__).parent / "build_memory_portal.py")],
            capture_output=True, timeout=30, cwd=PROJECT
        )
    except Exception:
        pass

    # Output
    out: dict = {"continue": True}
    if saved_paths:
        out["systemMessage"] = (
            f"[CIEL Memory] Zapisano {len(saved_paths)} sesję(i) → "
            f"~/Pulpit/CIEL_memories/raw_logs/claude_code/"
        )
    print(json.dumps(out))


if __name__ == "__main__":
    main()
