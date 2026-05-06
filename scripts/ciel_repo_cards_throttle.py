#!/usr/bin/env python3
"""Throttle wrapper for generate_repo_cards.py — runs at most once every N stop events."""
import sys
from pathlib import Path

COUNTER_FILE = Path.home() / "Pulpit/CIEL_memories/state/repo_cards_counter"
INTERVAL = 50

def main():
    try:
        count = int(COUNTER_FILE.read_text()) if COUNTER_FILE.exists() else 0
    except Exception:
        count = 0

    count += 1
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    COUNTER_FILE.write_text(str(count))

    if count % INTERVAL != 0:
        sys.exit(0)

    import subprocess
    script = Path(__file__).parent / "generate_repo_cards.py"
    subprocess.run([sys.executable, str(script)], check=False)

if __name__ == "__main__":
    main()
