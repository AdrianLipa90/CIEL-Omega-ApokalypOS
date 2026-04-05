"""Synchronise entry point (v1) — builds and emits a sync report to stdout.

Reads the repository registry and coupling map from the ``integration/``
directory, calls ``repo_phase.build_sync_report``, and prints the result
as formatted JSON.  Invoked via the ``ciel-sot-sync`` console script.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .paths import resolve_project_root
from .repo_phase import build_sync_report

_LOG = logging.getLogger(__name__)


def main() -> int:
    root = resolve_project_root(Path(__file__))
    registry_path = root / 'integration' / 'repository_registry.json'
    couplings_path = root / 'integration' / 'couplings.json'
    report = build_sync_report(registry_path, couplings_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
