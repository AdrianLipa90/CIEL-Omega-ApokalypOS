from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .gh_coupling_v2 import build_live_coupling
from .index_validator import validate_index_registry as validate_index_registry_v1
from .index_validator_v2 import validate_index_registry as validate_index_registry_v2
from .integration_mirror import sync_integration_mirrors
from .paths import resolve_project_root
from .synchronize_v2 import build_sync_report_v2

PIPELINE_REPORT_PATH = Path('integration') / 'reports' / 'pipeline_maintenance' / 'latest_pipeline_report.json'


def run_pipeline(root: str | Path, *, run_gh_coupling: bool = False) -> dict[str, Any]:
    root = Path(root)

    mirror_results = sync_integration_mirrors(root)
    sync_report = build_sync_report_v2(root)
    issues_v1 = validate_index_registry_v1(root)
    issues_v2 = validate_index_registry_v2(root)

    gh_report: dict[str, Any] | None = None
    if run_gh_coupling:
        gh_report = build_live_coupling(root)

    report = {
        'schema': 'ciel-sot-agent/pipeline-maintenance-report/v0.1',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'root': str(root),
        'steps': {
            'mirror_sync': {
                'updated_pairs': [list(result.pair) for result in mirror_results if result.updated],
                'results': [
                    {'pair': list(result.pair), 'updated': result.updated, 'reason': result.reason}
                    for result in mirror_results
                ],
            },
            'sync_v2': sync_report,
            'index_validation_v1': {
                'error_count': len([issue for issue in issues_v1 if issue.level == 'error']),
                'warning_count': len([issue for issue in issues_v1 if issue.level == 'warning']),
            },
            'index_validation_v2': {
                'error_count': len([issue for issue in issues_v2 if issue.level == 'error']),
                'warning_count': len([issue for issue in issues_v2 if issue.level == 'warning']),
            },
            'gh_coupling_v2': gh_report if run_gh_coupling else {'skipped': True},
        },
    }

    report_path = root / PIPELINE_REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main() -> int:
    root = resolve_project_root(Path(__file__))
    report = run_pipeline(root, run_gh_coupling=False)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
