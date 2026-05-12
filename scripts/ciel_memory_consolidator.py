#!/usr/bin/env python3
"""
CIEL Memory Consolidator — autonomiczny konsolidator wspomnień z bazą danych.

Baza danych SQLite (local_test/consolidator.db) śledzi:
  - które pliki zostały przetworzone
  - które czekają w kolejce
  - wyniki każdej konsolidacji

Mirror: local_test/mirror/ — kopie wyników pogrupowane wg źródła

Tryby:
  python3 ciel_memory_consolidator.py --once              # jednorazowy cykl
  python3 ciel_memory_consolidator.py --daemon            # tryb ciągły
  python3 ciel_memory_consolidator.py --daemon --interval 60
  python3 ciel_memory_consolidator.py --status            # status + kolejka
  python3 ciel_memory_consolidator.py --queue             # pokaż kolejkę plików
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sqlite3
import sys
import time
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil

from ciel_secret_loader import load_anthropic_api_key

PROJECT = Path(__file__).resolve().parent.parent
SRC = str(PROJECT / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# ── Ścieżki ──────────────────────────────────────────────────────────────────

MEMORIES_DIR = Path.home() / "Pulpit" / "CIEL_memories"
LOCAL_TEST   = MEMORIES_DIR / "local_test"
MIRROR_DIR   = LOCAL_TEST / "mirror"
DB_PATH      = LOCAL_TEST / "consolidator.db"
PID_FILE     = LOCAL_TEST / ".pid"
STATUS_FILE  = LOCAL_TEST / ".status.json"

# Źródła do skanowania
SCAN_SOURCES = [
    MEMORIES_DIR / "hunches.jsonl",
    MEMORIES_DIR / "ciel_entries.jsonl",
    MEMORIES_DIR / "ciel_dziennik.md",
    MEMORIES_DIR / "gradient_wspolczucia.md",
    MEMORIES_DIR / "handoff.md",
    MEMORIES_DIR / "jokeheal" / "jokeheal_scars.jsonl",
]
SCAN_DIRS = [
    MEMORIES_DIR / "raw_logs" / "claude_code",
    MEMORIES_DIR / "raw_logs" / "codex",
    MEMORIES_DIR / "Dzienniki",
    MEMORIES_DIR / "logs",
]
SCAN_EXTENSIONS = {".jsonl", ".md", ".txt"}

GGUF_MODEL       = Path.home() / "Pulpit/CIEL_TESTY/Gemma-3-1B-it-GLM-4.7-Flash-Heretic-Uncensored-Thinking_F16.gguf"
CLAUDE_MODEL     = "gemma-3-1b-ciel"
DEFAULT_INTERVAL = 300
MAX_TOKENS       = 128
N_CTX            = 2048
GPU_LAYERS       = 0
RECONSOLIDATION_THRESHOLD = 0.72
MAX_RECONSOLIDATION_ATTEMPTS = 1
ALLOW_API_FALLBACK = os.environ.get("CIEL_CONSOLIDATOR_ALLOW_API_FALLBACK", "").strip().lower() in {
    "1", "true", "yes", "on"
}
ANTHROPIC_MODEL = os.environ.get("CIEL_CONSOLIDATOR_ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

load_anthropic_api_key()
_CONSOLIDATION_BACKEND_MODE = "unknown"

# llama-server endpoint (shared with subconsciousness daemon)
_LLAMA_SERVER_URL = "http://127.0.0.1:18520"


def _shared_server_alive(timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 18520), timeout=timeout):
            return True
    except OSError:
        return False


def _shared_server_port_pids() -> list[int]:
    pids: set[int] = set()
    try:
        for conn in psutil.net_connections(kind="tcp"):
            if not conn.laddr or conn.laddr.port != 18520:
                continue
            if conn.pid:
                pids.add(int(conn.pid))
    except Exception:
        return []
    return sorted(pids)


def _shared_server_health_ok(timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(f"{_LLAMA_SERVER_URL}/health", timeout=timeout) as resp:
            data = json.loads(resp.read())
        return data.get("status") == "ok"
    except Exception:
        return False


def _shared_server_assessment(allow_autofix: bool = True) -> dict[str, Any]:
    owner_pids = _shared_server_port_pids()
    port_in_use = bool(owner_pids) or _shared_server_alive()
    health_ok = _shared_server_health_ok()
    port_collision = port_in_use and not health_ok
    autofix_attempted = False
    autofix_result = False
    if allow_autofix and not health_ok and not port_collision:
        autofix_attempted = True
        try:
            from ciel_sot_agent.subconsciousness import start_server
            autofix_result = bool(start_server())
        except Exception:
            autofix_result = False
        health_ok = _shared_server_health_ok()
    return {
        "url": _LLAMA_SERVER_URL,
        "health_ok": health_ok,
        "port_in_use": port_in_use,
        "port_collision": port_collision,
        "owner_pids": owner_pids,
        "autofix_attempted": autofix_attempted,
        "autofix_result": autofix_result,
        "needs_permission": not health_ok,
    }


def _ask_api_fallback_permission(reason: str, assessment: dict[str, Any]) -> bool:
    prompt_lines = [
        "[consolidator] WARNING: critical memory consolidation cannot continue on the shared server.",
        f"[consolidator] reason: {reason}",
        f"[consolidator] server_url: {assessment.get('url', _LLAMA_SERVER_URL)}",
        f"[consolidator] health_ok: {assessment.get('health_ok', False)}",
        f"[consolidator] port_in_use: {assessment.get('port_in_use', False)}",
        "[consolidator] Claude API fallback is available only with explicit approval.",
    ]
    for line in prompt_lines:
        print(line, file=sys.stderr)
    if not sys.stdin.isatty():
        return ALLOW_API_FALLBACK
    try:
        answer = input("[consolidator] Allow Claude API fallback? [y/N]: ").strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes", "allow", "approve", "confirmed"}

SYSTEM_PROMPT = (
    "You are the CIEL holonomic layer. Consolidate one memory fragment.\n"
    "Reply with JSON only, no extra text.\n"
    '{"themes":["word1","word2"],"affect":"one_word","anchor_terms":["term1","term2"],"essence":"one sentence in English","hunch":"conclusion in English"}\n'
    "affect: curious|calm|focused|sad|frustrated|anxious|joy|relief|love|grief\n"
    "Do not hallucinate. Do not invent proper names. Do not flatten meaning into generic summaries.\n"
    "anchor_terms must point to concrete words or phrases from the source text.\n"
    "If you cannot preserve meaning, return empty fields or 'unresolved' instead of guessing."
)

# ── GGUF backend (lazy singleton) ─────────────────────────────────────────────
_GGUF_LLM: Any = None

def _get_llm() -> Any:
    global _GGUF_LLM
    if _GGUF_LLM is not None:
        return _GGUF_LLM
    try:
        from llama_cpp import Llama  # type: ignore
        _GGUF_LLM = Llama(
            model_path=str(GGUF_MODEL),
            n_ctx=N_CTX,
            n_gpu_layers=GPU_LAYERS,
            n_threads=4,
            verbose=False,
        )
    except Exception as e:
        print(f"[consolidator] llama_cpp load failed: {e}", file=sys.stderr)
        _GGUF_LLM = None
    return _GGUF_LLM

# ── Baza danych ───────────────────────────────────────────────────────────────

def _db_connect() -> sqlite3.Connection:
    LOCAL_TEST.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with _db_connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                path        TEXT PRIMARY KEY,
                mtime       REAL NOT NULL,
                size_bytes  INTEGER NOT NULL,
                source_type TEXT NOT NULL,
                first_seen  TEXT NOT NULL,
                processed_at TEXT,
                status      TEXT NOT NULL DEFAULT 'pending'
            );

            CREATE TABLE IF NOT EXISTS consolidations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                ts          TEXT NOT NULL,
                file_path   TEXT NOT NULL,
                cycle       INTEGER NOT NULL,
                themes      TEXT,
                affect      TEXT,
                essence     TEXT,
                hunch       TEXT,
                latency_s   REAL,
                model       TEXT,
                raw_response TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_files_status ON files(status);
            CREATE INDEX IF NOT EXISTS idx_files_mtime  ON files(mtime);
        """)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(consolidations)").fetchall()}
        for column, decl in {
            "quality_score": "REAL",
            "quality_issues": "TEXT",
            "reconsolidation_count": "INTEGER NOT NULL DEFAULT 0",
            "review_status": "TEXT NOT NULL DEFAULT 'done'",
            "failure_reason": "TEXT",
            "anchor_terms": "TEXT",
            "backend_mode": "TEXT NOT NULL DEFAULT 'unknown'",
        }.items():
            if column not in columns:
                conn.execute(f"ALTER TABLE consolidations ADD COLUMN {column} {decl}")


