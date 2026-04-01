from __future__ import annotations

import json
from pathlib import Path

from src.ciel_sot_agent.runtime_evidence_ingest import (
    classify_evidence,
    ingest_runtime_evidence,
    validate_runtime_evidence_data,
)


def _valid_evidence() -> dict[str, object]:
    return {
        'repository_scope': 'AdrianLipa90/CIEL-Desktop',
        'execution_mode': 'desktop_runtime',
        'status_label': 'operational_preview',
        'evidence_class': 'run_and_measured',
        'evidence': {
            'boot_status': 'ok',
            'gui_status': 'ok',
            'latency': {'cold_start_ms': 1840},
            'resource_usage': {'memory_mb': 212},
            'error_log': [],
        },
        'performance_evidence': {'cold_start_ms': 1840},
        'blockers': [],
        'unknowns': [],
        'next_actions': ['run gguf mode'],
    }


def _schema() -> dict[str, object]:
    return {
        'required_fields': [
            'repository_scope',
            'execution_mode',
            'status_label',
            'evidence',
            'evidence_class',
            'performance_evidence',
            'blockers',
            'unknowns',
            'next_actions',
        ],
        'allowed_execution_modes': ['desktop_runtime', 'gguf'],
        'allowed_evidence_classes': ['run_and_measured', 'unverified', 'inferred_from_code'],
        'allowed_status_labels': ['operational_preview', 'not_production_ready'],
    }


def _contract() -> dict[str, object]:
    return {
        'consumer_repo': 'AdrianLipa90/CIEL-Desktop',
        'accepted_modes': ['desktop_runtime', 'gguf'],
        'required_evidence': ['boot_status', 'gui_status', 'latency', 'resource_usage', 'error_log'],
    }


def test_validate_runtime_evidence_accepts_valid_payload() -> None:
    issues = validate_runtime_evidence_data(
        _valid_evidence(),
        schema=_schema(),
        contract=_contract(),
    )
    assert [issue for issue in issues if issue.level == 'error'] == []


def test_validate_runtime_evidence_flags_missing_payload_fields() -> None:
    invalid = _valid_evidence()
    evidence_payload = invalid['evidence']
    assert isinstance(evidence_payload, dict)
    del evidence_payload['resource_usage']
    issues = validate_runtime_evidence_data(
        invalid,
        schema=_schema(),
        contract=_contract(),
    )
    messages = [issue.message for issue in issues if issue.level == 'error']
    assert any('missing required payload evidence: resource_usage' in message for message in messages)


def test_classify_evidence_prefers_declared_class() -> None:
    assert classify_evidence({'evidence_class': 'run_and_measured', 'evidence': {}}) == 'run_and_measured'


def test_ingest_runtime_evidence_writes_report(tmp_path: Path) -> None:
    root = tmp_path
    runtime_modes = root / 'integration' / 'runtime_modes'
    runtime_modes.mkdir(parents=True)
    (runtime_modes / 'desktop_runtime_contract.json').write_text(
        json.dumps(_contract(), ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    (runtime_modes / 'runtime_evidence_schema.json').write_text(
        json.dumps(_schema(), ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    evidence_path = root / 'desktop_runtime_report.json'
    evidence_path.write_text(json.dumps(_valid_evidence(), ensure_ascii=False, indent=2), encoding='utf-8')

    result = ingest_runtime_evidence(root, evidence_path)
    assert result['valid'] is True
    report_path = root / 'integration' / 'reports' / 'runtime_evidence' / 'runtime_evidence_ingest.json'
    assert report_path.exists()
