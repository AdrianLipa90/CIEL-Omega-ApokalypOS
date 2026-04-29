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
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

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
]
SCAN_DIRS = [
    MEMORIES_DIR / "raw_logs" / "claude_code",
    MEMORIES_DIR / "Dzienniki",
    MEMORIES_DIR / "logs",
]
SCAN_EXTENSIONS = {".jsonl", ".md", ".txt"}

# Model i serwer
LLAMA_SERVER = (
    Path.home()
    / "Pulpit/CIEL_TESTY/CIEL1/src/CIEL_OMEGA_COMPLETE_SYSTEM"
    / "ciel_omega/llm/adapters/llama_cpp/bin/llama-server"
)
MODEL_PATH = Path.home() / "Dokumenty/co8/qwen2.5-0.5b-instruct-q2_k.gguf"
LLAMA_PORT = 8765
LLAMA_URL  = f"http://localhost:{LLAMA_PORT}/v1/chat/completions"

DEFAULT_INTERVAL = 300
MAX_TOKENS       = 256
N_CTX            = 2048

SYSTEM_PROMPT = (
    "Analyze the memory file. Output JSON only, no other text.\n"
    'Example output: {"themes":["portal","debugging"],"affect":"focused","essence":"Fixed portal hunches refresh bug.","hunch":"Check auto-refresh every session."}\n'
    "affect must be one word: curious calm focused sad frustrated anxious joy relief\n"
    "themes: 2-3 keywords from the actual content.\n"
    "essence: one real sentence about what the file contains.\n"
    "hunch: one real takeaway for future."
)

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


def _source_type(path: Path) -> str:
    name = path.name.lower()
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
    """Zwraca kolejkę plików do przetworzenia — priorytet: małe pliki najpierw, potem reszta."""
    with _db_connect() as conn:
        return conn.execute(
            "SELECT * FROM files WHERE status = 'pending' "
            "ORDER BY source_type = 'raw_log' ASC, size_bytes ASC "
            "LIMIT ?",
            (limit,),
        ).fetchall()


def mark_file_done(path: str, cycle: int,
                   themes: list, affect: str, essence: str, hunch: str,
                   latency: float, raw: str) -> None:
    now_ts = datetime.now(timezone.utc).isoformat()
    with _db_connect() as conn:
        conn.execute(
            "UPDATE files SET status='done', processed_at=? WHERE path=?",
            (now_ts, path),
        )
        conn.execute(
            "INSERT INTO consolidations "
            "(ts, file_path, cycle, themes, affect, essence, hunch, latency_s, model, raw_response) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (now_ts, path, cycle,
             json.dumps(themes, ensure_ascii=False), affect, essence, hunch,
             latency, MODEL_PATH.name, raw[:500]),
        )


def get_queue_summary() -> dict:
    with _db_connect() as conn:
        total   = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM files WHERE status='pending'").fetchone()[0]
        done    = conn.execute("SELECT COUNT(*) FROM files WHERE status='done'").fetchone()[0]
        next5   = [dict(r) for r in conn.execute(
            "SELECT path, source_type, size_bytes FROM files WHERE status='pending' "
            "ORDER BY source_type='raw_log' ASC, size_bytes ASC LIMIT 5"
        ).fetchall()]
        recent  = [dict(r) for r in conn.execute(
            "SELECT ts, file_path, affect, essence FROM consolidations "
            "ORDER BY id DESC LIMIT 5"
        ).fetchall()]
    return {"total": total, "pending": pending, "done": done, "next": next5, "recent": recent}


# ── Mirror ────────────────────────────────────────────────────────────────────

def write_mirror(source_type: str, result: dict) -> None:
    """Zapisz wynik konsolidacji do mirror/<source_type>/YYYY-MM-DD.jsonl"""
    today = datetime.now().strftime("%Y-%m-%d")
    target_dir = MIRROR_DIR / source_type
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / f"{today}.jsonl"
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


# ── LlamaServer ──────────────────────────────────────────────────────────────

_server_proc: subprocess.Popen | None = None