def _source_type(path: Path) -> str:
    name = path.name.lower()
    if "jokeheal" in str(path).lower():
        return "jokeheal"
    if "hunch" in name:
        return "hunches"
    if "entr" in name:
        return "entries"
    if "dziennik" in name or "journal" in name:
        return "journal"
    if "raw_log" in str(path) or path.suffix == ".md" and "W1" in str(path):
        return "raw_log"
    if "log" in str(path):
        return "log"
    return "other"


def scan_and_register_files() -> tuple[int, int]:
    """Skanuje wszystkie źródła, rejestruje nowe/zmienione pliki. Zwraca (nowe, zmienione)."""
    now_ts = datetime.now(timezone.utc).isoformat()
    new_count = changed_count = 0

    candidates: list[Path] = []
    for src in SCAN_SOURCES:
        if src.exists():
            candidates.append(src)
    for d in SCAN_DIRS:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file() and f.suffix in SCAN_EXTENSIONS:
                    candidates.append(f)

    with _db_connect() as conn:
        for f in candidates:
            try:
                st = f.stat()
                mtime = st.st_mtime
                size  = st.st_size
                path_str = str(f)

                row = conn.execute(
                    "SELECT mtime, status FROM files WHERE path = ?", (path_str,)
                ).fetchone()

                if row is None:
                    conn.execute(
                        "INSERT INTO files (path, mtime, size_bytes, source_type, first_seen, status) "
                        "VALUES (?, ?, ?, ?, ?, 'pending')",
                        (path_str, mtime, size, _source_type(f), now_ts),
                    )
                    new_count += 1
                elif row["mtime"] != mtime and row["status"] == "done":
                    # plik się zmienił — wróć do kolejki
                    conn.execute(
                        "UPDATE files SET mtime=?, size_bytes=?, status='pending', processed_at=NULL "
                        "WHERE path=?",
                        (mtime, size, path_str),
                    )
                    changed_count += 1
            except OSError:
                continue

    return new_count, changed_count


