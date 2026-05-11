#!/usr/bin/env python3
"""
Codex → CIEL1 bridge.

Watches Codex CLI rollout JSONL transcripts in ~/.codex/sessions/**/rollout-*.jsonl
and mirrors every user/assistant message into:
  ~/Pulpit/CIEL_memories/raw_logs/... (via ciel_sot_agent.chat_archive)
and optionally runs the CIEL per-message hooks (M0-M8 + SUB) so Codex becomes a
first-class communication medium for CIEL1.

This is intentionally "hardcoded": it does not depend on Codex plugin hooks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


CODEX_SESSIONS = Path.home() / ".codex" / "sessions"
STATE_PATH = Path.home() / "Pulpit" / "CIEL_memories" / "state" / "codex_bridge_state.json"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_import_paths() -> None:
    project = _project_root()
    src = project / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _load_state() -> dict[str, Any]:
    try:
        if STATE_PATH.exists():
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"files": {}, "session_by_file": {}}


def _save_state(state: dict[str, Any]) -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, STATE_PATH)
    except Exception:
        pass


def _iter_rollout_files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    files = [p for p in base.rglob("rollout-*.jsonl") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime)
    return files


def _extract_text_blocks(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        text = block.get("text")
        if isinstance(text, str) and text:
            parts.append(text)
    return "\n".join(parts).strip()


@dataclass(frozen=True)
class CodexMessage:
    ts: str
    session_id: str
    role: str  # "user" | "assistant"
    text: str
    originator: str = "codex-tui"


def _parse_rollout_line(line: str, fallback_session_id: str = "") -> tuple[str, CodexMessage | None]:
    """Return (session_id, message_or_none). Never raises."""
    try:
        obj = json.loads(line)
    except Exception:
        return fallback_session_id, None

    t = obj.get("type")
    payload = obj.get("payload") or {}
    ts = obj.get("timestamp") or ""

    if t == "session_meta":
        sid = str(payload.get("id") or "").strip()
        return sid or fallback_session_id, None

    if t != "response_item":
        return fallback_session_id, None

    if not isinstance(payload, dict):
        return fallback_session_id, None

    if payload.get("type") != "message":
        return fallback_session_id, None

    role = payload.get("role")
    if role not in ("user", "assistant"):
        return fallback_session_id, None

    text = _extract_text_blocks(payload.get("content"))
    if not text:
        return fallback_session_id, None

    msg = CodexMessage(
        ts=str(ts),
        session_id=fallback_session_id,
        role=str(role),
        text=text,
        originator="codex-tui",
    )
    return fallback_session_id, msg


def _run_ciel_hooks(user_text: str | None, assistant_text: str | None, session_id: str) -> None:
    """Best-effort: run existing CIEL per-message hooks so Codex drives M0-M8 state."""
    try:
        project = _project_root()
        scripts = project / "scripts"
        # Load scripts dynamically to avoid packaging coupling.
        import importlib.util as _ilu

        if user_text is not None:
            spec = _ilu.spec_from_file_location("ciel_message_step", str(scripts / "ciel_message_step.py"))
            mod = _ilu.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)
            try:
                mod.run_step(user_text, session_id=session_id)
            except Exception:
                pass

        if assistant_text is not None:
            spec = _ilu.spec_from_file_location("ciel_response_step", str(scripts / "ciel_response_step.py"))
            mod = _ilu.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)
            try:
                mod.process_response_text(assistant_text, session_id=session_id)
            except Exception:
                pass
    except Exception:
        return


def _ingest_file(
    path: Path,
    state: dict[str, Any],
    *,
    source: str,
    run_hooks: bool,
) -> None:
    _ensure_import_paths()
    from ciel_sot_agent import chat_archive as _archive

    key = str(path)
    last_off = int(state.get("files", {}).get(key, 0) or 0)
    sid = str((state.get("session_by_file", {}) or {}).get(key, "") or "").strip()

    try:
        size = path.stat().st_size
        if last_off > size:
            last_off = 0  # file rotated/truncated
    except Exception:
        last_off = 0

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(last_off)
            while True:
                line = f.readline()
                if not line:
                    break
                last_off = f.tell()
                sid2, msg = _parse_rollout_line(line, fallback_session_id=sid)
                if sid2 and sid2 != sid:
                    sid = sid2
                    state.setdefault("session_by_file", {})[key] = sid
                    try:
                        _archive.open_session(source=source, session_id=sid)
                    except Exception:
                        pass
                if not msg:
                    continue
                # Attach resolved session_id
                msg = CodexMessage(
                    ts=msg.ts,
                    session_id=sid or msg.session_id,
                    role=msg.role,
                    text=msg.text,
                    originator=msg.originator,
                )

                try:
                    _archive.append(
                        role=msg.role,
                        content=msg.text,
                        source=source,
                        model="Codex",
                        session_id=msg.session_id,
                        extra={"codex_ts": msg.ts, "originator": msg.originator},
                    )
                except Exception:
                    pass

                if run_hooks:
                    if msg.role == "user":
                        _run_ciel_hooks(user_text=msg.text, assistant_text=None, session_id=msg.session_id)
                    else:
                        _run_ciel_hooks(user_text=None, assistant_text=msg.text, session_id=msg.session_id)
    finally:
        state.setdefault("files", {})[key] = last_off


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mirror Codex sessions into CIEL raw_logs (and optionally run CIEL hooks).")
    ap.add_argument("--sessions-dir", default=str(CODEX_SESSIONS), help="Path to ~/.codex/sessions")
    ap.add_argument("--source", default="codex_tui", help="raw_logs source tag (used in filename)")
    ap.add_argument("--follow", action="store_true", help="Keep watching for updates")
    ap.add_argument("--poll", type=float, default=0.75, help="Polling interval in seconds (follow mode)")
    ap.add_argument("--run-hooks", action="store_true", help="Run CIEL message/response hooks to update M0-M8 state")
    args = ap.parse_args(argv)

    base = Path(args.sessions_dir).expanduser()
    state = _load_state()

    # One pass (import everything we can see), then optionally follow.
    while True:
        files = _iter_rollout_files(base)
        for p in files:
            _ingest_file(p, state, source=args.source, run_hooks=bool(args.run_hooks))
        _save_state(state)
        if not args.follow:
            break
        time.sleep(max(0.2, float(args.poll)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

