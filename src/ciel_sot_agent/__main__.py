"""Entry point for ``python -m ciel_sot_agent``.

Usage::

    python -m ciel_sot_agent <command> [args...]

Available commands mirror the installed console scripts.  Pass ``--help``
or omit the command to see this list.
"""

from __future__ import annotations

import importlib
import sys

# Maps short command names to (module, callable) pairs, matching pyproject.toml [project.scripts].
COMMANDS: dict[str, tuple[str, str]] = {
    "sync":                     ("ciel_sot_agent.synchronize",             "main"),
    "sync-v2":                  ("ciel_sot_agent.synchronize_v2",          "main"),
    "gh-coupling":              ("ciel_sot_agent.gh_coupling",             "main"),
    "gh-coupling-v2":           ("ciel_sot_agent.gh_coupling_v2",          "main"),
    "index-validate":           ("ciel_sot_agent.index_validator",         "main"),
    "index-validate-v2":        ("ciel_sot_agent.index_validator_v2",      "main"),
    "orbital-bridge":           ("ciel_sot_agent.orbital_bridge",          "main"),
    "ciel-pipeline":            ("ciel_sot_agent.ciel_pipeline",           "main"),
    "sapiens-client":           ("ciel_sot_agent.sapiens_client",          "main"),
    "runtime-evidence-ingest":  ("ciel_sot_agent.runtime_evidence_ingest", "main"),
    "gui":                      ("ciel_sot_agent.gui.app",                 "main"),
    "install-model":            ("ciel_sot_agent.gguf_manager.cli",        "main"),
    "local-surface":            ("ciel_sot_agent.local_ciel_surface",      "main"),
    "local-nonlocality":        ("ciel_sot_agent.local_nonlocality_fallback", "main"),
    "wpm":                      ("ciel_sot_agent.wpm_cli",                 "main"),
    "bench":                    ("ciel_sot_agent.bench_cli",               "main"),
    "capture":                  ("ciel_sot_agent.capture_cli",             "main"),
}


def _print_help() -> None:
    print("Usage: python -m ciel_sot_agent <command> [args...]")
    print()
    print("Available commands:")
    for name in COMMANDS:
        print(f"  {name}")
    print()
    print("Example:")
    print("  python -m ciel_sot_agent sync")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        _print_help()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        print("Run 'python -m ciel_sot_agent --help' for a list of commands.", file=sys.stderr)
        sys.exit(1)

    # Rewrite sys.argv so the delegated main() receives only its own arguments.
    sys.argv = [f"ciel-sot-{cmd}", *sys.argv[2:]]

    module_path, func_name = COMMANDS[cmd]
    module = importlib.import_module(module_path)
    fn = getattr(module, func_name)
    result = fn()
    sys.exit(result or 0)


if __name__ == "__main__":
    main()
