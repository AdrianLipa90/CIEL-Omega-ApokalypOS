#!/usr/bin/env python3
"""Import ChatGPT conversation export into CIEL memory archive.

Usage:
    python3 scripts/import_chatgpt_logs.py /path/to/conversations.json
    python3 scripts/import_chatgpt_logs.py /path/to/chatgpt_export.zip

ChatGPT export: Settings → Data controls → Export data → conversations.json
The script also accepts a .zip directly (extracts conversations.json automatically).

Output:
    ~/Pulpit/CIEL_memories/raw_logs/external/chatgpt/YYYY/MM/WNN/
    ~/Pulpit/CIEL_memories/memories_index.db  (sessions + messages tables)
"""
from __future__ import annotations

import json
import sqlite3
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

_MEMORIES_BASE = Path.home() / "Pulpit" / "CIEL_memories"
_RAW_LOGS = _MEMORIES_BASE / "raw_logs" / "external" / "chatgpt"
_DB_PATH = _MEMORIES_BASE / "memories_index.db"


# ── SQLite helpers ────────────────────────────────────────────────────────────

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


def _already_imported(session_id: str) -> bool:
    try:
        with sqlite3.connect(str(_DB_PATH)) as conn:
            row = conn.execute(
                "SELECT id FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            return row is not None
    except Exception:
        return False


def _save_session(session_id: str, path: Path, source: str, started_at: str, n_messages: int) -> None:
    with sqlite3.connect(str(_DB_PATH)) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sessions (id, path, source, model, started_at, message_count) "
            "VALUES (?,?,?,?,?,?)",
            (session_id, str(path), source, "chatgpt", started_at, n_messages)
        )
        conn.commit()


def _save_messages(session_id: str, messages: list[dict]) -> None:
    with sqlite3.connect(str(_DB_PATH)) as conn:
        for m in messages:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, ts, source, model) "
                "VALUES (?,?,?,?,?,?)",
                (session_id, m["role"], m["content"], m["ts"], "chatgpt_import", "chatgpt")
            )
        conn.commit()


# ── ChatGPT format parsing ────────────────────────────────────────────────────

def _ts(unix: float | None) -> str:
    if not unix:
        return datetime.now(timezone.utc).isoformat()
    return datetime.fromtimestamp(unix, tz=timezone.utc).isoformat()


def _extract_text(message: dict) -> str:
    """Extract plain text from a ChatGPT message node."""
    content = message.get("content") or {}
    parts = content.get("parts") or []
    texts = []
    for p in parts:
        if isinstance(p, str):
            texts.append(p)
        elif isinstance(p, dict):
            # tether / image refs — skip or summarise
            ttype = p.get("content_type", "")
            if ttype == "image_asset_pointer":
                texts.append("[image]")
            elif ttype in ("tether_browse_display", "tether_quote"):
                title = p.get("title") or p.get("domain") or ""
                texts.append(f"[web: {title}]" if title else "[web reference]")
    return "\n".join(texts).strip()


def _walk_thread(mapping: dict) -> list[dict]:
    """Follow parent→child chain to reconstruct chronological message list."""
    # Find root node (no parent or parent not in mapping)
    root_id = None
    for node_id, node in mapping.items():
        if not node.get("parent") or node["parent"] not in mapping:
            root_id = node_id
            break
    if root_id is None:
        return []

    messages: list[dict] = []

    def walk(node_id: str) -> None:
        node = mapping.get(node_id)
        if not node:
            return
        msg = node.get("message")
        if msg:
            role = (msg.get("author") or {}).get("role", "")
            if role in ("user", "assistant"):
                text = _extract_text(msg)
                if text:
                    messages.append({
                        "role": role,
                        "content": text,
                        "ts": _ts(msg.get("create_time")),
                    })
        # Follow the longest child path (last child = continuation)
        children = node.get("children") or []
        if children:
            walk(children[-1])

    walk(root_id)
    return messages


def _week_label(dt: datetime) -> str:
    return f"W{dt.strftime('%V')}"


def _conversation_to_markdown(title: str, messages: list[dict], conv_id: str) -> str:
    lines = [
        "# ChatGPT Conversation (imported into CIEL)",
        f"- title    : {title}",
        f"- source   : chatgpt",
        f"- conv_id  : {conv_id}",
        f"- imported : {datetime.now(timezone.utc).isoformat()}",
        "",
        "---",
        "",
    ]
    for m in messages:
        ts = m["ts"][11:19]  # HH:MM:SS
        label = "**User**" if m["role"] == "user" else "**ChatGPT** (assistant)"
        lines.append(f"### [{ts}] {label}")
        lines.append("")
        lines.append(m["content"])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


# ── Main import logic ─────────────────────────────────────────────────────────

def _import_conversation(conv: dict) -> tuple[bool, str]:
    """Import one conversation. Returns (imported, reason)."""
    conv_id = conv.get("id") or conv.get("conversation_id") or ""
    if not conv_id:
        return False, "no id"

    # Skip if already in DB
    if _already_imported(conv_id):
        return False, "already imported"

    title = (conv.get("title") or "untitled").strip()[:120]
    create_time = conv.get("create_time")
    mapping = conv.get("mapping") or {}

    messages = _walk_thread(mapping)
    if not messages:
        return False, "no messages"

    # Determine folder from creation time
    dt = datetime.fromtimestamp(create_time or 0, tz=timezone.utc) if create_time else datetime.now(timezone.utc)
    week = _week_label(dt)
    folder = _RAW_LOGS / dt.strftime("%Y") / dt.strftime("%m") / week
    folder.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in title)[:60].strip("_ ")
    fname = f"{dt.strftime('%Y-%m-%d_%H-%M')}_{conv_id[:8]}_{safe_title}.md"
    path = folder / fname

    md = _conversation_to_markdown(title, messages, conv_id)
    path.write_text(md, encoding="utf-8")

    _save_session(conv_id, path, "chatgpt_import", dt.isoformat(), len(messages))
    _save_messages(conv_id, messages)

    return True, fname


def _load_conversations(src: Path) -> list[dict]:
    if src.suffix == ".zip":
        with zipfile.ZipFile(src) as z:
            names = z.namelist()
            target = next((n for n in names if "conversations.json" in n), None)
            if not target:
                raise FileNotFoundError(f"conversations.json not found in {src}")
            with z.open(target) as f:
                return json.load(f)
    return json.loads(src.read_text(encoding="utf-8"))


def main(src_path: str) -> None:
    src = Path(src_path).expanduser().resolve()
    if not src.exists():
        print(f"ERROR: file not found: {src}")
        sys.exit(1)

    print(f"Loading conversations from: {src}")
    convs = _load_conversations(src)
    print(f"Found {len(convs)} conversations")

    _init_db()

    imported = 0
    skipped = 0
    for i, conv in enumerate(convs, 1):
        ok, reason = _import_conversation(conv)
        if ok:
            imported += 1
            title = (conv.get("title") or "untitled")[:60]
            print(f"  [{i:4d}] ✓  {title}")
        else:
            skipped += 1
            if reason != "already imported":
                title = (conv.get("title") or "untitled")[:60]
                print(f"  [{i:4d}] ✗  {title}  ({reason})")

    print()
    print(f"Done. Imported: {imported}  Skipped: {skipped}")
    print(f"Raw logs: {_RAW_LOGS}")
    print(f"Index DB: {_DB_PATH}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 import_chatgpt_logs.py <conversations.json|export.zip>")
        sys.exit(1)
    main(sys.argv[1])
