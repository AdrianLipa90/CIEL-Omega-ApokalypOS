from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .paths import resolve_project_root


PAIR_MAPPINGS: tuple[tuple[str, str], ...] = (
    ('integration/repository_registry.json', 'integration/registries/repository_registry.json'),
    ('integration/couplings.json', 'integration/couplings/repository_couplings.json'),
    ('integration/hyperspace_index.json', 'integration/indices/hyperspace_index.json'),
    ('integration/index_registry.yaml', 'integration/registries/index_registry.yaml'),
    ('integration/gh_upstreams.json', 'integration/upstreams/gh_upstreams.json'),
    ('integration/gh_live_registry.json', 'integration/upstreams/gh_live_registry.json'),
    ('integration/gh_coupling_state.json', 'integration/couplings/gh_coupling_state.json'),
    ('integration/hyperspace_index_orbital.json', 'integration/indices/hyperspace_index_orbital.json'),
    ('integration/index_registry_orbital.yaml', 'integration/registries/index_registry_orbital.yaml'),
)


@dataclass(frozen=True)
class MirrorSyncResult:
    pair: tuple[str, str]
    updated: bool
    reason: str


def _read_structured(path: Path) -> Any:
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.json':
        return json.loads(text)
    if path.suffix in {'.yaml', '.yml'}:
        return yaml.safe_load(text)
    raise ValueError(f'Unsupported mirror file type: {path}')


def _write_structured(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.json':
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return
    if path.suffix in {'.yaml', '.yml'}:
        path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding='utf-8')
        return
    raise ValueError(f'Unsupported mirror file type: {path}')


def _merge_values(left: Any, right: Any) -> Any:
    if isinstance(left, dict) and isinstance(right, dict):
        merged: dict[str, Any] = {}
        for key in set(left) | set(right):
            if key in left and key in right:
                merged[key] = _merge_values(left[key], right[key])
            elif key in right:
                merged[key] = right[key]
            else:
                merged[key] = left[key]
        return merged

    if isinstance(left, list) and isinstance(right, list):
        dict_lists = all(isinstance(item, dict) for item in [*left, *right])
        if dict_lists:
            for identity_field in ('id', 'key', 'path'):
                if any(identity_field in item for item in [*left, *right]):
                    merged_by_id: dict[str, Any] = {}
                    ordered_ids: list[str] = []

                    def _collect(items: list[Any]) -> None:
                        for item in items:
                            marker = str(item.get(identity_field, ''))
                            if not marker:
                                marker = json.dumps(item, ensure_ascii=False, sort_keys=True, default=str)
                            if marker not in merged_by_id:
                                ordered_ids.append(marker)
                                merged_by_id[marker] = item
                            else:
                                merged_by_id[marker] = _merge_values(merged_by_id[marker], item)

                    _collect(left)
                    _collect(right)
                    return [merged_by_id[item_id] for item_id in ordered_ids]

        merged_list: list[Any] = []
        seen: set[str] = set()
        for item in [*left, *right]:
            marker = json.dumps(item, ensure_ascii=False, sort_keys=True, default=str)
            if marker in seen:
                continue
            seen.add(marker)
            merged_list.append(item)
        return merged_list

    if right in (None, '', [], {}):
        return left
    return right


def sync_integration_mirrors(root: str | Path) -> list[MirrorSyncResult]:
    root = Path(root)
    results: list[MirrorSyncResult] = []
    for legacy_rel, target_rel in PAIR_MAPPINGS:
        legacy = root / legacy_rel
        target = root / target_rel

        if not legacy.exists() or not target.exists():
            results.append(MirrorSyncResult((legacy_rel, target_rel), updated=False, reason='missing-path'))
            continue

        legacy_payload = _read_structured(legacy)
        target_payload = _read_structured(target)
        merged = _merge_values(legacy_payload, target_payload)

        changed = merged != legacy_payload or merged != target_payload
        if changed:
            _write_structured(legacy, merged)
            _write_structured(target, merged)
            results.append(MirrorSyncResult((legacy_rel, target_rel), updated=True, reason='merged'))
        else:
            results.append(MirrorSyncResult((legacy_rel, target_rel), updated=False, reason='already-synced'))
    return results


def main() -> int:
    root = resolve_project_root(Path(__file__))
    results = sync_integration_mirrors(root)
    print(
        json.dumps(
            {
                'schema': 'ciel-sot-agent/integration-mirror-sync-report/v0.1',
                'updated_pairs': [r.pair for r in results if r.updated],
                'results': [
                    {'pair': list(r.pair), 'updated': r.updated, 'reason': r.reason}
                    for r in results
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
