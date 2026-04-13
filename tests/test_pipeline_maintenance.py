from __future__ import annotations

import json
from pathlib import Path

from src.ciel_sot_agent.pipeline_maintenance import PIPELINE_REPORT_PATH, run_pipeline


def test_run_pipeline_writes_report_and_contains_expected_steps() -> None:
    root = Path(__file__).resolve().parents[1]
    report = run_pipeline(root, run_gh_coupling=False)

    assert report['schema'] == 'ciel-sot-agent/pipeline-maintenance-report/v0.1'
    assert report['steps']['gh_coupling_v2']['skipped'] is True
    assert 'mirror_sync' in report['steps']
    assert 'sync_v2' in report['steps']
    assert 'index_validation_v1' in report['steps']
    assert 'index_validation_v2' in report['steps']

    report_path = root / PIPELINE_REPORT_PATH
    assert report_path.exists()
    persisted = json.loads(report_path.read_text(encoding='utf-8'))
    assert persisted['schema'] == report['schema']
