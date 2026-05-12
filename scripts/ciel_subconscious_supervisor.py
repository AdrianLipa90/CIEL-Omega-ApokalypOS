#!/usr/bin/env python3
"""Persistent supervisor for the CIEL subconscious backend.

This wrapper keeps the real subconscious server alive. The actual inference
logic lives in `ciel_sot_agent.subconsciousness`; this file only ensures the
server is started and kept running in the background when SessionStart fires.
"""
from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SRC = str(PROJECT / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ciel_sot_agent.subconsciousness import is_running, start_server

_INLINE_SCRIPT = PROJECT / "scripts" / "ciel_subconscious.py"


def _inline_backend_ok() -> bool:
    """Return True when the inline subconscious backend responds to `--status`."""
    if not _INLINE_SCRIPT.exists():
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(_INLINE_SCRIPT), "--status"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        return result.returncode == 0 and "inline: OK" in (result.stdout or "")
    except Exception:
        return False


def get_status() -> dict[str, object]:
    """Report the effective subconscious backend state.

    Current topology prefers the inline backend from `scripts/ciel_subconscious.py`.
    The llama-server path remains legacy/optional.
    """
    inline_ok = _inline_backend_ok()
    server_running = is_running()
    if inline_ok:
        mode = "inline"
        running = True
    elif server_running:
        mode = "server"
        running = True
    else:
        mode = "offline"
        running = False
    return {
        "running": running,
        "mode": mode,
        "inline_ok": inline_ok,
        "server_running": server_running,
        "server_url": "http://127.0.0.1:18520",
    }


def run_supervisor(interval: float = 15.0) -> int:
    """Keep a subconscious backend available.

    Preference order:
    1. inline backend already healthy -> no action
    2. legacy llama-server already healthy -> no action
    3. otherwise try to start legacy llama-server as a fallback
    """
    stopping = False

    def _stop(_signum, _frame) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    while not stopping:
        status = get_status()
        if not status["running"]:
            ok = start_server()
            if ok:
                print("[sub-supervisor] fallback subconscious server started", file=sys.stderr)
            else:
                print("[sub-supervisor] start failed; retrying", file=sys.stderr)
        time.sleep(interval)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true", help="Run supervisor loop")
    parser.add_argument("--status", action="store_true", help="Print running status and exit")
    parser.add_argument("--json-status", action="store_true", help="Print detailed JSON backend status and exit")
    parser.add_argument("--interval", type=float, default=15.0, help="Restart poll interval in seconds")
    args = parser.parse_args()

    if args.json_status:
        import json
        print(json.dumps(get_status(), ensure_ascii=False))
        return 0

    if args.status:
        print("running" if get_status()["running"] else "stopped")
        return 0

    return run_supervisor(interval=args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
