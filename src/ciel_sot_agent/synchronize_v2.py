from __future__ import annotations

import json
from pathlib import Path

from .repo_phase import build_sync_report


REGISTRY_V2_PATH = 'integration/registries/repository_registry.json'
REGISTRY_LEGACY_PATH = 'integration/repository_registry.json'
COUPLINGS_V2_PATH = 'integration/couplings/repository_couplings.json'
COUPLINGS_LEGACY_PATH = 'integration/couplings.json'


def resolve_existing_path(root: str | Path, *candidates: str) -> Path:
    root = Path(root)
    for candidate in candidates:
        candidate_path = root / candidate
        if candidate_path.exists():
            return candidate_path
    return root / candidates[0]


def resolve_sync_paths(root: str | Path) -> dict[str, Path]:
    root = Path(root)
    return {
        'registry': resolve_existing_path(root, REGISTRY_V2_PATH, REGISTRY_LEGACY_PATH),
        'couplings': resolve_existing_path(root, COUPLINGS_V2_PATH, COUPLINGS_LEGACY_PATH),
    }


def build_sync_report_v2(root: str | Path) -> dict[str, object]:
    root = Path(root)
    paths = resolve_sync_paths(root)
    report = build_sync_report(paths['registry'], paths['couplings'])
    return {
        'schema': 'ciel-sot-agent/sync-report/v0.2',
        'path_resolution': {
            'registry': str(paths['registry'].relative_to(root)),
            'couplings': str(paths['couplings'].relative_to(root)),
        },
        'report': report,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    report = build_sync_report_v2(root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
