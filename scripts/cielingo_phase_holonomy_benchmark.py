#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from ciel_sot_agent.phase_holonomy_benchmark import load_cases, run_phase_holonomy_benchmark


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a CIELingo phase-holonomy Monte Carlo benchmark.")
    parser.add_argument("--cases", type=Path, default=None, help="Optional JSON file with case studies.")
    parser.add_argument("--n", type=int, default=64, help="Monte Carlo trials per case.")
    parser.add_argument("--strength", type=float, default=0.12, help="Perturbation strength.")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed.")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path.")
    args = parser.parse_args()

    report = run_phase_holonomy_benchmark(
        load_cases(str(args.cases) if args.cases is not None else None),
        n_trials=args.n,
        strength=args.strength,
        seed=args.seed,
    )
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