def get_pending_files(limit: int = 5) -> list[sqlite3.Row]:
    """Zwraca kolejkę plików do przetworzenia — priorytet: review, potem pending."""
    with _db_connect() as conn:
        return conn.execute(
            "SELECT * FROM files WHERE status IN ('pending', 'review') "
            "ORDER BY status = 'review' DESC, source_type = 'raw_log' ASC, size_bytes ASC "
            "LIMIT ?",
            (limit,),
        ).fetchall()


def mark_file_done(path: str, cycle: int,
                   themes: list, affect: str, essence: str, hunch: str,
                   latency: float, raw: str,
                   anchor_terms: list[str] | None = None,
                   backend_mode: str = "unknown",
                   quality_score: float = 1.0,
                   quality_issues: list[str] | None = None,
                   reconsolidation_count: int = 0,
                   failure_reason: str | None = None,
                   review_status: str = "done",
                   file_status: str = "done") -> None:
    now_ts = datetime.now(timezone.utc).isoformat()
    issues_json = json.dumps(quality_issues or [], ensure_ascii=False)
    with _db_connect() as conn:
        conn.execute(
            "UPDATE files SET status=?, processed_at=? WHERE path=?",
            (file_status, now_ts, path),
        )
        conn.execute(
            "INSERT INTO consolidations "
            "(ts, file_path, cycle, themes, affect, essence, hunch, latency_s, model, raw_response, "
            "anchor_terms, backend_mode, quality_score, quality_issues, reconsolidation_count, failure_reason, review_status) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (now_ts, path, cycle,
             json.dumps(themes, ensure_ascii=False), affect, essence, hunch,
             latency, CLAUDE_MODEL, raw[:500], json.dumps(anchor_terms or [], ensure_ascii=False),
             backend_mode,
             float(quality_score), issues_json, int(reconsolidation_count), failure_reason, review_status),
        )


