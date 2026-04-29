#!/usr/bin/env python3
"""Ingest all memory files (md, txt, json, jsonl, yaml, pdf, docx, db) into TSM.

Parses each file into text chunks, encodes with CIELEncoder → phi_berry,
then stamps into holonomic_memory TSM (only new entries, never overwrites).

Usage:
    python3 scripts/ingest_memory_files.py [--dry-run] [--sources PATH ...]

Default sources:
    ~/Pulpit/CIEL_memories/          (md, jsonl, json, yaml, txt, pdf)
    ~/.claude/projects/-home-adrian/memory/  (md)
    ~/Pulpit/CIEL_memories/ciel_algo_repo/source_material/  (md, yaml, txt)
"""
from __future__ import annotations

import argparse
import importlib.util as ilu
import json
import re
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_MEM_DIR = Path.home() / "Pulpit/CIEL_memories"
_CLAUDE_MEM = Path.home() / ".claude/projects/-home-adrian/memory"

_DEFAULT_SOURCES = [
    _MEM_DIR,
    _CLAUDE_MEM,
    _MEM_DIR / "ciel_algo_repo" / "source_material",
    Path.home() / "Pulpit" / "training",
]

_SKIP_DIRS = {"raw_logs", ".claude", "__pycache__", "ciel_algo_repo/src", "ciel_semantic_orbital"}
_SKIP_SUFFIXES = {".pyc", ".npz", ".h5", ".pkl", ".lock"}
_SKIP_FILENAMES = {"handoff.md", "handoff_archive_2026_04.md"}  # session logs, not content
_MAX_CHUNK = 800   # chars per TSM entry
_MIN_CHUNK = 40


def _load_direct(name: str, rel: str):
    path = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory" / rel
    spec = ilu.spec_from_file_location(name, path)
    mod = ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Parsers ───────────────────────────────────────────────────────────────────

def _chunks(text: str, source: str) -> list[dict]:
    """Split text into chunks, return list of {text, source, d_type}."""
    # Split on double newlines or heading markers
    parts = re.split(r'\n{2,}|(?=^#{1,3} )', text, flags=re.MULTILINE)
    results = []
    for p in parts:
        p = p.strip()
        if len(p) < _MIN_CHUNK:
            continue
        if len(p) > _MAX_CHUNK:
            # hard split
            for i in range(0, len(p), _MAX_CHUNK):
                sub = p[i:i+_MAX_CHUNK].strip()
                if len(sub) >= _MIN_CHUNK:
                    results.append({"text": sub, "source": source})
        else:
            results.append({"text": p, "source": source})
    return results


