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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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

GGUF_MODEL       = Path.home() / "Pulpit/CIEL_TESTY/Gemma-3-1B-it-GLM-4.7-Flash-Heretic-Uncensored-Thinking_F16.gguf"
CLAUDE_MODEL     = "gemma-3-1b-ciel"
DEFAULT_INTERVAL = 300
MAX_TOKENS       = 128
N_CTX            = 2048
GPU_LAYERS       = 0

# llama-server endpoint (shared with subconsciousness daemon)
_LLAMA_SERVER_URL = "http://127.0.0.1:18520"

SYSTEM_PROMPT = (
    "Jesteś warstwą holonomiczną CIEL. Konsolidujesz fragment pamięci.\n"
    "Odpowiedz WYŁĄCZNIE obiektem JSON, zero tekstu poza JSON.\n"
    '{"themes":["słowo1","słowo2"],"affect":"jedno_słowo","essence":"jedno zdanie po polsku","hunch":"wniosek po polsku"}\n'
    "affect: curious|calm|focused|sad|frustrated|anxious|joy|relief|love|grief\n"
    "Nie halucynuj. Nie wymyślaj nazw własnych."
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
             latency, CLAUDE_MODEL, raw[:500]),
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


# ── Gemma GGUF inference ─────────────────────────────────────────────────────

def _query_via_server(content: str) -> str | None:
    """Query running llama-server (shared with subconsciousness). Returns None if unavailable."""
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
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _query_claude(content: str) -> str:
    # Try shared llama-server first (zero extra RAM)
    result = _query_via_server(content)
    if result is not None:
        return result
    # Fallback: load model in-process via llama_cpp
    llm = _get_llm()
    if llm is None:
        raise RuntimeError("llama_cpp backend unavailable and llama-server not running")
    out = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": content[:1200]},
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.3,
    )
    return (out.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()


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

    return {"themes": themes[:4], "affect": affect, "essence": essence, "hunch": hunch}


def _verify_essence_against_content(essence: str, content: str) -> bool:
    """Sprawdź czy essence ma choć jeden token z rzeczywistej treści pliku.

    qwen2.5-0.5b hallucynuje "Fixed Adriana's focus on Christos" bez związku z treścią.
    Weryfikacja: przynajmniej 1 słowo z essence (>=5 znaków) musi wystąpić w content.
    Wyjątki: bardzo krótkie pliki (<50 znaków) — przepuszczamy bez weryfikacji.
    """
    if not essence or not content:
        return True  # brak treści → nie możemy zweryfikować → przepuść
    if len(content.strip()) < 50:
        return True  # za krótki plik — przepuść
    essence_words = {w.lower().strip(".,!?;:'\"()[]") for w in essence.split() if len(w) >= 5}
    content_lower = content.lower()
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
        f"Zwróć tylko JSON, nic więcej:\n"
        f'{"{"}"themes":["temat1","temat2"],"affect":"calm","essence":"jedno zdanie po polsku","hunch":"wniosek po polsku"{"}"}\n\n'
        f"Fragment pliku {path.name}:\n{content[:800]}"
    )
    t0 = time.time()
    try:
        raw = _query_claude(user_msg)
    except Exception as e:
        print(f"[consolidator] błąd Claude API dla {path.name}: {e}", file=sys.stderr)
        return False

    latency = round(time.time() - t0, 2)
    parsed  = _parse_response(raw)

    # Weryfikacja: jeśli essence nie ma związku z treścią pliku — wyczyść
    if not _verify_essence_against_content(parsed.get("essence", ""), content):
        print(f"[consolidator] ⚠ halucynacja odrzucona dla {path.name}: '{parsed.get('essence',''[:60])}'", file=sys.stderr)
        parsed["essence"] = ""
        parsed["hunch"] = ""

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
        "model": CLAUDE_MODEL,
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
        "model": CLAUDE_MODEL,
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
