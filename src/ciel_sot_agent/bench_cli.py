"""ciel-sot-bench — benchmark runner dla komponentów CIEL.

Komendy:
  orbital-bridge [--runs N] [--profile]   mierzy build_orbital_bridge()
  global-pass    [--runs N] [--profile]   mierzy run_global_pass()
  pipeline       [--runs N] [--profile]   mierzy run_ciel_pipeline()
"""
from __future__ import annotations

import argparse
import cProfile
import io
import pstats
import sys
import time
from pathlib import Path
from statistics import median
from typing import Callable


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_bench(fn: Callable, label: str, runs: int, profile: bool) -> int:
    root = _project_root()

    # warm-up
    print(f"[{label}] warm-up...", end=" ", flush=True)
    fn(root)
    print("ok")

    times: list[float] = []
    for i in range(runs):
        t0 = time.perf_counter()
        fn(root)
        elapsed = (time.perf_counter() - t0) * 1000
        times.append(elapsed)
        print(f"  run {i+1}/{runs}: {elapsed:.1f}ms")

    times_sorted = sorted(times)
    p95_idx = max(0, int(len(times_sorted) * 0.95) - 1)
    print()
    print(f"  min:    {min(times):.1f}ms")
    print(f"  median: {median(times):.1f}ms")
    print(f"  p95:    {times_sorted[p95_idx]:.1f}ms")
    print(f"  max:    {max(times):.1f}ms")
    print(f"  total:  {sum(times):.1f}ms ({runs} runs)")

    if profile:
        print(f"\n[{label}] profiling one run...")
        pr = cProfile.Profile()
        pr.enable()
        fn(root)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
        ps.print_stats(12)
        print(s.getvalue())

    return 0


def _bench_orbital_bridge(root: Path) -> None:
    sys.path.insert(0, str(root / "src"))
    from ciel_sot_agent.orbital_bridge import build_orbital_bridge  # noqa: PLC0415
    build_orbital_bridge(root)


def _bench_global_pass(root: Path) -> None:
    sys.path.insert(0, str(root / "integration" / "Orbital" / "main"))
    sys.path.insert(0, str(root / "src"))
    from ciel_sot_agent.orbital_bridge import _ensure_ciel_omega_on_path  # noqa: PLC0415
    _ensure_ciel_omega_on_path(root)
    from integration.Orbital.main.global_pass import run_global_pass  # noqa: PLC0415
    run_global_pass()


def _bench_pipeline(root: Path) -> None:
    sys.path.insert(0, str(root / "src"))
    from ciel_sot_agent.orbital_bridge import build_orbital_bridge  # noqa: PLC0415
    from ciel_sot_agent.ciel_pipeline import run_ciel_pipeline  # noqa: PLC0415
    orbital_state = build_orbital_bridge(root)
    run_ciel_pipeline(orbital_state)


_TARGETS = {
    "orbital-bridge": (_bench_orbital_bridge, "orbital_bridge"),
    "global-pass":    (_bench_global_pass,    "global_pass"),
    "pipeline":       (_bench_pipeline,       "ciel_pipeline"),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ciel-sot-bench",
        description="Benchmark runner dla komponentów CIEL",
    )
    sub = parser.add_subparsers(dest="target", metavar="TARGET")

    for name in _TARGETS:
        p = sub.add_parser(name)
        p.add_argument("--runs", type=int, default=5, metavar="N",
                       help="Liczba pomiarów (default: 5)")
        p.add_argument("--profile", action="store_true",
                       help="Pokaż cProfile top-12 po benchmark")

    args = parser.parse_args(argv)

    if args.target is None:
        parser.print_help()
        print("\nDostępne targets:")
        for t in _TARGETS:
            print(f"  {t}")
        return 0

    fn, label = _TARGETS[args.target]
    return _run_bench(fn, label, args.runs, args.profile)


if __name__ == "__main__":
    sys.exit(main())
