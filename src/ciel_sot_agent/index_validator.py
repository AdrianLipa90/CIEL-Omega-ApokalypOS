from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


DEMO_SHELL_MAP_OBJECT_ID = 'MAP-SOT-0001'
DEMO_SHELL_MAP_SCHEMA = 'ciel-sot-agent/demo-shell-map/v0.1'
REQUIRED_DEMO_OBJECT_FIELDS = (
    'id',
    'name',
    'kind',
    'upstream_path',
    'status',
    'integration_role',
    'sot_bindings',
)


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    object_id: str
    message: str


def load_index_registry(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def load_json_file(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def validate_demo_shell_map_data(
    shell_map: Mapping[str, Any],
    *,
    map_object: Mapping[str, Any],
    registry_ids: set[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    map_object_id = str(map_object.get('id', DEMO_SHELL_MAP_OBJECT_ID))

    if str(shell_map.get('schema', '')) != DEMO_SHELL_MAP_SCHEMA:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell map schema mismatch'))

    upstream_repo = str(shell_map.get('upstream_repo', '')).strip()
    if not upstream_repo:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell map has no upstream_repo'))
    else:
        provenance = {str(item) for item in map_object.get('provenance', []) or []}
        if upstream_repo not in provenance:
            issues.append(ValidationIssue('error', map_object_id, 'MAP-SOT-0001 provenance does not include upstream_repo'))

    if not str(shell_map.get('role', '')).strip():
        issues.append(ValidationIssue('error', map_object_id, 'demo shell map has no role'))

    if str(map_object.get('provenance_type', '')) != 'imported':
        issues.append(ValidationIssue('error', map_object_id, 'MAP-SOT-0001 must use provenance_type=imported'))

    if 'TST-SOT-0002' not in (map_object.get('tests', []) or []):
        issues.append(ValidationIssue('warning', map_object_id, 'MAP-SOT-0001 should be covered by TST-SOT-0002'))

    if 'IF-SOT-0001' not in (map_object.get('interfaces', []) or []):
        issues.append(ValidationIssue('warning', map_object_id, 'MAP-SOT-0001 should expose IF-SOT-0001'))

    imported_objects = shell_map.get('objects')
    if not isinstance(imported_objects, list) or not imported_objects:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell map has no objects list'))
        return issues

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()

    for imported in imported_objects:
        imported_id = str(imported.get('id', '')).strip()
        if not imported_id:
            issues.append(ValidationIssue('error', map_object_id, 'imported demo object has no id'))
            continue
        if imported_id in seen_ids:
            issues.append(ValidationIssue('error', map_object_id, f'duplicate imported demo object id: {imported_id}'))
        seen_ids.add(imported_id)

        if not imported_id.startswith('IMP-DEMO-'):
            issues.append(ValidationIssue('warning', map_object_id, f'imported demo object id has unexpected prefix: {imported_id}'))

        for field in REQUIRED_DEMO_OBJECT_FIELDS:
            if field == 'sot_bindings':
                continue
            value = str(imported.get(field, '')).strip()
            if not value:
                issues.append(ValidationIssue('error', map_object_id, f'imported demo object {imported_id} is missing field: {field}'))

        upstream_path = str(imported.get('upstream_path', '')).strip()
        if upstream_path:
            if upstream_path in seen_paths:
                issues.append(ValidationIssue('warning', map_object_id, f'duplicate upstream_path in demo shell map: {upstream_path}'))
            seen_paths.add(upstream_path)

        bindings = imported.get('sot_bindings', []) or []
        if not isinstance(bindings, list) or not bindings:
            issues.append(ValidationIssue('error', map_object_id, f'imported demo object {imported_id} has no sot_bindings'))
            continue

        if map_object_id not in {str(binding) for binding in bindings}:
            issues.append(ValidationIssue('error', map_object_id, f'imported demo object {imported_id} does not bind back to {map_object_id}'))

        for binding in bindings:
            binding = str(binding)
            if binding not in registry_ids:
                issues.append(ValidationIssue('error', map_object_id, f'imported demo object {imported_id} has unknown SOT binding: {binding}'))

    return issues


def validate_index_registry(root: str | Path) -> list[ValidationIssue]:
    root = Path(root)
    registry_path = root / 'integration' / 'index_registry.yaml'
    data = load_index_registry(registry_path)
    objects = data.get('objects', []) or []
    issues: list[ValidationIssue] = []
    ids: set[str] = set()
    object_map: dict[str, dict[str, Any]] = {}

    for obj in objects:
        oid = str(obj.get('id', ''))
        path = str(obj.get('path', ''))
        if not oid:
            issues.append(ValidationIssue('error', '(missing-id)', 'object has no id'))
            continue
        if oid in ids:
            issues.append(ValidationIssue('error', oid, 'duplicate object id'))
        ids.add(oid)
        object_map[oid] = obj
        if not path:
            issues.append(ValidationIssue('error', oid, 'object has no path'))
        else:
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

    map_object = object_map.get(DEMO_SHELL_MAP_OBJECT_ID)
    if map_object:
        map_path = root / str(map_object.get('path', ''))
        try:
            shell_map = load_json_file(map_path)
        except Exception as exc:  # pragma: no cover - exercised through failing repos, not unit fixture
            issues.append(ValidationIssue('error', DEMO_SHELL_MAP_OBJECT_ID, f'cannot parse demo shell map: {exc}'))
        else:
            issues.extend(validate_demo_shell_map_data(shell_map, map_object=map_object, registry_ids=ids))

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