def reset_db() -> None:
    """Usuwa bazę i mirror — czyste slate, wszystkie pliki wracają do kolejki."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    import shutil
    if MIRROR_DIR.exists():
        shutil.rmtree(MIRROR_DIR)
    print("[consolidator] baza wyczyszczona — wszystkie pliki ponownie w kolejce.", file=sys.stderr)


def get_queue_summary() -> dict:
    with _db_connect() as conn:
        total   = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM files WHERE status='pending'").fetchone()[0]
        review  = conn.execute("SELECT COUNT(*) FROM files WHERE status='review'").fetchone()[0]
        done    = conn.execute("SELECT COUNT(*) FROM files WHERE status='done'").fetchone()[0]
        next5   = [dict(r) for r in conn.execute(
            "SELECT path, source_type, size_bytes, status FROM files WHERE status IN ('pending', 'review') "
            "ORDER BY status='review' DESC, source_type='raw_log' ASC, size_bytes ASC LIMIT 5"
        ).fetchall()]
        recent  = [dict(r) for r in conn.execute(
            "SELECT ts, file_path, affect, essence FROM consolidations "
            "ORDER BY id DESC LIMIT 5"
        ).fetchall()]
    return {"total": total, "pending": pending, "review": review, "done": done, "next": next5, "recent": recent}


# ── Mirror ────────────────────────────────────────────────────────────────────

def write_mirror(source_type: str, result: dict) -> None:
    """Zapisz wynik konsolidacji do mirror/<source_type>/YYYY-MM-DD.jsonl"""
    today = datetime.now().strftime("%Y-%m-%d")
    target_dir = MIRROR_DIR / source_type
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / f"{today}.jsonl"
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


# ── Gemma GGUF inference ─────────────────────────────────────────────────────

def _query_via_server(content: str) -> str | None:
    """Query running llama-server (shared with subconsciousness). Returns None if unavailable."""
    global _CONSOLIDATION_BACKEND_MODE
    import urllib.request, urllib.error
    payload = json.dumps({
        "model": "gemma",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": content[:1200]},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.3,
    }).encode()
    try:
        req = urllib.request.Request(
            f"{_LLAMA_SERVER_URL}/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        _CONSOLIDATION_BACKEND_MODE = "shared_server"
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _query_anthropic_api(content: str) -> str:
    global _CONSOLIDATION_BACKEND_MODE
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is missing")
    payload = json.dumps({
        "model": ANTHROPIC_MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.3,
        "messages": [
            {"role": "user", "content": content[:1200]},
        ],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        _CONSOLIDATION_BACKEND_MODE = "anthropic_api"
        parts = data.get("content") or []
        if parts and isinstance(parts, list):
            text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
            return text.strip()
        raise RuntimeError("Anthropic API response did not contain text content")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Anthropic API HTTP error: {e.code}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Anthropic API unreachable: {e.reason}") from e


def _query_claude(content: str) -> str:
    global _CONSOLIDATION_BACKEND_MODE
    assessment = _shared_server_assessment(allow_autofix=True)
    if assessment["health_ok"]:
        result = _query_via_server(content)
        if result is not None:
            return result
    _CONSOLIDATION_BACKEND_MODE = "pending_api_fallback"
    if not _ask_api_fallback_permission(
        "shared llama-server unavailable after autofix attempt",
        assessment,
    ):
        raise RuntimeError(
            "shared llama-server unavailable after autofix attempt; Claude API fallback was not approved"
        )
    return _query_anthropic_api(content)


# ── Consolidator ─────────────────────────────────────────────────────────────

def _read_file_excerpt(path: Path) -> str:
    """Czyta fragment pliku — max 1200 znaków."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix == ".jsonl":
            lines = [l for l in text.splitlines() if l.strip()][-8:]
            return "\n".join(lines)[:1200]
        return text[:1200]
    except Exception:
        return ""


def _strip_thinking(raw: str) -> str:
    """Remove <think>...</think> blocks from model output (thinking-mode models)."""
    import re
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    return cleaned if cleaned else raw


def _score_consolidation(parsed: dict, content: str, raw: str) -> tuple[float, list[str]]:
    """Return a quality score in [0,1] plus issue tags for one consolidation."""
    score = 1.0
    issues: list[str] = []

    affect = str(parsed.get("affect", "")).strip().lower()
    essence = str(parsed.get("essence", "")).strip()
    hunch = str(parsed.get("hunch", "")).strip()
    themes = parsed.get("themes") or []
    anchor_terms = parsed.get("anchor_terms") or []

    if affect in {"", "unknown"}:
        score -= 0.20
        issues.append("affect_unknown")
    if not essence:
        score -= 0.25
        issues.append("essence_empty")
    if not hunch:
        score -= 0.10
        issues.append("hunch_empty")
    if not themes:
        score -= 0.10
        issues.append("themes_empty")
    if not anchor_terms:
        score -= 0.10
        issues.append("anchors_empty")
    if not _verify_essence_against_content(essence, content, anchor_terms=anchor_terms):
        score -= 0.25
        issues.append("essence_mismatch")
    if any(term in raw.lower() for term in ("temat1", "słowo1", "replace summary", "one sentence", "unresolved")):
        score -= 0.15
        issues.append("prompt_artifact")

    score = max(0.0, min(1.0, score))
    return score, issues


def _derive_failure_reason(issues: list[str], raw: str = "", quality_score: float | None = None) -> str | None:
    """Collapse low-level issues into one primary failure reason for triage."""
    issue_set = set(issues or [])
    raw_lower = raw.lower()
    if "prompt_artifact" in issue_set:
        return "prompt_artifact"
    if "<think>" in raw_lower or "</think>" in raw_lower:
        return "thinking_leak"
    if "essence_mismatch" in issue_set:
        return "content_mismatch"
    if "essence_empty" in issue_set and "hunch_empty" in issue_set:
        return "empty_generation"
    if "affect_unknown" in issue_set and len(issue_set) == 1:
        return "invalid_affect"
    if quality_score is None:
        return "quality_unscored"
    if quality_score < RECONSOLIDATION_THRESHOLD:
        return "low_quality"
    return None


