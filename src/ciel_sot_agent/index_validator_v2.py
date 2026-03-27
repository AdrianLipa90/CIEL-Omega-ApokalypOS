from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


DEMO_SHELL_MAP_OBJECT_ID = 'MAP-SOT-0001'
DEMO_SHELL_MAP_V2_OBJECT_ID = 'UP-SOT-0002'
DEMO_SHELL_MAP_OBJECT_PATH = 'integration/upstreams/ciel_omega_demo_shell_map.json'
DEMO_SHELL_MAP_SCHEMA = 'ciel-sot-agent/demo-shell-map/v0.1'
DEMO_SHELL_INVENTORY_SCHEMA = 'ciel-sot-agent/upstream-inventory/v0.1'
DEMO_SHELL_INVENTORY_PATH = 'integration/upstreams/ciel_omega_demo_inventory.json'
INDEX_REGISTRY_V2_PATH = 'integration/registries/index_registry_v2.yaml'
INDEX_REGISTRY_LEGACY_PATH = 'integration/index_registry.yaml'
REQUIRED_DEMO_OBJECT_FIELDS = (
    'id',
    'name',
    'kind',
    'upstream_path',
    'status',
    'integration_role',
    'sot_bindings',
)
FORMAL_UPSTREAM_PREFIXES = ('DER-', 'HYP-', 'DOC-', 'REG-', 'GOV-', 'UP-', 'ORB-', 'IDX-')


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    object_id: str
    message: str


