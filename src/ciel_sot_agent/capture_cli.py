"""ciel-sot-capture — szybki zapis idei do WPM i ideas_capture.md.

Użycie:
  ciel-sot-capture "fragment idei"
  ciel-sot-capture --type anchor "zasada etyczna"
  ciel-sot-capture --context "sesja-2026-04-16" "pomysł na optymalizację"
"""
from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_to_wpm(sense: str, dtype: str, context: str) -> str:
    root = _project_root()
    sys.path.insert(0, str(root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"))
    sys.path.insert(0, str(root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega"))

    from memory.monolith.unified_memory import WPMWriterHDF5, MemoriseD  # noqa: PLC0415

    wpm_path = (
        root
        / "src"
        / "CIEL_OMEGA_COMPLETE_SYSTEM"
        / "CIEL_MEMORY_SYSTEM"
        / "WPM"
        / "wave_snapshots"
        / "wave_archive.h5"
    )

    wpm = WPMWriterHDF5(wpm_path)
    now = datetime.now().isoformat()
    mid = str(uuid.uuid4())

    rec = MemoriseD(
        memorise_id=mid,
        created_at=now,
        D_id=str(uuid.uuid4()),
        D_context=context,
        D_sense=sense,
        D_associations=[],
        D_timestamp=now,
        D_meta={"source_event": "capture_cli", "session_date": now[:10]},
        D_type=dtype,
        D_attr={"length": len(sense)},
        weights={"W_L": 0.50, "W_S": 0.55, "W_K": 0.60, "W_E": 0.65},
        rationale="captured via ciel-sot-capture CLI",
        source="CIEL_AUTONOMOUS",
    )

    wpm.save(rec)
    return mid


def _write_to_ideas(sense: str, dtype: str, mid: str) -> None:
    root = _project_root()
    ideas_file = root / "docs" / "ideas_capture.md"

    if not ideas_file.exists():
        ideas_file.write_text(
            "# Ideas Capture — Protokół \"Złap i Zakotwicz\"\n\n"
            "## Jak używać\n"
            "Napisz `!! <fragment>` lub użyj `ciel-sot-capture \"fragment\"`.\n\n"
            "---\n\n## Idee\n\n",
            encoding="utf-8",
        )

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    badge = f"[{dtype}]" if dtype != "text" else ""
    entry = f"### {now} {badge}\n\n{sense}\n\n*WPM:{mid[:8]}*\n\n---\n\n"

    with open(ideas_file, "a", encoding="utf-8") as f:
        f.write(entry)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ciel-sot-capture",
        description="Szybki zapis idei do WPM i ideas_capture.md",
    )
    parser.add_argument("sense", help="Treść wspomnienia / idei")
    parser.add_argument(
        "--type", dest="dtype", default="text",
        choices=["text", "anchor", "affective", "milestone"],
        help="Typ wpisu (default: text). 'anchor' → ethical_anchor",
    )
    parser.add_argument(
        "--context", default="",
        help="Kontekst (opcjonalny, default: auto z daty)",
    )

    args = parser.parse_args(argv)

    # Normalize type
    dtype_map = {"anchor": "ethical_anchor", "affective": "affective_memory"}
    dtype = dtype_map.get(args.dtype, args.dtype)
    context = args.context or f"capture_{datetime.now().strftime('%Y-%m-%d')}"

    try:
        mid = _write_to_wpm(args.sense, dtype, context)
    except Exception as exc:
        print(f"Błąd zapisu do WPM: {exc}", file=sys.stderr)
        return 1

    try:
        _write_to_ideas(args.sense, dtype, mid)
    except Exception as exc:
        print(f"Ostrzeżenie: błąd zapisu do ideas_capture.md: {exc}", file=sys.stderr)

    print(f"WPM:{mid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