def start_llama_server() -> bool:
    global _server_proc
    if not LLAMA_SERVER.exists():
        print(f"[consolidator] BŁĄD: llama-server nie znaleziony: {LLAMA_SERVER}", file=sys.stderr)
        return False
    if not MODEL_PATH.exists():
        print(f"[consolidator] BŁĄD: model nie znaleziony: {MODEL_PATH}", file=sys.stderr)
        return False
    if _is_server_running():
        return True

    print(f"[consolidator] Uruchamiam llama-server ({MODEL_PATH.name})...", file=sys.stderr)
    _server_proc = subprocess.Popen(
        [str(LLAMA_SERVER), "--model", str(MODEL_PATH),
         "--port", str(LLAMA_PORT), "--ctx-size", str(N_CTX),
         "--n-gpu-layers", "99", "--threads", "4", "--log-disable"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(40):
        time.sleep(1)
        if _is_server_running():
            print(f"[consolidator] llama-server gotowy (pid={_server_proc.pid})", file=sys.stderr)
            return True
        if _server_proc.poll() is not None:
            print("[consolidator] llama-server zakończył się przedwcześnie", file=sys.stderr)
            return False
    print("[consolidator] llama-server timeout", file=sys.stderr)
    return False


def stop_llama_server() -> None:
    global _server_proc
    if _server_proc and _server_proc.poll() is None:
        _server_proc.terminate()
        try:
            _server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _server_proc.kill()
    _server_proc = None


def _is_server_running() -> bool:
    try:
        with urllib.request.urlopen(
            f"http://localhost:{LLAMA_PORT}/health", timeout=2
        ) as r:
            return r.status == 200
    except Exception:
        return False


# ── Consolidator ─────────────────────────────────────────────────────────────

def _read_file_excerpt(path: Path) -> str:
    """Czyta fragment pliku — max 1200 znaków."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix == ".jsonl":
            # Czytaj ostatnie 8 linii
            lines = [l for l in text.splitlines() if l.strip()][-8:]
            return "\n".join(lines)[:1200]
        return text[:1200]
    except Exception:
        return ""


def _query_llama(content: str) -> str:
    payload = json.dumps({
        "model": "local",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.3,
        "stop": ["\n\n"],
    }).encode("utf-8")
    req = urllib.request.Request(
        LLAMA_URL, data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip()


def _parse_response(raw: str) -> dict:
    text = raw.strip()

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

    affect = str(d.get("affect") or d.get("emotion") or "unknown").lower().split()[0]
    if affect not in _VALID_AFFECTS:
        affect = "unknown"

    essence = str(d.get("essence") or d.get("summary") or d.get("description") or "")
    hunch   = str(d.get("hunch") or d.get("insight") or d.get("note") or "")

    # Odrzuć jeśli essence/hunch to dosłowne kopie promptu
    _PROMPT_ARTIFACTS = {"one sentence describing", "one actionable insight", "replace summary", "replace insight"}
    if any(art in essence.lower() for art in _PROMPT_ARTIFACTS):
        essence = ""
    if any(art in hunch.lower() for art in _PROMPT_ARTIFACTS):
        hunch = ""

    return {"themes": themes[:4], "affect": affect, "essence": essence, "hunch": hunch}


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

    user_msg = f"File: {path.name}\n\n{content}"
    t0 = time.time()
    try:
        raw = _query_llama(user_msg)
    except Exception as e:
        print(f"[consolidator] błąd llama dla {path.name}: {e}", file=sys.stderr)
        return False

    latency = round(time.time() - t0, 2)
    parsed  = _parse_response(raw)

    mark_file_done(
        path=str(path), cycle=cycle,
        themes=parsed.get("themes", []),
        affect=parsed.get("affect", ""),
        essence=parsed.get("essence", ""),
        hunch=parsed.get("hunch", ""),
        latency=latency, raw=raw,
    )

    result = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "file": path.name,
        "source_type": file_row["source_type"],
        "consolidation": parsed,
        "latency_s": latency,
        "model": MODEL_PATH.name,
    }
    write_mirror(file_row["source_type"], result)

    print(
        f"[consolidator] ✓ {path.name} · affect={parsed.get('affect','')} · {latency:.1f}s",
        file=sys.stderr,
    )
    return True


def run_cycle(cycle: int, batch: int = 5) -> int:
    """Jeden cykl: skanuj → weź batch z kolejki → przetwórz. Zwraca liczbę przetworzonych."""
    new, changed = scan_and_register_files()
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
        "model": MODEL_PATH.name,
        "db": str(DB_PATH),
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

    if not start_llama_server():
        print("[consolidator] nie udało się uruchomić llama-server. Kończę.", file=sys.stderr)
        return

    _write_status(cycle=0, running=True)
    print(f"[consolidator] daemon uruchomiony · pid={os.getpid()} · interval={interval}s · model={MODEL_PATH.name}", file=sys.stderr)

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
        stop_llama_server()
        if PID_FILE.exists():
            PID_FILE.unlink()
        print("[consolidator] daemon zatrzymany.", file=sys.stderr)


def run_once(batch: int = 5) -> None:
    init_db()
    if not start_llama_server():
        print("[consolidator] nie udało się uruchomić llama-server.", file=sys.stderr)
        return
    try:
        n = run_cycle(cycle=1, batch=batch)
        print(f"[consolidator] przetworzono {n} plików.", file=sys.stderr)
    finally:
        stop_llama_server()


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIEL Memory Consolidator")
    parser.add_argument("--once",     action="store_true", help="jednorazowy cykl")
    parser.add_argument("--daemon",   action="store_true", help="tryb ciągły")
    parser.add_argument("--status",   action="store_true", help="status i ostatnie wyniki")
    parser.add_argument("--queue",    action="store_true", help="pokaż kolejkę plików")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    parser.add_argument("--batch",    type=int, default=5, help="pliki per cykl")
    args = parser.parse_args()

    if args.status:
        init_db()
        summary = get_queue_summary()
        st = json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {}
        print(json.dumps({"status": st, "queue": summary}, ensure_ascii=False, indent=2))
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