def parse_md(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return _chunks(text, str(path))


def parse_txt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return _chunks(text, str(path))


def parse_json(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = list(data.values()) if len(data) > 1 else [data]
    else:
        return []
    results = []
    for item in items:
        if isinstance(item, dict):
            text = (item.get("text") or item.get("content") or item.get("sense")
                    or item.get("description") or item.get("name") or str(item))
        else:
            text = str(item)
        text = str(text).strip()
        if len(text) >= _MIN_CHUNK:
            results.append({"text": text[:_MAX_CHUNK], "source": str(path)})
    return results


def parse_jsonl(path: Path) -> list[dict]:
    results = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except Exception:
            continue
        if isinstance(item, dict):
            text = (item.get("text") or item.get("content") or item.get("sense")
                    or item.get("description") or str(item))
        else:
            text = str(item)
        text = str(text).strip()
        if len(text) >= _MIN_CHUNK:
            results.append({"text": text[:_MAX_CHUNK], "source": str(path)})
    return results


def parse_yaml(path: Path) -> list[dict]:
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return parse_txt(path)
    if data is None:
        return []
    text = json.dumps(data, ensure_ascii=False, indent=2)
    return _chunks(text, str(path))


def parse_pdf(path: Path) -> list[dict]:
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                pages.append(t)
        return _chunks("\n\n".join(pages), str(path))
    except Exception as e:
        print(f"  [pdf error] {path.name}: {e}")
        return []


def parse_docx(path: Path) -> list[dict]:
    try:
        import docx  # type: ignore
        doc = docx.Document(str(path))
        text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return _chunks(text, str(path))
    except Exception as e:
        print(f"  [docx error] {path.name}: {e}")
        return []


def parse_db(path: Path) -> list[dict]:
    """Extract text from SQLite — reads text columns from all tables."""
    results = []
    try:
        conn = sqlite3.connect(str(path))
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        for table in tables:
            try:
                cols_info = conn.execute(f"PRAGMA table_info({table})").fetchall()
                text_cols = [c[1] for c in cols_info if "text" in c[2].lower() or "char" in c[2].lower()]
                if not text_cols:
                    continue
                rows = conn.execute(
                    f"SELECT {','.join(text_cols)} FROM {table} LIMIT 200"
                ).fetchall()
                for row in rows:
                    text = " | ".join(str(v) for v in row if v and len(str(v)) > 10)
                    if len(text) >= _MIN_CHUNK:
                        results.append({"text": text[:_MAX_CHUNK], "source": f"{path}:{table}"})
            except Exception:
                continue
        conn.close()
    except Exception as e:
        print(f"  [db error] {path.name}: {e}")
    return results


_PARSERS = {
    ".md": parse_md, ".txt": parse_txt,
    ".json": parse_json, ".jsonl": parse_jsonl,
    ".yaml": parse_yaml, ".yml": parse_yaml,
    ".pdf": parse_pdf, ".docx": parse_docx, ".doc": parse_docx,
    ".db": parse_db,
}


def collect_files(sources: list[Path]) -> list[Path]:
    files = []
    for src in sources:
        if not src.exists():
            continue
        if src.is_file():
            files.append(src)
            continue
        for p in sorted(src.rglob("*")):
            # skip excluded dirs
            if any(skip in str(p) for skip in _SKIP_DIRS):
                continue
            if p.suffix.lower() in _SKIP_SUFFIXES:
                continue
            if p.name in _SKIP_FILENAMES:
                continue
            if p.suffix.lower() in _PARSERS and p.is_file():
                files.append(p)
    return files


def already_ingested(conn: sqlite3.Connection, text: str) -> bool:
    """Check if identical D_sense already exists in TSM."""
    row = conn.execute(
        "SELECT 1 FROM memories WHERE D_sense = ? LIMIT 1", (text[:200],)
    ).fetchone()
    return row is not None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sources", nargs="*", type=Path)
    args = parser.parse_args()

    sources = [Path(s) for s in args.sources] if args.sources else _DEFAULT_SOURCES

    print(f"Sources: {[str(s) for s in sources]}")

    # Load encoder
    enc_mod = _load_direct("ciel_encoder_ingest", "ciel_encoder.py")
    enc = enc_mod.get_encoder()
    print(f"Encoder: {enc.model_name}")

    # Load holonomic memory
    hm_mod = _load_direct("holonomic_memory_ingest", "holonomic_memory.py")
    hm = hm_mod.HolonomicMemory()
    db_path = hm.db_path
    print(f"TSM: {db_path}")

    files = collect_files(sources)
    print(f"Files found: {len(files)}")

    # Heisenberg soft-clip — load hw monitor for resource-aware throttling
    _hw_clip = None
    try:
        _hw_spec = ilu.spec_from_file_location("ciel_hw_monitor", _ROOT / "scripts/ciel_hw_monitor.py")
        _hw_mod = ilu.module_from_spec(_hw_spec)
        _hw_spec.loader.exec_module(_hw_mod)
        _hw_clip = _hw_mod.heisenberg_clip
    except Exception:
        pass

    conn = sqlite3.connect(str(db_path))
    total_new = 0
    total_skip = 0

    try:
        for fpath in files:
            suffix = fpath.suffix.lower()
            parse_fn = _PARSERS.get(suffix)
            if not parse_fn:
                continue
            chunks = parse_fn(fpath)
            if not chunks:
                continue

            file_new = 0
            for chunk in chunks:
                text = chunk["text"].strip()
                if len(text) < _MIN_CHUNK:
                    continue
                if already_ingested(conn, text):
                    total_skip += 1
                    continue

                # Determine D_type from source path
                p = str(fpath)
                if "hunch" in p:
                    d_type = "hunch"
                elif "ciel_entries" in p or "ciel_dziennik" in p:
                    d_type = "ciel_entry"
                elif ".claude" in p and "memory" in p:
                    d_type = "claude_memory"
                elif "source_material" in p or "kontrakt" in p:
                    d_type = "contract"
                elif suffix == ".pdf":
                    d_type = "document"
                elif suffix == ".db":
                    d_type = "db_extract"
                else:
                    d_type = "ingested"

                enc_result = enc.encode(text)
                phi = float(enc_result.phase)
                sector = enc_result.dominant_sector
                mid = str(uuid.uuid4())
                ts = datetime.now(timezone.utc).isoformat()

                print(f"  [{d_type}] φ={phi:.3f} s={sector} | {text[:60]!r}")

                if not args.dry_run:
                    conn.execute("""
INSERT INTO memories (memorise_id, created_at, D_id, D_sense, D_type,
                      phi_berry, closure_score, winding_n, target_phase, holonomy_ts, source)
VALUES (?,?,?,?,?, ?,?,?,?,?,?)
""", (mid, ts, mid, text[:400], d_type,
      phi, 0.5, 0, phi, ts, str(fpath)))
                    file_new += 1
                    total_new += 1

            if file_new and not args.dry_run:
                conn.commit()
            if chunks:
                print(f"  {fpath.name}: {file_new} new, {len(chunks)-file_new} skipped")

            # Heisenberg throttle between files — sleep if system under pressure
            if _hw_clip and not args.dry_run and file_new > 0:
                clip = _hw_clip()
                if clip["sleep_s"] > 0.05:
                    time.sleep(clip["sleep_s"])

    finally:
        conn.close()

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Done: {total_new} new entries, {total_skip} duplicates skipped.")


if __name__ == "__main__":
    main()
