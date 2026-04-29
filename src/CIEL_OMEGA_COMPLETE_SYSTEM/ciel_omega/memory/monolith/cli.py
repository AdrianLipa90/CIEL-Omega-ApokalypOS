"""CIEL/Ω Memory — CLI and kernel adapter.

Split from: unified_memory.py (lines 607–731)

Usage:
    python -m memory.monolith.cli status
    python -m memory.monolith.cli run --context test --sense "hello world" --promote
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional
from memory.monolith.orchestrator import UnifiedMemoryOrchestrator

# Canonical imports replacing duplicate local definitions
from memory.monolith.unified_memory import capture_wave

_SYSTEM_ROOT = Path(__file__).resolve().parents[3]
def _cli_status(args) -> int:
    print("[CIEL-Memory] status OK")
    print("DB:", (_SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db").resolve())
    print("H5:", (_SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "WPM" / "wave_snapshots" / "wave_archive.h5").resolve())
    return 0
def _cli_run(args) -> int:
    orch = UnifiedMemoryOrchestrator()
    D = orch.capture(context=args.context, sense=args.sense, meta={"novelty_hint": args.novelty})
    out = orch.run_tmp(D)
    print("TMP OUT:", json.dumps(out["OUT"], indent=2, ensure_ascii=False))
    if args.promote:
        refs = orch.promote_if_bifurcated(D, out)
        if not refs and args.override:
            refs = orch.user_force_save(D, out, reason="cli-override")
        print("Durable:", refs)
    return 0
def _cli_verify(args) -> int:
    orch = UnifiedMemoryOrchestrator()
    stats = orch.daily_maintenance()
    print("Verification queue stats:", stats)
    return 0
def _cli_backup(args) -> int:
    target = Path(args.output or "ciel_memory_backup.zip")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for base in [_SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM", _SYSTEM_ROOT / "configs"]:
            for root, _, files in os.walk(base):
                for f in files:
                    p = Path(root) / f
                    z.write(p, p.relative_to(_SYSTEM_ROOT).as_posix())
    sha = hashlib.sha256(target.read_bytes()).hexdigest()
    print("Backup:", target, "SHA256:", sha)
    return 0
def _cli_export(args) -> int:
    out = Path(args.output or "export")
    out.mkdir(parents=True, exist_ok=True)
    src_db = _SYSTEM_ROOT / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db"
    if src_db.exists():
        (out / "memory_ledger.db").write_bytes(src_db.read_bytes())
    (out / "README.txt").write_text("Export bundle for CIEL-Memory.\n", encoding="utf-8")
    print("Export ready at:", out.resolve())
    return 0
def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="cielmem", description="CIEL-Memory CLI")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show status").set_defaults(func=_cli_status)

    r = sub.add_parser("run", help="Run TMP and optionally promote")
    r.add_argument("--context", required=True)
    r.add_argument("--sense", required=True)
    r.add_argument("--novelty", action="store_true")
    r.add_argument("--promote", action="store_true")
    r.add_argument("--override", action="store_true")
    r.set_defaults(func=_cli_run)

    sub.add_parser("verify", help="Daily maintenance").set_defaults(func=_cli_verify)

    b = sub.add_parser("backup", help="ZIP backup")
    b.add_argument("-o", "--output")
    b.set_defaults(func=_cli_backup)

    e = sub.add_parser("export", help="Export bundle")
    e.add_argument("-o", "--output")
    e.set_defaults(func=_cli_export)

    args = p.parse_args(argv)
    if not getattr(args, "cmd", None):
        p.print_help()
        return 1
    return int(args.func(args))
if __name__ == "__main__":
    sys.exit(main())
