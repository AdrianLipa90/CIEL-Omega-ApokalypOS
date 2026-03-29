#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def sanitize_identifier(text: str) -> str:
    out = []
    for ch in text:
        if ch.isalnum() or ch == '_':
            out.append(ch)
        else:
            out.append('_')
    s = ''.join(out).strip('_')
    return s or 'unnamed'


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def export_from_orbital_registry(reg: dict, edges: dict) -> list[str]:
    lines: list[str] = []
    lines.append('# NOEMA export generated from canonical SOT orbital registry')
    lines.append('')
    for rec in reg.get('records', []):
        ident = sanitize_identifier(rec.get('id', ''))
        path = rec.get('path', '')
        role = rec.get('semantic_role', 'unresolved')
        orbit = rec.get('orbital_role', 'UNRESOLVED')
        confidence = rec.get('orbital_confidence', 0.0)
        lines.append(f'object {ident}')
        lines.append(f'  path = "{path}"')
        lines.append(f'  role = "{role}"')
        lines.append(f'  orbit = "{orbit}"')
        lines.append(f'  confidence = {confidence}')
        lines.append('end')
        lines.append('')
    for e in edges.get('edges', []):
        src = sanitize_identifier(e.get('source', ''))
        dst = sanitize_identifier(e.get('target', ''))
        rel = e.get('relation', 'links')
        weight = e.get('weight', 0.0)
        lines.append(f'link {src} -> {dst}')
        lines.append(f'  relation = "{rel}"')
        lines.append(f'  weight = {weight}')
        lines.append('end')
        lines.append('')
    return lines


def export_from_contract_concordance(concordance: dict) -> list[str]:
    lines: list[str] = []
    lines.append('# NOEMA export seed generated from canonical contract concordance')
    lines.append('')
    lines.append('object packet_schema')
    lines.append(f'  value = "{concordance.get("packet_schema", "unknown")}"')
    lines.append('  role = "canonical-packet-envelope"')
    lines.append('end')
    lines.append('')
    for key, meta in concordance.get('concordance', {}).items():
        ident = sanitize_identifier(key)
        lines.append(f'object {ident}')
        lines.append(f'  canonical = "{meta.get("canonical", "")}"')
        lines.append(f'  shell_mapping = "{meta.get("shell_mapping", "")}"')
        lines.append(f'  noema_projection = "{meta.get("noema_projection", "")}"')
        lines.append('end')
        lines.append('')
        lines.append(f'link packet_schema -> {ident}')
        lines.append('  relation = "projects"')
        lines.append('  weight = 0.61')
        lines.append('end')
        lines.append('')
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    reg_path = repo_root / 'integration' / 'registries' / 'definitions' / 'orbital_definition_registry.json'
    edge_path = repo_root / 'integration' / 'registries' / 'definitions' / 'nonlocal_definition_edges.json'
    concordance_path = repo_root / 'integration' / 'imports' / 'noema_sapiens_orbital' / 'CONTRACT_CONCORDANCE.json'

    reg = load_json(reg_path, {'records': []})
    edges = load_json(edge_path, {'edges': []})
    concordance = load_json(concordance_path, {})

    if reg.get('records'):
        lines = export_from_orbital_registry(reg, edges)
        mode = 'orbital_registry'
    else:
        lines = export_from_contract_concordance(concordance)
        mode = 'contract_concordance_fallback'

    out_dir = repo_root / 'integration' / 'imports' / 'noema_sapiens_orbital' / 'generated'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'registry_export.noema'
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'ok': True, 'mode': mode, 'output': str(out_path), 'objects': len(lines)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