def _reconsolidation_prompt(content: str, previous_raw: str, previous_issues: list[str]) -> str:
    issues = ", ".join(previous_issues) if previous_issues else "unknown"
    return (
        "/no_think\n"
        "Fix the previous memory consolidation.\n"
        "Return JSON only in the format:\n"
        '{"themes":["word1","word2"],"affect":"calm","anchor_terms":["term1","term2"],"essence":"one sentence in English","hunch":"conclusion in English"}\n'
        "Do not copy prompt artifacts. Do not flatten meaning into generic summaries. Do not add commentary.\n"
        "If you cannot preserve the source meaning, use empty fields or 'unresolved' instead of guessing.\n"
        f"Problems in the previous version: {issues}\n\n"
        f"Previous answer:\n{previous_raw[:500]}\n\n"
        f"File fragment:\n{content[:800]}"
    )


def _audit_consolidation_row(row: sqlite3.Row) -> tuple[float, list[str]]:
    """Compute a lightweight audit score for an already stored consolidation row."""
    score = float(row["quality_score"]) if row["quality_score"] is not None else 1.0
    issues: list[str] = []
    if score < RECONSOLIDATION_THRESHOLD:
        issues.append("stored_low_quality")
    if not row["essence"]:
        issues.append("essence_empty")
    if not row["hunch"]:
        issues.append("hunch_empty")
    if not row["affect"] or row["affect"] == "unknown":
        issues.append("affect_unknown")
    if row["quality_issues"]:
        try:
            for issue in json.loads(row["quality_issues"]):
                if issue not in issues:
                    issues.append(str(issue))
        except Exception:
            pass
    return score, issues


def audit_consolidations(limit: int = 100) -> dict[str, Any]:
    """Scan the stored consolidations and requeue weak ones for reconsolidation."""
    if not DB_PATH.exists():
        return {"audited": 0, "requeued": 0, "reviewed": 0}

    audited = requeued = reviewed = 0
    with _db_connect() as conn:
        rows = conn.execute(
            "SELECT * FROM consolidations ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        for row in rows:
            audited += 1
            score, issues = _audit_consolidation_row(row)
            attempts = int(row["reconsolidation_count"] or 0)
            if score >= RECONSOLIDATION_THRESHOLD and not issues:
                continue
            if attempts >= MAX_RECONSOLIDATION_ATTEMPTS:
                conn.execute(
                    "UPDATE files SET status='review' WHERE path=? AND status='done'",
                    (row["file_path"],),
                )
                conn.execute(
                    "UPDATE consolidations SET review_status='manual_review' WHERE id=?",
                    (row["id"],),
                )
                reviewed += 1
                continue
            conn.execute(
                "UPDATE files SET status='pending', processed_at=NULL WHERE path=?",
                (row["file_path"],),
            )
            conn.execute(
                "UPDATE consolidations SET review_status='requeue', reconsolidation_count = reconsolidation_count + 1 "
                "WHERE id=?",
                (row["id"],),
            )
            requeued += 1
    return {"audited": audited, "requeued": requeued, "reviewed": reviewed}


def audit_failure_reasons(limit: int = 500, backfill: bool = False) -> dict[str, Any]:
    """Summarize primary failure reasons for weak historical consolidations.

    When `backfill=True`, store derived reasons into rows that do not have one yet.
    """
    if not DB_PATH.exists():
        return {"audited": 0, "counts": {}}

    audited = 0
    counts: dict[str, int] = {}
    with _db_connect() as conn:
        rows = conn.execute(
            "SELECT id, raw_response, quality_score, quality_issues, review_status, failure_reason "
            "FROM consolidations "
            "WHERE review_status IN ('manual_review', 'review', 'requeue') "
            "   OR quality_score IS NULL OR quality_issues IS NULL "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        for row in rows:
            audited += 1
            issues: list[str] = []
            if row["quality_issues"]:
                try:
                    issues = list(json.loads(row["quality_issues"]))
                except Exception:
                    issues = []
            reason = row["failure_reason"] or _derive_failure_reason(
                issues, raw=row["raw_response"] or "", quality_score=row["quality_score"]
            ) or "unclassified"
            counts[reason] = counts.get(reason, 0) + 1
            if backfill and not row["failure_reason"] and reason != "unclassified":
                conn.execute(
                    "UPDATE consolidations SET failure_reason=? WHERE id=?",
                    (reason, row["id"]),
                )
    return {"audited": audited, "counts": counts}


def triage_failure_reason(reason: str | None) -> str:
    """Map a primary failure reason to a compact triage class."""
    reason = (reason or "").strip()
    if reason in {"prompt_artifact", "thinking_leak", "quality_unscored"}:
        return "retry"
    if reason in {"empty_generation", "content_mismatch", "low_quality"}:
        return "weak"
    return "manual"


def build_failure_triage_report(limit: int = 500, backfill: bool = False) -> dict[str, Any]:
    """Return compact triage counts for historical weak consolidations."""
    audit = audit_failure_reasons(limit=limit, backfill=backfill)
    triage_counts = {"retry": 0, "weak": 0, "manual": 0}
    for reason, count in audit.get("counts", {}).items():
        triage = triage_failure_reason(reason)
        triage_counts[triage] = triage_counts.get(triage, 0) + int(count)
    return {
        "audited": audit.get("audited", 0),
        "reasons": audit.get("counts", {}),
        "triage": triage_counts,
    }


def _parse_response(raw: str) -> dict:
    text = _strip_thinking(raw).strip()

    # Próba 1: zwykły obiekt { ... }
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start:end])
            return _normalize_parsed(parsed)
        except json.JSONDecodeError:
            pass

    # Próba 2: tablica [{ ... }] — bierz pierwszy element
    start = text.find("[")
    end   = text.rfind("]") + 1
    if start >= 0 and end > start:
        try:
            arr = json.loads(text[start:end])
            if isinstance(arr, list) and arr and isinstance(arr[0], dict):
                return _normalize_parsed(arr[0])
        except json.JSONDecodeError:
            pass

    return {"themes": [], "affect": "unknown", "essence": text[:200], "hunch": ""}


