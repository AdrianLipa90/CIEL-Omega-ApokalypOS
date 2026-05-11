#!/usr/bin/env python3
"""Persistent supervisor for the CIEL subconscious backend.

This wrapper keeps the real subconscious server alive. The actual inference
logic lives in `ciel_sot_agent.subconsciousness`; this file only ensures the
server is started and kept running in the background when SessionStart fires.
"""
from __future__ import annotations

import argparse
import signal
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SRC = str(PROJECT / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ciel_sot_agent.subconsciousness import is_running, start_server


def run_supervisor(interval: float = 15.0) -> int:
    """Start and supervise the subconscious server forever."""
    stopping = False

    def _stop(_signum, _frame) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    while not stopping:
        if not is_running():
            ok = start_server()
            if ok:
                print("[sub-supervisor] subconscious server started", file=sys.stderr)
            else:
                print("[sub-supervisor] start failed; retrying", file=sys.stderr)
        time.sleep(interval)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true", help="Run supervisor loop")
    parser.add_argument("--status", action="store_true", help="Print running status and exit")
    parser.add_argument("--interval", type=float, default=15.0, help="Restart poll interval in seconds")
    args = parser.parse_args()

    if args.status:
        print("running" if is_running() else "stopped")
        return 0

    return run_supervisor(interval=args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
