from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    object_id: str
    message: str


def load_index_registry(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def validate_index_registry(root: str | Path) -> list[ValidationIssue]:
    root = Path(root)
    registry_path = root / 'integration' / 'index_registry.yaml'
    data = load_index_registry(registry_path)
    objects = data.get('objects', []) or []
    issues: list[ValidationIssue] = []
    ids: set[str] = set()
    known_paths: set[str] = set()

    for obj in objects:
        oid = str(obj.get('id', ''))
        path = str(obj.get('path', ''))
        if not oid:
            issues.append(ValidationIssue('error', '(missing-id)', 'object has no id'))
            continue
        if oid in ids:
            issues.append(ValidationIssue('error', oid, 'duplicate object id'))
        ids.add(oid)
        if not path:
            issues.append(ValidationIssue('error', oid, 'object has no path'))
        else:
            known_paths.add(path)
            if not (root / path).exists():
                issues.append(ValidationIssue('error', oid, f'path does not exist: {path}'))

        status = str(obj.get('status', ''))
        placeholder = bool(obj.get('placeholder', False))
        if status == 'placeholder' and not placeholder:
            issues.append(ValidationIssue('error', oid, 'status placeholder but placeholder flag is false'))
        if placeholder and status != 'placeholder':
            issues.append(ValidationIssue('warning', oid, 'placeholder flag true but status is not placeholder'))

        upstream = obj.get('upstream', []) or []
        layer = str(obj.get('layer', ''))
        if layer not in {'architecture', 'analogy'} and layer not in {'protocol', 'report'} and not upstream:
            issues.append(ValidationIssue('warning', oid, 'object has no upstream links'))

        if layer == 'code':
            has_formal_upstream = any(str(u).startswith(('DER-', 'HYP-', 'DOC-', 'REG-')) for u in upstream)
            if not has_formal_upstream:
                issues.append(ValidationIssue('error', oid, 'code object has no formal/registry upstream'))

    for obj in objects:
        oid = str(obj.get('id', ''))
        for ref_list_name in ('upstream', 'downstream', 'tests', 'interfaces'):
            for ref in obj.get(ref_list_name, []) or []:
                ref = str(ref)
                if ref and ref not in ids and not ref.startswith('GitHub '):
                    issues.append(ValidationIssue('error', oid, f'unknown reference in {ref_list_name}: {ref}'))

    return issues


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    issues = validate_index_registry(root)
    for issue in issues:
        print(f'[{issue.level}] {issue.object_id}: {issue.message}')
    if any(i.level == 'error' for i in issues):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