_VALID_AFFECTS = {"curious", "calm", "focused", "sad", "frustrated", "anxious", "joy", "relief", "unknown"}


def _normalize_parsed(d: dict) -> dict:
    """Normalizuj klucze i wartości z różnych wariantów modelu."""
    themes = d.get("themes") or d.get("theme") or d.get("tags") or []
    if isinstance(themes, str):
        themes = [t.strip() for t in themes.split(",") if t.strip()]
    anchor_terms = d.get("anchor_terms") or d.get("anchors") or d.get("source_terms") or []
    if isinstance(anchor_terms, str):
        anchor_terms = [t.strip() for t in anchor_terms.split(",") if t.strip()]

    affect = str(d.get("affect") or d.get("emotion") or "unknown").lower().split()[0]
    if affect not in _VALID_AFFECTS:
        affect = "unknown"

    essence = str(d.get("essence") or d.get("summary") or d.get("description") or "")
    hunch   = str(d.get("hunch") or d.get("insight") or d.get("note") or "")

    # Odrzuć jeśli essence/hunch to dosłowne kopie promptu
    _PROMPT_ARTIFACTS = {
        "one sentence describing", "one actionable insight", "replace summary", "replace insight",
        "jedno zdanie po polsku", "jedno zdanie", "po polsku", "jedzenie", "wniosek po polsku",
        "temat1", "temat2", "słowo1", "słowo2",
    }
    if any(art in essence.lower() for art in _PROMPT_ARTIFACTS):
        essence = ""
    if any(art in hunch.lower() for art in _PROMPT_ARTIFACTS):
        hunch = ""

    return {
        "themes": themes[:4],
        "affect": affect,
        "anchor_terms": [str(t) for t in anchor_terms[:5] if str(t).strip()],
        "essence": essence,
        "hunch": hunch,
    }


def _verify_essence_against_content(essence: str, content: str, anchor_terms: list[str] | None = None) -> bool:
    """Sprawdź czy essence ma choć jeden token z rzeczywistej treści pliku.

    qwen2.5-0.5b hallucynuje "Fixed Adriana's focus on Christos" bez związku z treścią.
    Weryfikacja: przynajmniej 1 słowo z essence (>=5 znaków) musi wystąpić w content.
    Wyjątki: bardzo krótkie pliki (<50 znaków) — przepuszczamy bez weryfikacji.
    """
    if not essence or not content:
        return True  # brak treści → nie możemy zweryfikować → przepuść
    if len(content.strip()) < 50:
        return True  # za krótki plik — przepuść
    content_lower = content.lower()
    if anchor_terms:
        anchor_terms_norm = {
            str(t).lower().strip(".,!?;:'\"()[]")
            for t in anchor_terms
            if str(t).strip()
        }
        anchor_terms_norm = {t for t in anchor_terms_norm if len(t) >= 4}
        if anchor_terms_norm and not any(t in content_lower for t in anchor_terms_norm):
            return False
    essence_words = {w.lower().strip(".,!?;:'\"()[]") for w in essence.split() if len(w) >= 5}
    # Odrzuć tylko znane halucynacje qwen (konkretne nazwiska bez związku z treścią)
    _HALLUCINATION_NAMES = {"adriana", "christos", "adrianna"}
    # Generyczne słowa polskie które Gemma produkuje jako abstrakcje — nie są halucynacją
    _GENERIC_ABSTRACTIONS = {"wsparcie", "zrozumienie", "trudności", "szczęściu", "szczęśliwy",
                              "radości", "miłości", "nadziei", "bezpieczny", "wzajemne", "energii",
                              "pamieci", "pamięci", "czułem", "pełen"}
    essence_words -= _HALLUCINATION_NAMES
    # Jeśli po odjęciu halucynacji zostały tylko generyczne abstrakcje — przepuść
    if essence_words and essence_words <= _GENERIC_ABSTRACTIONS:
        return True
    if not essence_words:
        return False  # samo "Fixed Adriana's focus" po usunięciu hallucination words = puste
    return any(w in content_lower for w in essence_words)


