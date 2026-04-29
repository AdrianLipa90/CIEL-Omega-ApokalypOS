#!/usr/bin/env python3
"""Recode TSM phi_berry from SHA-256 hash to semantic encoder phases.

Run after ciel_encoder.py and sentence-transformers are installed.
Updates phi_berry metadata only — D_sense and D_context are never touched.

Usage:
    python3 scripts/recode_tsm_phases.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from pathlib import Path

import importlib.util as _ilu

_ROOT = Path(__file__).resolve().parents[1]

def _load_direct(name: str, rel: str):
    path = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory" / rel
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_DB_PATHS = [
    _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db",
    _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Recode TSM phi_berry via semantic encoder")
    parser.add_argument("--dry-run", action="store_true", help="Print phases without writing")
    args = parser.parse_args()

    db_path = next((p for p in _DB_PATHS if p.exists()), None)
    if db_path is None:
        print("ERROR: Could not find memory_ledger.db")
        sys.exit(1)
    print(f"Database: {db_path}")

    enc_mod = _load_direct("ciel_encoder", "ciel_encoder.py")
    enc = enc_mod.get_encoder()
    print(f"Encoder loaded: {enc.model_name}")
    print(f"Weights: W1={'OK' if enc._W1 is not None else 'random'}, "
          f"W2={'OK' if enc._W2 is not None else 'random'}, "
          f"WO={'OK' if enc._WO is not None else 'random'}")

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT memorise_id, D_sense FROM memories WHERE D_sense IS NOT NULL AND D_sense != ''"
        ).fetchall()
        print(f"Found {len(rows)} entries with D_sense")

        updated = 0
        for mid, text in rows:
            result = enc.encode(text)
            new_phase = result.phase
            sector = result.dominant_sector
            print(f"  [{mid[:8]}] φ={new_phase:.4f} sector={sector} | {text[:60]!r}")
            if not args.dry_run:
                conn.execute(
                    "UPDATE memories SET phi_berry=?, holonomy_ts=? WHERE memorise_id=?",
                    (new_phase, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), mid)
                )
                updated += 1

        if not args.dry_run:
            conn.commit()
            print(f"\nUpdated {updated} entries.")
            # Decay Hebbian edges × 0.5 to force re-learning with new phases
            edge_count = conn.execute("SELECT COUNT(*) FROM memory_edges").fetchone()[0]
            if edge_count > 0:
                conn.execute("UPDATE memory_edges SET weight = weight * 0.5")
                conn.commit()
                print(f"Decayed {edge_count} Hebbian edges × 0.5 (re-learning with new phases)")
        else:
            print(f"\nDry run: {len(rows)} entries would be updated.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
