"""ciel-sot-wpm — CLI do Wave Phase Memory (WPM).

Komendy:
  list              tabela wszystkich wspomnień
  show <id>         pełna treść wpisu (UUID lub prefix 8 znaków)
  search <query>    szukaj po treści D_sense
  network           graf skojarzeń między wspomnieniami
  export            JSON dump wszystkich wpisów
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _wpm_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return (
        root
        / "src"
        / "CIEL_OMEGA_COMPLETE_SYSTEM"
        / "CIEL_MEMORY_SYSTEM"
        / "WPM"
        / "wave_snapshots"
        / "wave_archive.h5"
    )


def _load_all() -> list[dict[str, Any]]:
    try:
        import h5py
    except ImportError:
        print("h5py not available — install it: pip install h5py", file=sys.stderr)
        sys.exit(1)

    path = _wpm_path()
    if not path.exists():
        print(f"wave_archive.h5 not found: {path}", file=sys.stderr)
        sys.exit(1)

    memories = []
    with h5py.File(path, "r") as h5:
        mems = h5.get("memories", {})
        for mid in list(mems.keys()):
            grp = mems[mid]

            def _s(key: str) -> str:
                if key not in grp:
                    return ""
                raw = grp[key][()]
                return raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)

            assoc_raw = _s("D_associations")
            try:
                associations = json.loads(assoc_raw) if assoc_raw else []
            except Exception:
                associations = []

            memories.append(
                {
                    "id": mid,
                    "sense": _s("D_sense"),
                    "context": _s("D_context"),
                    "dtype": _s("D_type"),
                    "source": _s("source"),
                    "created_at": _s("created_at"),
                    "rationale": _s("rationale"),
                    "associations": associations,
                }
            )
    return sorted(memories, key=lambda m: m["created_at"])


def _cmd_list(args: argparse.Namespace) -> None:
    memories = _load_all()
    if not memories:
        print("(brak wpisów w WPM)")
        return

    # Column widths
    print(f"{'ID':8}  {'TYP':16}  {'ŹRÓDŁO':16}  {'DATA':16}  KONTEKST")
    print("-" * 80)
    for m in memories:
        short_id = m["id"][:8]
        dtype = m["dtype"][:16]
        source = m["source"][:16]
        created = m["created_at"][:16]
        context = m["context"][:30]
        print(f"{short_id}  {dtype:16}  {source:16}  {created}  {context}")
    print(f"\n{len(memories)} wpisów łącznie.")


def _cmd_show(args: argparse.Namespace) -> None:
    memories = _load_all()
    prefix = args.id.lower().replace("wpm:", "")
    matches = [m for m in memories if m["id"].lower().startswith(prefix)]
    if not matches:
        print(f"Nie znaleziono wpisu z ID prefix: {prefix!r}", file=sys.stderr)
        sys.exit(1)
    if len(matches) > 1:
        print(f"Niejednoznaczny prefix — {len(matches)} pasujących:", file=sys.stderr)
        for m in matches:
            print(f"  WPM:{m['id'][:8]}  {m['context']}", file=sys.stderr)
        sys.exit(1)

    m = matches[0]
    print(f"WPM:{m['id']}")
    print(f"Typ:      {m['dtype']}")
    print(f"Źródło:   {m['source']}")
    print(f"Kontekst: {m['context']}")
    print(f"Data:     {m['created_at']}")
    print(f"Uzas.:    {m['rationale']}")
    if m["associations"]:
        assoc_short = [f"WPM:{a[:8]}" for a in m["associations"]]
        print(f"Powiąz.:  {', '.join(assoc_short)}")
    print()
    print(m["sense"])


def _cmd_search(args: argparse.Namespace) -> None:
    query = args.query.lower()
    memories = _load_all()
    hits = [m for m in memories if query in m["sense"].lower() or query in m["context"].lower()]
    if not hits:
        print(f"Brak wyników dla: {args.query!r}")
        return
    print(f"{len(hits)} wyników dla {args.query!r}:\n")
    for m in hits:
        short_id = m["id"][:8]
        snippet = m["sense"][:120].replace("\n", " ")
        print(f"WPM:{short_id}  [{m['dtype']}]  {snippet}")


def _cmd_network(args: argparse.Namespace) -> None:
    memories = _load_all()
    id_to_short = {m["id"]: m["id"][:8] for m in memories}
    has_edges = False
    print("Graf skojarzeń WPM:\n")
    for m in memories:
        short = m["id"][:8]
        if m["associations"]:
            has_edges = True
            targets = [f"WPM:{id_to_short.get(a, a[:8])}" for a in m["associations"]]
            print(f"  WPM:{short}  [{m['dtype']}]  →  {', '.join(targets)}")
        else:
            print(f"  WPM:{short}  [{m['dtype']}]  (brak powiązań)")
    if not has_edges:
        print("\n(brak krawędzi — żadne wpisy nie mają skojarzeń)")


def _cmd_export(args: argparse.Namespace) -> None:
    memories = _load_all()
    print(json.dumps(memories, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ciel-sot-wpm",
        description="Wave Phase Memory (WPM) — przeglądarka i wyszukiwarka wspomnień CIEL",
    )
    sub = parser.add_subparsers(dest="cmd", metavar="KOMENDA")

    sub.add_parser("list", help="Lista wszystkich wpisów (tabela)")

    p_show = sub.add_parser("show", help="Pokaż pełną treść wpisu")
    p_show.add_argument("id", help="UUID lub prefix 8 znaków (np. 46297f7f lub WPM:46297f7f)")

    p_search = sub.add_parser("search", help="Szukaj po treści")
    p_search.add_argument("query", help="Fraza do wyszukania (case-insensitive)")

    sub.add_parser("network", help="Graf skojarzeń między wspomnieniami")
    sub.add_parser("export", help="JSON dump wszystkich wpisów")

    args = parser.parse_args(argv)

    if args.cmd is None:
        parser.print_help()
        return 0

    dispatch = {
        "list": _cmd_list,
        "show": _cmd_show,
        "search": _cmd_search,
        "network": _cmd_network,
        "export": _cmd_export,
    }
    dispatch[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
