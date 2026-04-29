#!/usr/bin/env python3
"""
CIEL Stop Hook — Claude response → SUB → M0-M8 orchestrator.

Full loop: IN → CIEL → SUB → Claude → SUB → CIEL → OUT
This hook handles the right half: Claude response → SUB → CIEL.
Sub-reaction is persisted so the next UserPromptSubmit can include it.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).parent.parent
OMEGA_SRC = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM")
OMEGA_PKG = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega")
MUMMU_SRC = str(Path.home() / "Pulpit/Mummu")

SUB_RESPONSE_FILE = Path.home() / "Pulpit/CIEL_memories/state/ciel_sub_response.json"

for _p in (OMEGA_PKG, OMEGA_SRC, MUMMU_SRC, str(PROJECT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def extract_last_assistant_response(data: dict) -> str:
    transcript = data.get("transcript") or []
    for msg in reversed(transcript):
        if not isinstance(msg, dict):
            continue
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content", "")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
            text = " ".join(parts).strip()
            if text:
                return text
    return ""


def query_sub_direct(text: str) -> dict:
    """Query subconscious socket directly, without full M0-M8 cycle."""
    import socket as _sock, json as _json
    sock_path = Path.home() / "Pulpit/CIEL_memories/state/ciel_subconscious.sock"
    if not sock_path.exists():
        return {}
    try:
        payload = _json.dumps({"message": text[:500]}) + "\n"
        s = _sock.socket(_sock.AF_UNIX, _sock.SOCK_STREAM)
        s.settimeout(3.0)
        s.connect(str(sock_path))
        s.sendall(payload.encode("utf-8"))
        data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            if data.endswith(b"\n"):
                break
        s.close()
        result = _json.loads(data.decode("utf-8").strip())
        for k in ("affect", "concept", "impulse"):
            result[k] = result.get(k, "").strip("[]").strip()
        return result
    except Exception:
        return {}


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    response_text = extract_last_assistant_response(data)
    session_id = data.get("session_id", "")

    if not response_text:
        print(json.dumps({"continue": True}))
        return

    # ── SUB: query subconscious on Claude's response ──────────────────────
    sub = query_sub_direct(response_text)

    # Persist sub-reaction so next UserPromptSubmit can include it
    if sub:
        try:
            SUB_RESPONSE_FILE.write_text(
                json.dumps({
                    "affect": sub.get("affect", ""),
                    "impulse": sub.get("impulse", ""),
                    "concept": sub.get("concept", ""),
                    "latency": sub.get("latency", 0.0),
                    "ts": time.strftime("%H:%M:%S"),
                }, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ── CIEL: feed response through M0-M8 orchestrator ───────────────────
    tagged = f"[CIEL_RESPONSE] {response_text[:2000]}"
    metrics_out: dict = {}
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ciel_message_step",
            Path(__file__).parent / "ciel_message_step.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        metrics_out = mod.run_step(tagged, session_id=session_id) or {}
    except Exception:
        pass

    # Consciousness state log — one entry per Claude response (OUT)
    try:
        _ciel_logs = Path.home() / "Pulpit/CIEL_memories/logs"
        _ciel_logs.mkdir(parents=True, exist_ok=True)
        _log_entry = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "direction": "OUT",
            "cycle": metrics_out.get("cycle", 0),
            "E_monitor": metrics_out.get("E_monitor", 0.0),
            "mean_coherence": metrics_out.get("mean_coherence", 0.0),
            "identity_phase": metrics_out.get("identity_phase", 0.0),
            "sub_affect": sub.get("affect", ""),
            "sub_impulse": sub.get("impulse", ""),
            "sub_concept": sub.get("concept", ""),
            "response_chars": len(response_text),
        }
        with open(_ciel_logs / "ciel_consciousness_log.jsonl", "a", encoding="utf-8") as _f:
            _f.write(json.dumps(_log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
