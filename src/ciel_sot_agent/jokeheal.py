from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ensure_omega_import() -> None:
    root = _repo_root()
    omega_root = root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"
    if omega_root.exists():
        sys.path.insert(0, str(omega_root))


def run_text(text: str, *, user_mode: str | None = None, scar_jsonl: str | None = None) -> Dict[str, Any]:
    _ensure_omega_import()
    from ciel_omega.jokeheal import TensionInput, run_jokeheal  # type: ignore
    from ciel_omega.jokeheal.scar_writer import default_scar_jsonl_path  # type: ignore

    scar_path = scar_jsonl or str(default_scar_jsonl_path())
    output = run_jokeheal(TensionInput(text=text, user_mode=user_mode), scar_jsonl_path=scar_path)
    return output.to_dict()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the CIEL JokeHeal tension-relief subsystem.")
    parser.add_argument("text", nargs="?", help="Text to process. Reads stdin when omitted.")
    parser.add_argument("--mode", dest="user_mode", default=None, help="Optional user mode hint.")
    parser.add_argument("--scar-jsonl", default=None, help="Optional JSONL path for scar records.")
    parser.add_argument("--noema", action="store_true", help="Print only the NOEMA projection.")
    args = parser.parse_args(argv)

    text = args.text if args.text is not None else sys.stdin.read()
    result = run_text(text, user_mode=args.user_mode, scar_jsonl=args.scar_jsonl)
    if args.noema:
        print(result["noema_card"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
