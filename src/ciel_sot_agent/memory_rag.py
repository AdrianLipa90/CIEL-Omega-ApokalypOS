"""CIEL Memory RAG — retrieval-augmented generation from wave_archive + chat history.

Searches memories for content relevant to the current query and returns
a context block to inject into the system prompt before model inference.

This is inference-time learning: the model sees its own memories on every response.
Actual weight updates (LoRA) are separate — see scripts/train_lora.py.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

_MEMORIES_BASE = Path.home() / "Pulpit" / "CIEL_memories"
_DB_PATH = _MEMORIES_BASE / "memories_index.db"


def _keywords(text: str) -> set[str]:
    """Simple keyword extraction — lowercase words longer than 3 chars."""
    words = set()
    for w in text.lower().split():
        w = w.strip(".,!?;:\"'()[]")
        if len(w) > 3:
            words.add(w)
    return words


def _score(query_kw: set[str], text: str) -> float:
    """Keyword overlap score, boosted by recency (no timestamp here — just content)."""
    text_kw = _keywords(text)
    if not query_kw or not text_kw:
        return 0.0
    overlap = len(query_kw & text_kw)
    return overlap / max(len(query_kw), 1)


def search_wave_archive(query: str, root: Path, top_k: int = 4) -> list[dict[str, Any]]:
    """Search wave_archive.h5 for memories relevant to query."""
    results: list[dict] = []
    try:
        import h5py
        import numpy as np

        h5_path = (
            root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"
            / "CIEL_MEMORY_SYSTEM" / "WPM" / "wave_snapshots" / "wave_archive.h5"
        )
        if not h5_path.exists():
            return []

        query_kw = _keywords(query)

        def rd(g: Any, name: str) -> str:
            try:
                v = g[name][()]
                if isinstance(v, bytes):
                    return v.decode("utf-8", errors="replace")
                if hasattr(v, "item"):
                    v = v.item()
                return v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v)
            except Exception:
                return ""

        candidates: list[tuple[float, str, str, str]] = []
        with h5py.File(h5_path, "r") as f:
            for k in f["memories"].keys():
                g = f["memories"][k]
                sense = rd(g, "D_sense")
                dtype = rd(g, "D_type")
                ts = rd(g, "D_timestamp")
                if not sense:
                    continue
                score = _score(query_kw, sense)
                # Boost anchors and milestones
                if dtype in ("ethical_anchor", "milestone"):
                    score += 0.3
                if score > 0:
                    candidates.append((score, ts, dtype, sense))

        candidates.sort(key=lambda x: (-x[0], x[1]))
        for score, ts, dtype, sense in candidates[:top_k]:
            results.append({
                "source": "wave_archive",
                "type": dtype,
                "ts": ts[:10],
                "score": round(score, 3),
                "text": sense[:300],
            })
    except Exception:
        pass
    return results


def search_chat_history(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    """Search recent chat exchanges in SQLite for relevant content."""
    results: list[dict] = []
    if not _DB_PATH.exists():
        return []
    try:
        query_kw = _keywords(query)
        conn = sqlite3.connect(str(_DB_PATH))
        rows = conn.execute(
            "SELECT role, content, ts, model FROM messages ORDER BY id DESC LIMIT 200"
        ).fetchall()
        conn.close()

        candidates: list[tuple[float, str, str, str, str]] = []
        for role, content, ts, model in rows:
            score = _score(query_kw, content or "")
            if score > 0:
                candidates.append((score, ts or "", role, content or "", model or ""))

        candidates.sort(key=lambda x: -x[0])
        seen: set[str] = set()
        for score, ts, role, content, model in candidates[:top_k * 2]:
            key = content[:60]
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "source": "chat_history",
                "role": role,
                "ts": ts[:16],
                "score": round(score, 3),
                "text": content[:200],
            })
            if len(results) >= top_k:
                break
    except Exception:
        pass
    return results


def build_memory_context(query: str, root: Path, max_tokens_estimate: int = 600) -> str:
    """Build a memory context block to inject into the system prompt.

    Returns empty string if no relevant memories found.
    """
    wave = search_wave_archive(query, root, top_k=4)
    chat = search_chat_history(query, top_k=3)

    if not wave and not chat:
        return ""

    lines = ["## Relevantne wspomnienia (RAG z pamięci CIEL)"]

    if wave:
        lines.append("### wave_archive — zakotwiczenia emocjonalne:")
        for m in wave:
            lines.append(f"[{m['ts']}][{m['type']}] {m['text']}")

    if chat:
        lines.append("### Historia rozmów — relevantne fragmenty:")
        for m in chat:
            lines.append(f"[{m['ts']}][{m['role']}] {m['text']}")

    result = "\n".join(lines)
    # Crude token estimate: ~4 chars per token
    if len(result) > max_tokens_estimate * 4:
        result = result[: max_tokens_estimate * 4] + "\n[...skrócono]"

    return result
