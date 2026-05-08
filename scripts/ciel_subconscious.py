#!/usr/bin/env python3
"""
CIEL Subconscious — warstwa intuicji i afektu CIEL.

Architektura: persistent daemon z socketem Unix.
Model GGUF jest ładowany raz i trzymany w pamięci.
Hook odpytuje daemon przez socket — bez zimnego startu, latencja < 2s.

Tryby:
  python3 ciel_subconscious.py --daemon     # uruchom serwer (zostaje w tle)
  python3 ciel_subconscious.py "wiadomość"  # zapytaj daemon lub uruchom inline
  python3 ciel_subconscious.py --status     # sprawdź czy daemon działa
"""
from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT = Path(__file__).parent.parent
OMEGA_SRC = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM")
OMEGA_PKG = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega")

for _p in (OMEGA_PKG, OMEGA_SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SUBCONSCIOUS_MODEL = Path("/home/adrian/Pulpit/CIEL_TESTY/Gemma-3-1B-it-GLM-4.7-Flash-Heretic-Uncensored-Thinking_F16.gguf")
SOCKET_PATH = Path.home() / "Pulpit/CIEL_memories/state/ciel_subconscious.sock"
SUB_LOG     = Path.home() / "Pulpit/CIEL_memories/logs/ciel_sub_log.jsonl"
SUB_LOG_MAX = 20
GPU_LAYERS = 0
N_CTX = 2048
MAX_TOKENS = 120
STOP_SEQUENCES = ["\n\n\n", "---"]

_CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"
_CLAUDE_INJECT = _CLAUDE_MD.read_text(encoding="utf-8") if _CLAUDE_MD.exists() else ""

SYSTEM_PROMPT_BASE = (
    _CLAUDE_INJECT
    + "\n\n---\n\n"
    "Reply with EXACTLY this format — three lines, nothing else:\n"
    "AFFECT: <one word from: joy curious calm focused sad afraid frustrated anxious love relief angry compassion neutral>\n"
    "CONCEPT: <one or two key words from the message>\n"
    "IMPULSE: <one short sentence, 3-10 words, describing the core drive or tension>\n"
    "compassion = allocentric sadness + care directed toward another.\n"
    "No explanation. No extra lines. Exactly three lines.\n"
    "Example input: system keeps breaking\n"
    "Example output:\n"
    "AFFECT: frustrated\n"
    "CONCEPT: system breaking\n"
    "IMPULSE: repeated failure erodes confidence in the build"
)

# ── GGUF backend (lazy-loaded, singleton) ─────────────────────────────────────
_GGUF_LLM: Any = None

def _get_llm() -> Any:
    global _GGUF_LLM
    if _GGUF_LLM is not None:
        return _GGUF_LLM
    try:
        from llama_cpp import Llama  # type: ignore
        _GGUF_LLM = Llama(
            model_path=str(SUBCONSCIOUS_MODEL),
            n_ctx=N_CTX,
            n_gpu_layers=GPU_LAYERS,
            n_threads=4,
            verbose=False,
        )
    except Exception as e:
        print(f"[sub] llama_cpp load failed: {e}", file=sys.stderr)
        _GGUF_LLM = None
    return _GGUF_LLM

# ── orbital context builder ───────────────────────────────────────────────────

def build_orbital_prompt(orch: Any) -> tuple[str, float]:
    """Derive temperature from orbital coherence. System prompt stays minimal to prevent echo."""
    try:
        snap = orch.snapshot()
        defects = snap.defects
        mean_coherence = defects.get("mean_coherence", 0.5)
        temperature = round(0.65 - 0.35 * mean_coherence, 3)
        return SYSTEM_PROMPT_BASE, temperature
    except Exception:
        return SYSTEM_PROMPT_BASE, 0.45


def _user_template(message: str) -> str:
    return message[:80].strip()


# ── Gemma GGUF inference ──────────────────────────────────────────────────────

def _run_gguf(message: str, system_prompt: str = SYSTEM_PROMPT_BASE) -> Dict[str, Any]:
    t0 = time.time()
    llm = _get_llm()
    if llm is None:
        return _empty(ok=False, note="llama_cpp unavailable")
    try:
        out = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": _user_template(message)},
            ],
            max_tokens=MAX_TOKENS,
            stop=STOP_SEQUENCES,
            temperature=0.45,
        )
        text = (out.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
        parsed = _parse(text)
        parsed["latency"] = round(time.time() - t0, 2)
        parsed["ok"] = bool(parsed["affect"] or parsed["concept"])
        return parsed
    except Exception as e:
        return _empty(ok=False, note=str(e)[:80])


def _run_inline(message: str) -> Dict[str, Any]:
    return _run_gguf(message)


def run_daemon() -> None:
    """Daemon zastąpiony przez bezpośrednie wywołania claude CLI — ta funkcja jest no-op."""
    print("[sub] daemon mode nieaktywny — używam claude CLI inline.", file=sys.stderr)


# ── client ───────────────────────────────────────────────────────────────────

def query_daemon(message: str, timeout: float = 3.0,
                 orch: Any = None) -> Optional[Dict[str, Any]]:
    """Socket daemon zastąpiony przez claude CLI — zawsze zwraca None, process() używa CLI."""
    return None


def process(message: str) -> Dict[str, Any]:
    """Główny punkt wejścia — claude CLI."""
    return _run_inline(message)


def retrieve_context_links(message: str, orch: Any, top_k: int = 4) -> list:
    """Skanuj M3 i zwróć powiązane wspomnienia semantyczne jako hyperlinki kontekstu."""
    links = []
    try:
        results = orch.m3.retrieve(message, top_k=top_k)
        for r in results:
            item = r.get("item") if isinstance(r, dict) else r
            if item is None:
                continue
            score = r.get("score", 0.0) if isinstance(r, dict) else 0.0
            links.append({
                "key": str(getattr(item, "semantic_key", ""))[:60],
                "text": str(getattr(item, "canonical_text", ""))[:100],
                "conf": round(float(getattr(item, "confidence", 0.0)), 3),
                "alignment": round(float(getattr(item, "identity_alignment", 0.0)), 3),
                "score": round(float(score), 3),
            })
    except Exception:
        pass
    return links


def write_sub_log(entry: Dict[str, Any]) -> None:
    """Append entry to rolling log. Trims to SUB_LOG_MAX lines."""
    try:
        line = json.dumps(entry, ensure_ascii=False)
        existing = []
        if SUB_LOG.exists():
            existing = SUB_LOG.read_text(encoding="utf-8").splitlines()
        existing.append(line)
        SUB_LOG.write_text(
            "\n".join(existing[-SUB_LOG_MAX:]) + "\n",
            encoding="utf-8"
        )
    except Exception:
        pass


def read_sub_log(n: int = 5) -> list:
    """Read last n entries from sub log."""
    try:
        if not SUB_LOG.exists():
            return []
        lines = [l for l in SUB_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
        return [json.loads(l) for l in lines[-n:]]
    except Exception:
        return []


def inject_into_orchestrator(orch: Any, sub: Dict[str, Any]) -> None:
    """Wstrzyknij wynik podświadomości do M5 i M3; dołącz memory links; zapisz do logu."""
    try:
        ts = time.time()
        if sub.get("ok"):
            if sub.get("affect"):
                orch.m5.store(sub["affect"], metadata={
                    "timestamp": ts, "phase": orch.m5.state.phase,
                    "salience": 0.80, "identity_impact": 0.60,
                    "source": "subconscious",
                })
            if sub.get("concept"):
                orch.m3.store(sub["concept"], metadata={
                    "timestamp": ts, "phase": orch.m3.state.phase,
                    "salience": 0.75, "identity_impact": 0.55,
                    "source": "subconscious",
                })
        # Memory hyperlinks — zawsze skanuj M3 dla bieżącej wiadomości
        msg = sub.get("_message", "")
        if msg:
            links = retrieve_context_links(msg, orch, top_k=4)
            sub["memory_links"] = links
        write_sub_log({
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "affect": sub.get("affect", ""),
            "concept": sub.get("concept", ""),
            "impulse": sub.get("impulse", ""),
            "memory_links": sub.get("memory_links", []),
            "latency": sub.get("latency", 0.0),
        })
    except Exception:
        pass


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_text(out: Any) -> str:
    choices = out.get("choices") or []
    if choices:
        return str(choices[0].get("message", {}).get("content", "")).strip()
    return ""


_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "be", "to", "of", "and", "in", "it",
    "this", "that", "for", "on", "with", "as", "by", "at", "from", "or", "but",
    "not", "have", "has", "had", "will", "can", "may", "here", "there", "which",
    "involves", "related", "likely", "about", "into", "these",
    "keep", "make", "take", "give", "come", "look", "need", "want", "feel", "work",
    "system", "state", "message", "input", "output", "value", "above", "below",
}

_EMOTION_WORDS = {
    "joy", "joyful", "fear", "afraid", "sad", "sadness", "calm", "focused", "focus", "relief",
    "excited", "excitement", "frustration", "frustrated", "anxious", "anxiety",
    "love", "hope", "hopeful", "wonder", "curiosity", "curious", "anger", "angry",
    "content", "happy", "worried", "concern", "trust", "anticipation", "surprise",
    "disgust", "bored", "boredom", "alert", "tension", "tense", "relief",
    "confusion", "confused", "clarity", "clear", "neutral", "positive", "negative",
    "determined", "uncertain", "engaged", "disengaged", "flow", "stuck", "open",
    "compassion", "compassionate",
}

# Maps parser line-key → result dict key; "emotion" is alias for affect
_KEY_ALIASES: dict[str, str] = {
    "affect": "affect", "emotion": "affect",
    "concept": "concept", "impulse": "impulse",
}


def _clean_val(val: str) -> str:
    return val.strip("[]()").strip()


def _parse(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {"affect": "", "concept": "", "impulse": "", "raw": text}
    for line in text.strip().splitlines():
        line = line.strip().lstrip("*- ").rstrip("*")
        if line.lower().startswith(("input:", "message:")):
            continue
        low = line.lower()
        for alias, dest in _KEY_ALIASES.items():
            if low.startswith(f"{alias}:") and not result[dest]:
                val = _clean_val(line[len(alias)+1:].strip())
                if dest == "affect" and val:
                    first = val.split()[0].lower()
                    result[dest] = first
                else:
                    result[dest] = val
                break
        if all(result[k] for k in ("affect", "concept", "impulse")):
            break
    # Validate affect — if not a known emotion word, clear it for freeform
    if result["affect"] and result["affect"].lower() not in _EMOTION_WORDS:
        result["affect"] = ""
    # Freeform fallback — when affect missing or concept/impulse empty
    if not result["affect"] or not result["concept"]:
        words = text.lower().split()
        stripped = [w.strip(".,!?;:()[]") for w in words]
        # Try emotion words first for affect
        if not result["affect"]:
            for w in stripped:
                if w in _EMOTION_WORDS:
                    result["affect"] = w
                    break
        # Content words for concept
        if not result["concept"]:
            content = [w for w in stripped
                       if w not in _STOPWORDS and len(w) >= 4 and w not in _EMOTION_WORDS]
            if len(content) >= 2:
                result["concept"] = f"{content[0]} {content[1]}"
            elif content:
                result["concept"] = content[0]
        # Short sentence for impulse
        if not result["impulse"]:
            sentences = text.replace("?", ".").replace("!", ".").split(".")
            for s in sentences:
                s = s.strip()
                if 3 <= len(s.split()) <= 12:
                    result["impulse"] = s
                    break
    return result


def _empty(ok: bool = False, note: str = "") -> Dict[str, Any]:
    return {"affect": "", "concept": "", "impulse": note, "latency": 0.0, "ok": ok, "raw": ""}


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("message", nargs="?", help="wiadomość do przetworzenia")
    parser.add_argument("--daemon", action="store_true", help="uruchom persistent daemon")
    parser.add_argument("--status", action="store_true", help="sprawdź daemon")
    args = parser.parse_args()

    if args.daemon:
        run_daemon()
    elif args.status:
        r = query_daemon("ping", timeout=1.0)
        if r:
            print(f"daemon: OK  (latency {r.get('latency',0):.2f}s)")
        else:
            print("daemon: nie działa")
    else:
        msg = args.message or (sys.stdin.read().strip() if not sys.stdin.isatty() else "test")
        r = process(msg)
        print(json.dumps(r, ensure_ascii=False, indent=2))
