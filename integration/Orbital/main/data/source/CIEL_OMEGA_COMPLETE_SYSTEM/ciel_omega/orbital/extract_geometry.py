from __future__ import annotations

import ast
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict

SECTORS = ["constraints", "fields", "runtime", "memory", "bridge", "vocabulary"]
MD_LINK = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
TAU_MAP = {1: 0.263, 2: 0.353, 4: 0.489}


def _discover_repo_root(start: Path) -> Path:
    """Find the enclosing repo root for mixed snapshot layouts.

    Supported layouts:
    1. <repo>/data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/...
    2. <repo>/systems/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/...
    3. <repo>/ciel_omega/...
    """

    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
        if (candidate / "data" / "source" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega").exists():
            return candidate
        if (candidate / "systems" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega").exists():
            return candidate
        if (candidate / "ciel_omega").exists() and (candidate / "orbital").exists():
            return candidate
    return start.parents[5] if len(start.parents) > 5 else start.parent


def repo_root_from_here() -> Path:
    return _discover_repo_root(Path(__file__).resolve())


def code_root_from_repo(repo_root: Path) -> Path:
    candidates = [
        repo_root / "systems" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega",
        repo_root / "data" / "source" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega",
        repo_root / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega",
        repo_root / "ciel_omega",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not locate ciel_omega code root below {repo_root}")


def sector_root(repo_root: Path, sector: str) -> Path:
    return code_root_from_repo(repo_root) / sector


def module_name_from_path(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(["ciel_omega", *parts])


def resolve_relative_import(module_name: str, level: int, imported_module: str | None) -> str:
    parts = module_name.split('.')
    pkg = parts[:-1]
    base = pkg[: len(pkg) - level + 1] if level <= len(pkg) else []
    if imported_module:
        base.append(imported_module)
    return '.'.join([p for p in base if p])


def sector_from_module(mod: str) -> str | None:
    parts = mod.split('.')
    if len(parts) >= 2 and parts[0] == 'ciel_omega' and parts[1] in SECTORS:
        return parts[1]
    return None


def count_import_edges(repo_root: Path):
    code_root = code_root_from_repo(repo_root)
    edges: DefaultDict[tuple[str, str], int] = defaultdict(int)
    for py in code_root.rglob('*.py'):
        if '__pycache__' in py.parts:
            continue
        try:
            src_sector = py.relative_to(code_root).parts[0]
        except Exception:
            continue
        if src_sector not in SECTORS:
            continue
        module_name = module_name_from_path(code_root, py)
        try:
            tree = ast.parse(py.read_text(encoding='utf-8', errors='replace'))
        except Exception:
            continue
        for node in ast.walk(tree):
            imports: list[str] = []
            if isinstance(node, ast.Import):
                imports = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    imports = [resolve_relative_import(module_name, node.level, node.module)]
                elif node.module:
                    imports = [node.module]
            for mod in imports:
                tgt_sector = sector_from_module(mod)
                if tgt_sector and tgt_sector != src_sector:
                    pair = tuple(sorted((src_sector, tgt_sector)))
                    edges[pair] += 1
    return edges


def resolve_link(src: Path, rel: str) -> Path | None:
    rel = rel.strip()
    if rel.startswith('http://') or rel.startswith('https://') or rel.startswith('#'):
        return None
    try:
        return (src.parent / rel).resolve()
    except Exception:
        return None


def scan_mesh_links(repo_root: Path, filename: str):
    edges: DefaultDict[tuple[str, str], float] = defaultdict(float)
    code_root = code_root_from_repo(repo_root)
    for doc in code_root.rglob(filename):
        src_parts = doc.relative_to(code_root).parts
        if not src_parts:
            continue
        src_sector = src_parts[0]
        if src_sector not in SECTORS:
            continue
        text = doc.read_text(encoding='utf-8', errors='replace')
        for rel in MD_LINK.findall(text):
            dst = resolve_link(doc, rel)
            if dst is None:
                continue
            try:
                relp = dst.relative_to(code_root)
            except Exception:
                continue
            if relp.parts and relp.parts[0] in SECTORS and relp.parts[0] != src_sector:
                pair = tuple(sorted((src_sector, relp.parts[0])))
                edges[pair] += 1.0
        lower = text.lower()
        for other in SECTORS:
            if other != src_sector and other in lower:
                pair = tuple(sorted((src_sector, other)))
                edges[pair] += 0.25
    return edges


def _load_json_if_exists(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def manifest_bonus(repo_root: Path):
    """Load optional structural hints without requiring a single canonical manifest.

    The old implementation hard-failed when linkage_map.json was missing. In the
    snapshot layout used here, that manifest often does not exist. This function
    now degrades gracefully and supplements the fixed canonical bonuses with any
    available orbital/registry evidence.
    """

    edges: DefaultDict[tuple[str, str], float] = defaultdict(float)
    fixed = {
        tuple(sorted(('fields', 'constraints'))): 0.20,
        tuple(sorted(('bridge', 'constraints'))): 0.35,
        tuple(sorted(('bridge', 'memory'))): 0.30,
        tuple(sorted(('fields', 'vocabulary'))): 0.25,
        tuple(sorted(('runtime', 'memory'))): 0.20,
    }
    for pair, value in fixed.items():
        edges[pair] += value

    linkage_candidates = [
        repo_root / 'manifests' / 'linkage_map.json',
        repo_root / 'data' / 'manifests' / 'linkage_map.json',
        repo_root / 'registries' / 'canonical_dependency_tables.json',
    ]
    linkage = None
    for candidate in linkage_candidates:
        linkage = _load_json_if_exists(candidate)
        if linkage is not None:
            break
    if isinstance(linkage, dict):
        # Presence of a manifest is already evidence of stronger structure.
        edges[tuple(sorted(('bridge', 'memory')))] += 0.05
        edges[tuple(sorted(('runtime', 'memory')))] += 0.05

    orchestrator_edges = repo_root / 'registries' / 'orchestrator_graph_edges.csv'
    if orchestrator_edges.exists():
        text = orchestrator_edges.read_text(encoding='utf-8', errors='replace').lower()
        for a in SECTORS:
            for b in SECTORS:
                if a >= b:
                    continue
                hits = text.count(a) * text.count(b)
                if hits > 0:
                    edges[(a, b)] += min(0.20, 0.01 * hits)

    return edges


def compute_info_mass(repo_root: Path):
    masses = {}
    code_root = code_root_from_repo(repo_root)
    for sector in SECTORS:
        d = code_root / sector
        py_files = list(d.rglob('*.py')) if d.exists() else []
        char_count = 0
        import_count = 0
        for p in py_files:
            txt = p.read_text(encoding='utf-8', errors='replace')
            char_count += len(txt)
            import_count += txt.count('import ') + txt.count('from ')
        readmes = list(d.rglob('README.md')) if d.exists() else []
        agents = list(d.rglob('AGENT.md')) if d.exists() else []
        masses[sector] = {
            'py_files': len(py_files),
            'char_count': char_count,
            'import_count': import_count,
            'readme_count': len(readmes),
            'agent_count': len(agents),
        }
    return masses


def normalize_pair_scores(imports, readmes, agents, bonus):
    pair_scores: DefaultDict[tuple[str, str], float] = defaultdict(float)
    all_pairs = {tuple(sorted((a, b))) for i, a in enumerate(SECTORS) for b in SECTORS[i + 1 :]}
    for pair in all_pairs:
        pair_scores[pair] = 0.0
    for pair, value in imports.items():
        pair_scores[pair] += 1.0 * value
    for pair, value in readmes.items():
        pair_scores[pair] += 2.5 * value
    for pair, value in agents.items():
        pair_scores[pair] += 3.0 * value
    for pair, value in bonus.items():
        pair_scores[pair] += 5.0 * value
    max_score = max(pair_scores.values()) if pair_scores else 1.0
    weights: DefaultDict[str, dict[str, float]] = defaultdict(dict)
    for a, b in all_pairs:
        score = pair_scores[(a, b)]
        weight = 0.35 + 0.65 * (score / max_score) if score > 0 else 0.10
        weights[a][b] = round(weight, 4)
    return pair_scores, weights


def derive_sector_scalars(repo_root: Path, pair_scores, masses):
    centrality = {s: 0.0 for s in SECTORS}
    for (a, b), score in pair_scores.items():
        centrality[a] += score
        centrality[b] += score
    max_c = max(centrality.values()) if centrality else 1.0
    max_chars = max((v['char_count'] for v in masses.values()), default=1) or 1
    output = {}
    base_types = {
        'constraints': 'S',
        'fields': 'S',
        'runtime': 'F',
        'memory': 'F',
        'bridge': 'P',
        'vocabulary': 'S',
    }
    spins = {
        'constraints': 'resolve',
        'fields': 'stabilize',
        'runtime': 'run',
        'memory': 'stabilize',
        'bridge': 'route',
        'vocabulary': 'link',
    }
    phases = {
        'constraints': 0.0,
        'fields': math.pi / 3,
        'runtime': 2 * math.pi / 3,
        'memory': math.pi,
        'bridge': 4 * math.pi / 3,
        'vocabulary': 5 * math.pi / 3,
    }
    q_targets = {'constraints': 1, 'fields': 1, 'runtime': 4, 'memory': 2, 'bridge': 4, 'vocabulary': 1}
    rhythms = {'constraints': 1.0, 'fields': 1.0, 'runtime': 2.0, 'memory': 1.0, 'bridge': 2.0, 'vocabulary': 1.0}
    theta0 = {'constraints': 0.55, 'fields': 0.75, 'runtime': 1.55, 'memory': 1.05, 'bridge': 1.45, 'vocabulary': 0.7}
    for sector in SECTORS:
        c_norm = centrality[sector] / max_c if max_c else 0.0
        mass = masses[sector]
        info_mass = 0.7 + 0.7 * (mass['char_count'] / max_chars) + 0.15 * mass['readme_count'] + 0.20 * mass['agent_count']
        coherence_weight = 0.75 + 0.35 * c_norm
        amplitude = 0.75 + 0.25 * c_norm
        preference = 0.08 + 0.12 * c_norm
        damping = 0.10 + (0.04 if sector in ('runtime', 'bridge') else 0.0)
        defect = 0.02 if sector != 'bridge' else 0.03
        output[sector] = {
            'orbital_level': 2,
            'orbital_type': base_types[sector],
            'dominant_spin': spins[sector],
            'theta': round(theta0[sector], 6),
            'phi': round(phases[sector], 12),
            'rhythm_ratio': rhythms[sector],
            'amplitude': round(amplitude, 4),
            'coherence_weight': round(coherence_weight, 4),
            'info_mass': round(info_mass, 4),
            'q_target': q_targets[sector],
            'damping': round(damping, 4),
            'preference': round(preference, 4),
            'defect': round(defect, 4),
            'tau': TAU_MAP.get(q_targets[sector], 0.353),
        }
    return output, centrality


def build(repo_root: Path):
    imports = count_import_edges(repo_root)
    readmes = scan_mesh_links(repo_root, 'README.md')
    agents = scan_mesh_links(repo_root, 'AGENT.md')
    bonus = manifest_bonus(repo_root)
    masses = compute_info_mass(repo_root)
    pair_scores, weights = normalize_pair_scores(imports, readmes, agents, bonus)
    sectors, centrality = derive_sector_scalars(repo_root, pair_scores, masses)
    return {
        'imports': {f'{a}|{b}': v for (a, b), v in sorted(imports.items())},
        'readme_mesh': {f'{a}|{b}': v for (a, b), v in sorted(readmes.items())},
        'agent_mesh': {f'{a}|{b}': v for (a, b), v in sorted(agents.items())},
        'manifest_bonus': {f'{a}|{b}': round(v, 4) for (a, b), v in sorted(bonus.items())},
        'pair_scores': {f'{a}|{b}': round(v, 4) for (a, b), v in sorted(pair_scores.items())},
        'centrality': centrality,
        'masses': masses,
        'sectors': {'sectors': sectors},
        'couplings': {'couplings': weights},
    }


__all__ = [
    'SECTORS',
    'build',
    'code_root_from_repo',
    'repo_root_from_here',
    'sector_root',
]