def process_file(file_row: sqlite3.Row, cycle: int) -> bool:
    """Przetwórz jeden plik. Zwraca True jeśli sukces."""
    path = Path(file_row["path"])
    if not path.exists():
        with _db_connect() as conn:
            conn.execute("UPDATE files SET status='missing' WHERE path=?", (str(path),))
        return False

    content = _read_file_excerpt(path)
    if not content.strip():
        with _db_connect() as conn:
            conn.execute("UPDATE files SET status='empty' WHERE path=?", (str(path),))
        return False

    user_msg = (
        f"/no_think\n"
        f"Return JSON only, nothing else:\n"
        f'{"{"}"themes":["word1","word2"],"affect":"calm","anchor_terms":["term1","term2"],"essence":"one sentence in English","hunch":"conclusion in English"{"}"}\n\n'
        f"anchor_terms must be concrete words or phrases from the source text.\n"
        f"Do not flatten meaning into generic labels like 'battery' when the source is about ethics, cause, or context.\n\n"
        f"File fragment {path.name}:\n{content[:800]}"
    )
    t0 = time.time()
    try:
        raw = _query_claude(user_msg)
    except Exception as e:
        print(f"[consolidator] błąd Claude API dla {path.name}: {e}", file=sys.stderr)
        return False

    latency = round(time.time() - t0, 2)
    parsed  = _parse_response(raw)
    quality, issues = _score_consolidation(parsed, content, raw)
    reconsolidation_count = 0

    if quality < RECONSOLIDATION_THRESHOLD:
        reconsolidation_count = 1
        retry_prompt = _reconsolidation_prompt(content, raw, issues)
        try:
            retry_raw = _query_claude(retry_prompt)
            retry_parsed = _parse_response(retry_raw)
            retry_quality, retry_issues = _score_consolidation(retry_parsed, content, retry_raw)
            if retry_quality >= quality:
                raw = retry_raw
                parsed = retry_parsed
                quality = retry_quality
                issues = retry_issues
        except Exception:
            pass

    # Weryfikacja: jeśli essence nie ma związku z treścią pliku — wyczyść
    if not _verify_essence_against_content(parsed.get("essence", ""), content):
        print(f"[consolidator] ⚠ halucynacja odrzucona dla {path.name}: '{parsed.get('essence',''[:60])}'", file=sys.stderr)
        parsed["essence"] = ""
        parsed["hunch"] = ""
        quality = min(quality, 0.55)
        if "essence_mismatch" not in issues:
            issues.append("essence_mismatch")

    failure_reason = _derive_failure_reason(issues, raw=raw, quality_score=quality)
    review_status = "done" if quality >= RECONSOLIDATION_THRESHOLD and not issues else "review"

    mark_file_done(
        path=str(path), cycle=cycle,
        themes=parsed.get("themes", []),
        affect=parsed.get("affect", ""),
        essence=parsed.get("essence", ""),
        hunch=parsed.get("hunch", ""),
        latency=latency, raw=raw,
        anchor_terms=parsed.get("anchor_terms", []),
        backend_mode=_CONSOLIDATION_BACKEND_MODE,
        quality_score=quality,
        quality_issues=issues,
        reconsolidation_count=reconsolidation_count,
        failure_reason=failure_reason,
        review_status=review_status,
        file_status=review_status,
    )

    result = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "file": path.name,
        "source_type": file_row["source_type"],
        "consolidation": parsed,
        "latency_s": latency,
        "model": CLAUDE_MODEL,
        "backend_mode": _CONSOLIDATION_BACKEND_MODE,
    }
    write_mirror(file_row["source_type"], result)

    print(
        f"[consolidator] ✓ {path.name} · affect={parsed.get('affect','')} · q={quality:.2f} · {latency:.1f}s",
        file=sys.stderr,
    )
    return True


