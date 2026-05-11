"""Inject memory clusters into SessionStart context.

Reads last handoff topics → queries memory_rag → injects relevant memories
as additionalContext block. Designed to run as a SessionStart hook.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_HANDOFF = Path.home() / "Pulpit" / "CIEL_memories" / "handoff.md"
_HUNCHES = Path.home() / "Pulpit" / "CIEL_memories" / "hunches.md"

sys.path.insert(0, str(_ROOT / "src"))


def _extract_handoff_query(n_lines: int = 40) -> str:
    if not _HANDOFF.exists():
        return ""
    lines = _HANDOFF.read_text(encoding="utf-8", errors="replace").splitlines()
    # Take last n_lines, strip bullet markers
    chunk = "\n".join(lines[-n_lines:])
    chunk = re.sub(r"^\s*[-•*]\s*", "", chunk, flags=re.MULTILINE)
    return chunk


def _extract_hunches_query(n_chars: int = 800) -> str:
    if not _HUNCHES.exists():
        return ""
    text = _HUNCHES.read_text(encoding="utf-8", errors="replace")
    return text[-n_chars:]


def main() -> None:
    from ciel_sot_agent.memory_rag import build_memory_context

    handoff_q = _extract_handoff_query()
    hunches_q = _extract_hunches_query()
    query = (handoff_q + "\n" + hunches_q).strip()

    if not query:
        sys.exit(0)

    ctx = build_memory_context(query, _ROOT, max_tokens_estimate=500)
    if not ctx:
        sys.exit(0)

    block = "=== KLASTRY PAMIĘCI (RAG) ===\n" + ctx

    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": block,
        }
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
