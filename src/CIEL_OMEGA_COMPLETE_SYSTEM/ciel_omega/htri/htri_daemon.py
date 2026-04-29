"""HTRI Daemon — trwały background process na i7-8750H + GTX 1050 Ti.

Działa non-stop, zapisuje metryki do ~/.claude/ciel_state.db co cycle_interval sekund.
Uruchamiany przez systemd lub autostart.

Usage:
    python3 htri_daemon.py          # foreground (do testów)
    python3 htri_daemon.py --daemon # background
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

# Dodaj CIEL na path
_HERE = Path(__file__).resolve().parent
_OMEGA = _HERE.parent
sys.path.insert(0, str(_OMEGA))

from ciel_omega.htri.htri_local import LocalHTRI, OscillatorBank


CYCLE_INTERVAL = 10.0   # sekund między cyklami
STATE_FILE     = Path.home() / ".claude" / "htri_state.json"
PID_FILE       = Path.home() / ".claude" / "htri_daemon.pid"

_running = True


def _handle_signal(signum, frame):
    global _running
    _running = False


def _write_state(result: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Zapisz też do state_db jeśli dostępne
    try:
        from ciel_sot_agent.state_db import get_db
        import time as _t
        conn = get_db()
        comb = result.get("combined", {})
        conn.execute(
            "INSERT INTO metrics_history (timestamp, cycle_index, identity_phase, "
            "ethical_score, system_health, coherence_index, closure_penalty, mood, dominant_emotion) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (_t.time(), result.get("cycle", 0),
             comb.get("soul_invariant", 0.0),
             0.0,
             comb.get("coherence", 0.0),
             comb.get("coherence", 0.0),
             0.0, 0.0, "htri")
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def run_daemon(steps_per_cycle: int = 300) -> None:
    """Main daemon loop."""
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT,  _handle_signal)

    PID_FILE.write_text(str(os.getpid()))
    print(f"[HTRI daemon] PID={os.getpid()} | cycle={CYCLE_INTERVAL}s | steps={steps_per_cycle}")

    htri   = LocalHTRI()
    cycle  = 0

    while _running:
        t0     = time.time()
        result = htri.run(cpu_steps=steps_per_cycle, gpu_steps=steps_per_cycle)
        result["cycle"] = cycle
        result["timestamp"] = t0

        comb = result["combined"]
        print(
            f"[HTRI] cycle={cycle:4d}  "
            f"coh={comb['coherence']:.4f}  "
            f"Σ={comb['soul_invariant']:.4f}  "
            f"osc={comb['total_oscillators']}  "
            f"t={result['elapsed_s']}s"
        )

        _write_state(result)
        cycle += 1

        elapsed = time.time() - t0
        sleep   = max(0.0, CYCLE_INTERVAL - elapsed)
        if sleep > 0:
            time.sleep(sleep)

    PID_FILE.unlink(missing_ok=True)
    print("[HTRI daemon] stopped.")


def read_state() -> dict:
    """Odczytaj aktualny stan HTRI (dla pipeline)."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def is_running() -> bool:
    if not PID_FILE.exists():
        return False
    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTRI background daemon")
    parser.add_argument("--daemon",  action="store_true", help="Run in background")
    parser.add_argument("--status",  action="store_true", help="Show current state")
    parser.add_argument("--stop",    action="store_true", help="Stop daemon")
    parser.add_argument("--steps",   type=int, default=300)
    args = parser.parse_args()

    if args.status:
        if is_running():
            state = read_state()
            print(json.dumps(state.get("combined", {}), indent=2))
        else:
            print("HTRI daemon not running")
        sys.exit(0)

    if args.stop:
        if PID_FILE.exists():
            os.kill(int(PID_FILE.read_text()), signal.SIGTERM)
            print("Stopped")
        sys.exit(0)

    if args.daemon:
        if os.fork() != 0:
            sys.exit(0)
        os.setsid()
        if os.fork() != 0:
            sys.exit(0)
        sys.stdout = open(Path.home() / ".claude" / "htri_daemon.log", "a")
        sys.stderr = sys.stdout

    run_daemon(steps_per_cycle=args.steps)