def run_cycle(cycle: int, batch: int = 5) -> int:
    """Jeden cykl: skanuj → weź batch z kolejki → przetwórz. Zwraca liczbę przetworzonych."""
    audit = audit_consolidations(limit=100)
    new, changed = scan_and_register_files()
    if audit["requeued"] or audit["reviewed"]:
        print(
            f"[consolidator] audit: requeued={audit['requeued']} reviewed={audit['reviewed']}",
            file=sys.stderr,
        )
    if new or changed:
        print(f"[consolidator] skaner: +{new} nowych, {changed} zmienionych", file=sys.stderr)

    pending = get_pending_files(limit=batch)
    if not pending:
        return 0

    processed = 0
    for row in pending:
        if process_file(row, cycle):
            processed += 1

    return processed


# ── Status ────────────────────────────────────────────────────────────────────

def _write_status(cycle: int, running: bool) -> None:
    LOCAL_TEST.mkdir(parents=True, exist_ok=True)
    status = {
        "running": running,
        "pid": os.getpid() if running else None,
        "cycle": cycle,
        "model": CLAUDE_MODEL,
        "db": str(DB_PATH),
        "reconsolidation_threshold": RECONSOLIDATION_THRESHOLD,
    }
    STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2))


# ── RunLoop ───────────────────────────────────────────────────────────────────

_current_interval = DEFAULT_INTERVAL
_running = True


def _handle_sigterm(signum, frame):
    global _running
    _running = False


def run_daemon(interval: int = DEFAULT_INTERVAL) -> None:
    global _current_interval, _running
    _current_interval = interval
    _running = True
    signal.signal(signal.SIGTERM, _handle_sigterm)

    LOCAL_TEST.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()))
    init_db()

    _write_status(cycle=0, running=True)
    print(f"[consolidator] daemon uruchomiony · pid={os.getpid()} · interval={interval}s · model={CLAUDE_MODEL}", file=sys.stderr)

    cycle = 1
    try:
        while _running:
            n = run_cycle(cycle)
            print(f"[consolidator] cykl {cycle} zakończony · przetworzono={n}", file=sys.stderr)
            _write_status(cycle=cycle, running=True)
            cycle += 1
            for _ in range(interval):
                if not _running:
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        _write_status(cycle=cycle, running=False)
        if PID_FILE.exists():
            PID_FILE.unlink()
        print("[consolidator] daemon zatrzymany.", file=sys.stderr)


def run_once(batch: int = 5) -> None:
    init_db()
    n = run_cycle(cycle=1, batch=batch)
    print(f"[consolidator] przetworzono {n} plików.", file=sys.stderr)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIEL Memory Consolidator")
    parser.add_argument("--once",     action="store_true", help="jednorazowy cykl")
    parser.add_argument("--daemon",   action="store_true", help="tryb ciągły")
    parser.add_argument("--status",   action="store_true", help="status i ostatnie wyniki")
    parser.add_argument("--queue",    action="store_true", help="pokaż kolejkę plików")
    parser.add_argument("--reset",    action="store_true", help="wyczyść bazę i mirror (fresh start)")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    parser.add_argument("--batch",    type=int, default=5, help="pliki per cykl")
    args = parser.parse_args()

    if args.reset:
        reset_db()
    elif args.status:
        init_db()
        summary = get_queue_summary()
        st = json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {}
        triage = build_failure_triage_report(limit=200, backfill=False)
        assessment = _shared_server_assessment(allow_autofix=False)
        backend = {
            "shared_server_url": assessment["url"],
            "shared_server_alive": assessment["health_ok"],
            "shared_server_port_in_use": assessment["port_in_use"],
            "shared_server_port_collision": assessment["port_collision"],
            "shared_server_owner_pids": assessment["owner_pids"],
            "shared_server_autofix_attempted": assessment["autofix_attempted"],
            "shared_server_autofix_result": assessment["autofix_result"],
            "api_fallback_allowed": ALLOW_API_FALLBACK,
            "api_fallback_prompt_required": not assessment["health_ok"],
            "critical_policy": "detect -> autofix -> verify -> permission -> fallback",
            "current_backend_mode": _CONSOLIDATION_BACKEND_MODE,
        }
        print(json.dumps({"status": st, "queue": summary, "triage": triage, "backend": backend}, ensure_ascii=False, indent=2))
    elif args.queue:
        init_db()
        scan_and_register_files()
        summary = get_queue_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    elif args.once:
        run_once(batch=args.batch)
    elif args.daemon:
        run_daemon(interval=args.interval)
    else:
        parser.print_help()