def load_index_registry(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def load_json_file(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def resolve_existing_path(root: str | Path, *candidates: str) -> Path:
    root = Path(root)
    for candidate in candidates:
        candidate_path = root / candidate
        if candidate_path.exists():
            return candidate_path
    return root / candidates[0]


def resolve_index_registry_path(root: str | Path) -> Path:
    return resolve_existing_path(root, INDEX_REGISTRY_V2_PATH, INDEX_REGISTRY_LEGACY_PATH)


def find_demo_shell_map_object(object_map: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for obj in object_map.values():
        if str(obj.get('path', '')).strip() == DEMO_SHELL_MAP_OBJECT_PATH:
            return obj
    return object_map.get(DEMO_SHELL_MAP_OBJECT_ID)


def validate_demo_shell_inventory_data(
    inventory: Mapping[str, Any],
    *,
    map_object_id: str = DEMO_SHELL_MAP_OBJECT_ID,
    expected_upstream_repo: str | None = None,
) -> tuple[list[ValidationIssue], set[str]]:
    issues: list[ValidationIssue] = []

    if str(inventory.get('schema', '')) != DEMO_SHELL_INVENTORY_SCHEMA:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell inventory schema mismatch'))

    upstream_repo = str(inventory.get('upstream_repo', '')).strip()
    if not upstream_repo:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell inventory has no upstream_repo'))
    elif expected_upstream_repo and upstream_repo != expected_upstream_repo:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell inventory upstream_repo does not match shell map upstream_repo'))

    if not str(inventory.get('ref', '')).strip():
        issues.append(ValidationIssue('error', map_object_id, 'demo shell inventory has no ref'))

    if not str(inventory.get('ref_sha', '')).strip():
        issues.append(ValidationIssue('error', map_object_id, 'demo shell inventory has no ref_sha'))

    raw_paths = inventory.get('paths')
    if not isinstance(raw_paths, list) or not raw_paths:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell inventory has no paths list'))
        return issues, set()

    known_paths: set[str] = set()
    for raw_path in raw_paths:
        normalized = str(raw_path).strip()
        if not normalized:
            issues.append(ValidationIssue('error', map_object_id, 'demo shell inventory contains empty path'))
            continue
        known_paths.add(normalized)

    return issues, known_paths


def validate_demo_shell_map_data(
    shell_map: Mapping[str, Any],
    *,
    map_object: Mapping[str, Any],
    registry_ids: set[str],
    known_upstream_paths: set[str] | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    map_object_id = str(map_object.get('id', DEMO_SHELL_MAP_OBJECT_ID))
    accepted_map_binding_ids = {map_object_id, DEMO_SHELL_MAP_OBJECT_ID, DEMO_SHELL_MAP_V2_OBJECT_ID}

    if str(shell_map.get('schema', '')) != DEMO_SHELL_MAP_SCHEMA:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell map schema mismatch'))

    upstream_repo = str(shell_map.get('upstream_repo', '')).strip()
    if not upstream_repo:
        issues.append(ValidationIssue('error', map_object_id, 'demo shell map has no upstream_repo'))
    else:
        provenance = {str(item) for item in map_object.get('provenance', []) or []}
        if upstream_repo not in provenance:
            issues.append(ValidationIssue('error', map_object_id, 'demo shell map provenance does not include upstream_repo'))

    if not str(shell_map.get('role', '')).strip():
        issues.append(ValidationIssue('error', map_object_id, 'demo shell map has no role'))

    if str(map_object.get('provenance_type', '')) != 'imported':
        issues.append(ValidationIssue('error', map_object_id, 'demo shell map object must use provenance_type=imported'))

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
            if known_upstream_paths is not None and upstream_path not in known_upstream_paths:
                issues.append(ValidationIssue('error', map_object_id, f'imported demo object {imported_id} references unknown upstream_path: {upstream_path}'))

        bindings = imported.get('sot_bindings', []) or []
        if not isinstance(bindings, list) or not bindings:
            issues.append(ValidationIssue('error', map_object_id, f'imported demo object {imported_id} has no sot_bindings'))
            continue

        binding_values = {str(binding) for binding in bindings}
        if not (binding_values & accepted_map_binding_ids):
            issues.append(ValidationIssue('error', map_object_id, f'imported demo object {imported_id} does not bind back to an accepted shell-map object id'))

        for binding in binding_values:
            if binding in accepted_map_binding_ids:
                continue
            if binding not in registry_ids:
                issues.append(ValidationIssue('error', map_object_id, f'imported demo object {imported_id} has unknown SOT binding: {binding}'))

    return issues


def validate_index_registry(root: str | Path) -> list[ValidationIssue]:
    root = Path(root)
    registry_path = resolve_index_registry_path(root)
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
        elif not (root / path).exists():
            issues.append(ValidationIssue('error', oid, f'path does not exist: {path}'))

        status = str(obj.get('status', ''))
        placeholder = bool(obj.get('placeholder', False))
        if status == 'placeholder' and not placeholder:
            issues.append(ValidationIssue('error', oid, 'status placeholder but placeholder flag is false'))
        if placeholder and status != 'placeholder':
            issues.append(ValidationIssue('warning', oid, 'placeholder flag true but status is not placeholder'))

        upstream = obj.get('upstream', []) or []
        layer = str(obj.get('layer', ''))
        if layer not in {'architecture', 'analogy', 'protocol', 'report'} and not upstream:
            issues.append(ValidationIssue('warning', oid, 'object has no upstream links'))

        if layer == 'code':
            has_formal_upstream = any(str(u).startswith(FORMAL_UPSTREAM_PREFIXES) for u in upstream)
            if not has_formal_upstream:
                issues.append(ValidationIssue('error', oid, 'code object has no formal/registry upstream'))

    for obj in objects:
        oid = str(obj.get('id', ''))
        for ref_list_name in ('upstream', 'downstream', 'tests', 'interfaces'):
            for ref in obj.get(ref_list_name, []) or []:
                ref = str(ref)
                if ref and ref not in ids and not ref.startswith('GitHub '):
                    issues.append(ValidationIssue('error', oid, f'unknown reference in {ref_list_name}: {ref}'))

    map_object = find_demo_shell_map_object(object_map)
    if map_object:
        map_object_id = str(map_object.get('id', DEMO_SHELL_MAP_OBJECT_ID))
        map_path = root / str(map_object.get('path', ''))
        known_upstream_paths: set[str] | None = None
        upstream_repo = None
        try:
            shell_map = load_json_file(map_path)
        except Exception as exc:  # pragma: no cover
            issues.append(ValidationIssue('error', map_object_id, f'cannot parse demo shell map: {exc}'))
            shell_map = None
        else:
            upstream_repo = str(shell_map.get('upstream_repo', '')).strip() or None

        inventory_path = resolve_existing_path(root, DEMO_SHELL_INVENTORY_PATH)
        if not inventory_path.exists():
            issues.append(ValidationIssue('error', map_object_id, f'demo shell inventory missing: {DEMO_SHELL_INVENTORY_PATH}'))
        else:
            try:
                inventory = load_json_file(inventory_path)
            except Exception as exc:  # pragma: no cover
                issues.append(ValidationIssue('error', map_object_id, f'cannot parse demo shell inventory: {exc}'))
            else:
                inventory_issues, known_upstream_paths = validate_demo_shell_inventory_data(
                    inventory,
                    map_object_id=map_object_id,
                    expected_upstream_repo=upstream_repo,
                )
                issues.extend(inventory_issues)

        if shell_map is not None:
            registry_ids = set(ids)
            registry_ids.add(DEMO_SHELL_MAP_OBJECT_ID)
            registry_ids.add(DEMO_SHELL_MAP_V2_OBJECT_ID)
            issues.extend(
                validate_demo_shell_map_data(
                    shell_map,
                    map_object=map_object,
                    registry_ids=registry_ids,
                    known_upstream_paths=known_upstream_paths,
                )
            )

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
