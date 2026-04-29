#!/usr/bin/env python3
"""CIEL Code Learner — nauka przez rezonans fazowy.

Parsuje pliki .py na fragmenty (funkcje/klasy/moduły), koduje każdy przez
CIELEncoder → phi_berry, stampuje do TSM jako d_type='code_fragment'.

Retrieval fazowy znajdzie semantycznie zbliżony kod przez holonomię,
nie przez grep. To jest "nauka przez rezonans" zamiast gradient descent.

Usage:
    python3 scripts/ciel_code_learner.py path/to/file.py
    python3 scripts/ciel_code_learner.py --watch src/            # auto na zapis
    python3 scripts/ciel_code_learner.py --query "faza Berry"    # znajdź kod
"""
from __future__ import annotations

import ast
import importlib.util as ilu
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

_ROOT    = Path(__file__).resolve().parents[1]
_MEM_SRC = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory"
_DB      = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"

_MIN_LINES = 4    # ignoruj trywialnie krótkie fragmenty
_MAX_CHARS = 800  # max znaków per wpis TSM


# ── moduły ────────────────────────────────────────────────────────────────────

def _load(name: str, rel: str):
    path = _MEM_SRC / rel
    if name in sys.modules:
        return sys.modules[name]
    spec = ilu.spec_from_file_location(name, path)
    mod  = ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── parsowanie AST ────────────────────────────────────────────────────────────

def _fragments(source: str, filepath: Path) -> Iterator[dict]:
    """Yield code fragments: functions, classes, top-level statements."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Nie Python 3 — zwróć cały plik jako jeden fragment
        yield {"kind": "file", "name": filepath.name, "text": source[:_MAX_CHARS],
               "lineno": 1, "file": str(filepath)}
        return

    lines = source.splitlines()

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        start = node.lineno - 1
        end   = getattr(node, 'end_lineno', start + 10)
        if end - start < _MIN_LINES:
            continue
        snippet = "\n".join(lines[start:end])
        kind    = "class" if isinstance(node, ast.ClassDef) else "function"
        # Docstring jako kontekst semantyczny
        doc = ast.get_docstring(node) or ""
        text = f"# {filepath.name}::{node.name}\n{snippet}"
        if doc:
            text = f"# {node.name}: {doc[:200]}\n{snippet}"
        yield {
            "kind":   kind,
            "name":   node.name,
            "text":   text[:_MAX_CHARS],
            "lineno": node.lineno,
            "file":   str(filepath),
        }


# ── ingest jednego pliku ──────────────────────────────────────────────────────

def ingest_file(path: Path, *, dry_run: bool = False, verbose: bool = True) -> int:
    """Parse, encode, stamp. Returns count of new entries."""
    source = path.read_text(encoding="utf-8", errors="replace")
    frags  = list(_fragments(source, path))
    if not frags:
        return 0

    enc = _load("ciel_encoder_cl", "ciel_encoder.py").get_encoder()

    conn = sqlite3.connect(str(_DB), timeout=15)
    new  = 0
    try:
        for frag in frags:
            text = frag["text"]
            # dedup: check if similar text already in TSM
            existing = conn.execute(
                "SELECT memorise_id FROM memories WHERE D_sense = ? AND D_type = 'code_fragment'",
                (text[:400],)
            ).fetchone()
            if existing:
                continue

            enc_result = enc.encode(text)
            phi = float(enc_result.phase)
            w_s = float(getattr(enc_result, "w_semantic", 0.6))

            ctx  = f"{frag['kind']}::{frag['name']}  {path.name}:{frag['lineno']}"
            mid  = "cf_" + uuid.uuid4().hex[:12]
            ts   = datetime.now(timezone.utc).isoformat()

            if verbose:
                print(f"  [{frag['kind']:8s}] φ={phi:.3f}  {frag['name'][:40]}  ({path.name}:{frag['lineno']})")

            if not dry_run:
                import time as _t
                for _attempt in range(5):
                    try:
                        conn.execute("""
INSERT OR IGNORE INTO memories
    (memorise_id, created_at, D_id, D_sense, D_context, D_type,
     W_S, phi_berry, closure_score, winding_n, target_phase, holonomy_ts)
VALUES (?,?,?,?,?,?,?,?,0,0,?,?)
""", (mid, ts, mid, text[:400], ctx, "code_fragment",
      w_s, phi, phi, ts))
                        break
                    except sqlite3.OperationalError:
                        _t.sleep(0.4 * (_attempt + 1))
                else:
                    continue
                new += 1

        if not dry_run:
            for _attempt in range(5):
                try:
                    conn.commit()
                    break
                except sqlite3.OperationalError:
                    import time as _t2; _t2.sleep(0.5)
    finally:
        conn.close()

    return new


# ── retrieval: znajdź kod przez fazę ─────────────────────────────────────────

def query_code(query_text: str, top_k: int = 8) -> list[dict]:
    """Encode query → phi, retrieve resonant code_fragments from TSM."""
    enc  = _load("ciel_encoder_cl", "ciel_encoder.py").get_encoder()
    hm_m = _load("holonomic_memory_cl", "holonomic_memory.py")
    hm   = hm_m.HolonomicMemory()

    enc_result = enc.encode(query_text)
    phi = float(enc_result.phase)

    results = hm.retrieve_resonant(phi, top_k=top_k, hebbian=False)
    # filter to code_fragment
    code_hits = [r for r in results if r.get("D_type") == "code_fragment"]
    return code_hits


# ── watch mode ────────────────────────────────────────────────────────────────

def watch(directory: Path) -> None:
    """Poll for .py file changes every 3s, re-ingest modified files."""
    import time
    print(f"Watching {directory} for .py changes (Ctrl+C to stop)...")
    seen_mtime: dict[Path, float] = {}

    while True:
        for pyfile in sorted(directory.rglob("*.py")):
            if "__pycache__" in str(pyfile):
                continue
            try:
                mt = pyfile.stat().st_mtime
            except OSError:
                continue
            if seen_mtime.get(pyfile) != mt:
                seen_mtime[pyfile] = mt
                n = ingest_file(pyfile, verbose=True)
                if n:
                    print(f"  → {n} new fragments from {pyfile.name}")
        time.sleep(3)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="CIEL Code Learner")
    ap.add_argument("path", nargs="?", type=Path, help=".py file or directory")
    ap.add_argument("--watch",  action="store_true", help="Watch directory for changes")
    ap.add_argument("--query",  type=str, help="Find code by semantic query")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--top-k", type=int, default=8)
    args = ap.parse_args()

    if args.query:
        hits = query_code(args.query, top_k=args.top_k)
        if not hits:
            print("Brak trafień w TSM dla tego zapytania.")
        for h in hits:
            print(f"\nφ={h['phi_berry']:.3f}  hw={h['holonomic_weight']}  {h['D_context']}")
            print("─" * 60)
            print(h["D_sense"])
        return

    if not args.path:
        ap.print_help()
        return

    if args.watch and args.path.is_dir():
        watch(args.path)
        return

    paths = list(args.path.rglob("*.py")) if args.path.is_dir() else [args.path]
    total = 0
    for p in paths:
        if "__pycache__" in str(p):
            continue
        n = ingest_file(p, dry_run=args.dry_run, verbose=True)
        total += n
    mode = "DRY RUN — " if args.dry_run else ""
    print(f"\n{mode}Łącznie: {total} nowych fragmentów kodu w TSM.")


if __name__ == "__main__":
    main()
