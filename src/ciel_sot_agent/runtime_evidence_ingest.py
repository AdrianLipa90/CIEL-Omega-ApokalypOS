from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


RUNTIME_CONTRACT_PATH = 'integration/runtime_modes/desktop_runtime_contract.json'
RUNTIME_EVIDENCE_SCHEMA_PATH = 'integration/runtime_modes/runtime_evidence_schema.json'


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    object_id: str
    message: str


def load_json_file(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def validate_runtime_evidence_data(
    evidence: Mapping[str, Any],
    *,
    schema: Mapping[str, Any],
    contract: Mapping[str, Any],
    object_id: str = 'RT-EVID-0001',
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    required_fields = schema.get('required_fields', [])
    for field in required_fields:
        if field not in evidence:
            issues.append(ValidationIssue('error', object_id, f'missing required evidence field: {field}'))

    execution_mode = str(evidence.get('execution_mode', '')).strip()
    if execution_mode not in {str(mode) for mode in schema.get('allowed_execution_modes', [])}:
        issues.append(ValidationIssue('error', object_id, f'unsupported execution_mode: {execution_mode or "(empty)"}'))
    accepted_modes = {str(mode) for mode in contract.get('accepted_modes', [])}
    if execution_mode and execution_mode not in accepted_modes:
        issues.append(ValidationIssue('error', object_id, f'execution_mode not accepted by contract: {execution_mode}'))

    evidence_class = str(evidence.get('evidence_class', '')).strip()
    if evidence_class not in {str(item) for item in schema.get('allowed_evidence_classes', [])}:
        issues.append(ValidationIssue('error', object_id, f'invalid evidence_class: {evidence_class or "(empty)"}'))

    status_label = str(evidence.get('status_label', '')).strip()
    if status_label not in {str(item) for item in schema.get('allowed_status_labels', [])}:
        issues.append(ValidationIssue('error', object_id, f'invalid status_label: {status_label or "(empty)"}'))

    if str(evidence.get('repository_scope', '')).strip() != str(contract.get('consumer_repo', '')).strip():
        issues.append(ValidationIssue('warning', object_id, 'repository_scope differs from contract consumer_repo'))

    required_evidence = {str(item) for item in contract.get('required_evidence', [])}
    payload = evidence.get('evidence')
    if not isinstance(payload, Mapping):
        issues.append(ValidationIssue('error', object_id, 'evidence must be an object'))
    else:
        missing_payload_fields = sorted(required_evidence - {str(key) for key in payload.keys()})
        for field in missing_payload_fields:
            issues.append(ValidationIssue('error', object_id, f'missing required payload evidence: {field}'))

    for list_field in ('blockers', 'unknowns', 'next_actions'):
        if list_field in evidence and not isinstance(evidence.get(list_field), list):
            issues.append(ValidationIssue('error', object_id, f'{list_field} must be a list'))

    return issues


def classify_evidence(evidence: Mapping[str, Any]) -> str:
    evidence_class = str(evidence.get('evidence_class', '')).strip()
    if evidence_class:
        return evidence_class
    if evidence.get('evidence'):
        return 'inferred_from_code'
    return 'unverified'


def ingest_runtime_evidence(
    root: str | Path,
    evidence_path: str | Path,
) -> dict[str, Any]:
    root = Path(root)
    contract = load_json_file(root / RUNTIME_CONTRACT_PATH)
    schema = load_json_file(root / RUNTIME_EVIDENCE_SCHEMA_PATH)
    evidence = load_json_file(evidence_path)

    issues = validate_runtime_evidence_data(evidence, schema=schema, contract=contract)
    result = {
        'schema': 'ciel-sot-agent/runtime-evidence-ingest/v0.1',
        'source_evidence_path': str(evidence_path),
        'evidence_class': classify_evidence(evidence),
        'issues': [issue.__dict__ for issue in issues],
        'valid': not any(issue.level == 'error' for issue in issues),
    }

    out_dir = root / 'integration' / 'reports' / 'runtime_evidence'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'runtime_evidence_ingest.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description='Ingest desktop runtime evidence into SOT audit surfaces.')
    parser.add_argument('evidence', help='Path to desktop runtime evidence JSON file.')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    result = ingest_runtime_evidence(root, args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get('valid') else 1


if __name__ == '__main__':
    raise SystemExit(main())
