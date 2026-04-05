"""CLI entry point for GGUF model installation.

Usage:
    ciel-sot-install-model                       # download default (TinyLlama)
    ciel-sot-install-model --model qwen2.5-0.5b-q4
    ciel-sot-install-model --model qwen2.5-1.5b-q4
    ciel-sot-install-model --list
"""

from __future__ import annotations

import argparse
import sys

from .manager import KNOWN_MODELS, GGUFManager


def _progress(done: int, total: int) -> None:
    if total > 0:
        pct = done * 100 // total
        bar = "#" * (pct // 2) + "-" * (50 - pct // 2)
        mb_done = done / 1_048_576
        mb_total = total / 1_048_576
        print(f"\r  [{bar}] {pct:3d}%  {mb_done:.1f}/{mb_total:.1f} MB", end="", flush=True)
    else:
        mb_done = done / 1_048_576
        print(f"\r  {mb_done:.1f} MB downloaded…", end="", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ciel-sot-install-model",
        description="Download a GGUF language model for CIEL SOT Agent.",
    )
    parser.add_argument(
        "--model",
        default="tinyllama-1.1b-chat-q4",
        help=(
            "Model key to download.  Run --list to see available keys.  "
            "Default: tinyllama-1.1b-chat-q4"
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_models",
        help="List all available models and exit.",
    )
    parser.add_argument(
        "--models-dir",
        default=None,
        help="Directory to store models (default: ~/.local/share/ciel/models).",
    )

    args = parser.parse_args(argv)

    if args.list_models:
        print("Available models:")
        for key, spec in KNOWN_MODELS.items():
            tags = ", ".join(spec.tags)
            default_marker = " [DEFAULT]" if key == "tinyllama-1.1b-chat-q4" else ""
            print(f"  {key}{default_marker}")
            print(f"    {spec.description}")
            print(f"    tags: {tags}")
            print(f"    url:  {spec.url}")
        return 0

    mgr = GGUFManager(models_dir=args.models_dir, progress_callback=_progress)

    if args.model not in KNOWN_MODELS:
        print(
            f"ERROR: unknown model key '{args.model}'. "
            f"Known keys: {', '.join(KNOWN_MODELS)}",
            file=sys.stderr,
        )
        return 1

    spec = KNOWN_MODELS[args.model]
    dest = mgr.models_dir / spec.name

    if dest.exists():
        print(f"[ciel-sot-install-model] Already installed: {dest}")
        return 0

    print(f"[ciel-sot-install-model] Downloading: {spec.description}")
    print(f"  Source: {spec.url}")
    print(f"  Destination: {dest}")

    try:
        path = mgr.ensure_model(args.model)
        print()  # newline after progress bar
        print(f"[ciel-sot-install-model] Model ready: {path}")
    except Exception as exc:  # noqa: BLE001
        print()
        print(f"ERROR: download failed — {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
