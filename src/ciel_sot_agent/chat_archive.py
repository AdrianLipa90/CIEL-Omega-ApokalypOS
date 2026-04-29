"""CIEL Chat Archive — append-only conversation log in Markdown.

Hierarchical structure:
  ~/Pulpit/CIEL_memories/raw_logs/YYYY/MM/WNN/YYYY-MM-DD_HH-MM_session.md

Never modified. Never deleted. Append only.
Each session creates one file. Each file is indexed in memories_index.db.
"""
from __future__ import annotations

import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

_MEMORIES_BASE = Path.home() / "Pulpit" / "CIEL_memories"
_RAW_LOGS = _MEMORIES_BASE / "raw_logs"
_DB_PATH = _MEMORIES_BASE / "memories_index.db"

_lock = threading.Lock()
_session_id: str = str(uuid.uuid4())[:8]
_session_file: dict[str, Path] = {}


# ── SQLite index ────────────────────────────────────────────────────────────

def _init_db() -> None:
    _MEMORIES_BASE.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(_DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                source TEXT,
                model TEXT,
                started_at TEXT,
                message_count INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                ts TEXT,
                source TEXT,
                model TEXT
            )
        """)
        conn.commit()


def _db_register_session(session_id: str, path: Path, source: str) -> None:
    try:
        _init_db()
        with sqlite3.connect(str(_DB_PATH)) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO sessions (id, path, source, started_at) VALUES (?,?,?,?)",
                (session_id, str(path), source, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
    except Exception:
        pass


def _db_append_message(session_id: str, role: str, content: str, source: str, model: str) -> None:
    try:
        ts = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(str(_DB_PATH)) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, ts, source, model) VALUES (?,?,?,?,?,?)",
                (session_id, role, content, ts, source, model)
            )
            conn.execute(
                "UPDATE sessions SET message_count = message_count + 1, model = ? WHERE id = ?",
                (model, session_id)
            )
            conn.commit()
    except Exception:
        pass


# ── session file ─────────────────────────────────────────────────────────────

def _session_path(source: str) -> Path:
    now = datetime.now(timezone.utc)
    week = f"W{now.strftime('%V')}"
    folder = _RAW_LOGS / now.strftime("%Y") / now.strftime("%m") / week
    folder.mkdir(parents=True, exist_ok=True)
    fname = f"{now.strftime('%Y-%m-%d_%H-%M')}_{_session_id}_{source}.md"
    return folder / fname


def _get_session_file(source: str) -> Path:
    if source not in _session_file:
        path = _session_path(source)
        with _lock:
            if source not in _session_file:
                path.write_text(
                    f"# CIEL Conversation Log\n"
                    f"- source  : {source}\n"
                    f"- session : {_session_id}\n"
                    f"- started : {datetime.now(timezone.utc).isoformat()}\n\n---\n\n",
                    encoding="utf-8",
                )
                _session_file[source] = path
                _db_register_session(_session_id, path, source)
    return _session_file[source]


def open_session(source: str = "gui_gguf") -> Path:
    """Pre-create session file immediately — call at startup."""
    return _get_session_file(source)


# ── public API ───────────────────────────────────────────────────────────────

def append(
    role: str,
    content: str,
    source: str = "gui_gguf",
    model: str = "unknown",
    session_id: str | None = None,
    extra: dict | None = None,
) -> None:
    """Append one message. Thread-safe, never raises."""
    try:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        role_label = "**User**" if role == "user" else f"**{model}** (assistant)"
        extra_str = ""
        if extra:
            extra_str = "\n" + "\n".join(f"_{k}: {v}_" for k, v in extra.items())
        block = f"### [{ts}] {role_label}\n\n{content}{extra_str}\n\n---\n\n"
        path = _get_session_file(source)
        with _lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(block)
        _db_append_message(session_id or _session_id, role, content, source, model)
    except Exception:
        pass


def append_exchange(
    user_msg: str,
    assistant_reply: str,
    source: str = "gui_gguf",
    model: str = "unknown",
    session_id: str | None = None,
) -> None:
    append("user", user_msg, source=source, model=model, session_id=session_id)
    append("assistant", assistant_reply, source=source, model=model, session_id=session_id)


def load_recent(n: int = 30, source: str | None = None) -> list[dict]:
    """List recent session files (metadata only)."""
    if not _RAW_LOGS.exists():
        return []
    files = sorted(_RAW_LOGS.rglob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    result = []
    for f in files:
        if source and source not in f.name:
            continue
        result.append({
            "path": str(f),
            "name": f.name,
            "rel": str(f.relative_to(_MEMORIES_BASE)),
            "size_kb": round(f.stat().st_size / 1024, 1),
        })
        if len(result) >= n:
            break
    return result


def load_last_session_history(source: str = "gui_gguf", max_messages: int = 40) -> list[dict]:
    """Parse the last non-empty session file and return chat history dicts.

    Returns list of {"role": "user"|"assistant", "content": str}.
    Skips the current session file (just created, empty).
    """
    if not _RAW_LOGS.exists():
        return []
    files = sorted(
        (f for f in _RAW_LOGS.rglob("*.md") if source in f.name),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    current = _session_file.get(source)
    for f in files:
        if current and f == current:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        messages = _parse_log_to_history(text)
        if messages:
            return messages[-max_messages:]
    return []


def _parse_log_to_history(text: str) -> list[dict]:
    """Parse raw log markdown into list of {role, content} dicts."""
    import re
    blocks = re.split(r"\n---\n", text)
    history: list[dict] = []
    header_re = re.compile(r"^###\s+\[\d{2}:\d{2}(?::\d{2})?\]\s+\*\*(.+?)\*\*")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        header_line = lines[0] if lines else ""
        m = header_re.match(header_line)
        if not m:
            continue
        label = m.group(1)
        role = "user" if label == "User" else "assistant"
        content = "\n".join(lines[2:]).strip()
        if content:
            history.append({"role": role, "content": content})
    return history


def stats() -> dict:
    files = list(_RAW_LOGS.rglob("*.md")) if _RAW_LOGS.exists() else []
    total_kb = sum(f.stat().st_size for f in files) / 1024
    return {
        "total_files": len(files),
        "total_kb": round(total_kb, 1),
        "base": str(_MEMORIES_BASE),
        "session_id": _session_id,
    }
