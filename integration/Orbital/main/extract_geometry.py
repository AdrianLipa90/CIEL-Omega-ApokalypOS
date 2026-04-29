from __future__ import annotations
import ast
import json
import math
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional

SECTORS = ["constraints", "fields", "runtime", "memory", "bridge", "vocabulary"]

DEFAULT_SECTORS = {
    'constraints': {
        'orbital_level': 1,
        'orbital_type': 'constraint',
        'dominant_spin': 'up',
        'theta': 0.52,
        'phi': 0.00,
        'rhythm_ratio': 1.00,
        'amplitude': 0.55,
        'coherence_weight': 1.00,
        'info_mass': 1.00,
        'q_target': 1,
        'damping': 0.18,
        'preference': 0.85,
    },
    'fields': {
        'orbital_level': 2,
        'orbital_type': 'field',
        'dominant_spin': 'up',
        'theta': 0.90,
        'phi': 0.60,
        'rhythm_ratio': 1.08,
        'amplitude': 0.62,
        'coherence_weight': 0.92,
        'info_mass': 0.95,
        'q_target': 2,
        'damping': 0.17,
        'preference': 0.78,
    },
    'runtime': {
        'orbital_level': 2,
        'orbital_type': 'runtime',
        'dominant_spin': 'up',
        'theta': 1.05,
        'phi': 1.25,
        'rhythm_ratio': 1.12,
        'amplitude': 0.68,
        'coherence_weight': 0.96,
        'info_mass': 0.98,
        'q_target': 2,
        'damping': 0.16,
        'preference': 0.82,
    },
    'memory': {
        'orbital_level': 4,
        'orbital_type': 'memory',
        'dominant_spin': 'down',
        'theta': 1.75,
        'phi': 2.10,
        'rhythm_ratio': 0.94,
        'amplitude': 0.74,
        'coherence_weight': 0.90,
        'info_mass': 1.02,
        'q_target': 4,
        'damping': 0.19,
        'preference': 0.76,
    },
    'bridge': {
        'orbital_level': 2,
        'orbital_type': 'bridge',
        'dominant_spin': 'up',
        'theta': 1.18,
        'phi': 2.80,
        'rhythm_ratio': 1.03,
        'amplitude': 0.60,
        'coherence_weight': 0.88,
        'info_mass': 0.86,
        'q_target': 2,
        'damping': 0.18,
        'preference': 0.74,
    },
    'vocabulary': {
        'orbital_level': 1,
        'orbital_type': 'semantic',
        'dominant_spin': 'down',
        'theta': 0.70,
        'phi': 3.60,
        'rhythm_ratio': 0.98,
        'amplitude': 0.52,
        'coherence_weight': 0.84,
        'info_mass': 0.80,
        'q_target': 1,
        'damping': 0.20,
        'preference': 0.70,
    },
}

DEFAULT_COUPLINGS = {
    'constraints': {'fields': 0.92, 'runtime': 0.95, 'memory': 0.70, 'bridge': 0.82, 'vocabulary': 0.76},
    'fields': {'runtime': 0.88, 'memory': 0.72, 'bridge': 0.79, 'vocabulary': 0.68},
    'runtime': {'memory': 0.80, 'bridge': 0.90, 'vocabulary': 0.66},
    'memory': {'bridge': 0.71, 'vocabulary': 0.78},
    'bridge': {'vocabulary': 0.74},
}

TAU_MAP = {1: 0.263, 2: 0.353, 4: 0.489}


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parent


def _find_ciel_omega_root(repo_root: Path) -> Optional[Path]:
    candidates = [
        repo_root / 'src' / 'CIEL_OMEGA_COMPLETE_SYSTEM' / 'ciel_omega',
        repo_root / 'data' / 'source' / 'CIEL_OMEGA_COMPLETE_SYSTEM' / 'ciel_omega',
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return None


def sector_root(repo_root: Path, sector: str) -> Path:
    omega = _find_ciel_omega_root(repo_root)
    if omega is not None:
        return omega / sector
    return repo_root / 'src' / 'CIEL_OMEGA_COMPLETE_SYSTEM' / 'ciel_omega' / sector


def module_name_from_path(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(["ciel_omega", *parts])


def resolve_relative_import(module_name: str, level: int, imported_module: Optional[str]) -> str:
    parts = module_name.split('.')
    pkg = parts[:-1]
    if level > len(pkg):
        base = []
    else:
        base = pkg[:len(pkg) - level + 1]
    if imported_module:
        base.append(imported_module)
    return '.'.join([p for p in base if p])


def sector_from_module(mod: str) -> Optional[str]:
    parts = mod.split('.')
    if len(parts) >= 2 and parts[0] == 'ciel_omega' and parts[1] in SECTORS:
        return parts[1]
    return None


def count_import_edges(repo_root: Path):
    omega = _find_ciel_omega_root(repo_root)
    if omega is None:
        return defaultdict(int)
    code_root = omega
    edges: defaultdict[tuple[str, str], int] = defaultdict(int)
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


MD_LINK = re.compile(r'\[[^\]]+\]\(([^)]+)\)')


def resolve_link(src: Path, rel: str) -> Optional[Path]:
    rel = rel.strip()
    if rel.startswith('http://') or rel.startswith('https://') or rel.startswith('#'):
        return None
    try:
        return (src.parent / rel).resolve()
    except Exception:
        return None


def scan_mesh_links(repo_root: Path, filename: str):
    edges: defaultdict[tuple[str, str], float] = defaultdict(float)
    omega = _find_ciel_omega_root(repo_root)
    if omega is None:
        return edges
    code_root = omega
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
                edges[pair] += 1
        lower = text.lower()
        for other in SECTORS:
            if other != src_sector and other in lower:
                pair = tuple(sorted((src_sector, other)))
                edges[pair] += 0.25
    return edges


def manifest_bonus(repo_root: Path):
    edges: defaultdict[tuple[str, str], float] = defaultdict(float)
    linkage_path = repo_root / 'manifests' / 'linkage_map.json'
    if linkage_path.exists():
        try:
            json.loads(linkage_path.read_text(encoding='utf-8'))
        except Exception:
            pass
    edges[tuple(sorted(('fields', 'constraints')))] += 0.20
    edges[tuple(sorted(('bridge', 'constraints')))] += 0.35
    edges[tuple(sorted(('bridge', 'memory')))] += 0.30
    edges[tuple(sorted(('fields', 'vocabulary')))] += 0.25
    edges[tuple(sorted(('runtime', 'memory')))] += 0.20
    return edges


def compute_info_mass(repo_root: Path):
    masses = {}
    omega = _find_ciel_omega_root(repo_root)
    if omega is None:
        for s in SECTORS:
            masses[s] = {'py_files': 0, 'char_count': 0, 'import_count': 0,
                         'readme_count': 0, 'agent_count': 0}
        return masses
    code_root = omega
    for s in SECTORS:
        d = code_root / s
        py_files = list(d.rglob('*.py')) if d.exists() else []
        char_count = 0
        import_count = 0
        for p in py_files:
            txt = p.read_text(encoding='utf-8', errors='replace')
            char_count += len(txt)
            import_count += txt.count('import ') + txt.count('from ')
        readmes = list(d.rglob('README.md')) if d.exists() else []
        agents = list(d.rglob('AGENT.md')) if d.exists() else []
        masses[s] = {
            'py_files': len(py_files),
            'char_count': char_count,
            'import_count': import_count,
            'readme_count': len(readmes),
            'agent_count': len(agents),
        }
    return masses


def normalize_pair_scores(imports, readmes, agents, bonus):
    pair_scores: defaultdict[tuple[str, str], float] = defaultdict(float)
    all_pairs = {tuple(sorted((a, b))) for i, a in enumerate(SECTORS) for b in SECTORS[i + 1:]}
    for p in all_pairs:
        pair_scores[p] = 0.0
    for p, v in imports.items():
        pair_scores[p] += 1.0 * v
    for p, v in readmes.items():
        pair_scores[p] += 2.5 * v
    for p, v in agents.items():
        pair_scores[p] += 3.0 * v
    for p, v in bonus.items():
        pair_scores[p] += 5.0 * v
    max_score = max(pair_scores.values()) if pair_scores else 1.0
    weights: defaultdict[str, dict[str, float]] = defaultdict(dict)
    for a, b in all_pairs:
        score = pair_scores[(a, b)]
        w = 0.35 + 0.65 * (score / max_score) if score > 0 else 0.10
        weights[a][b] = round(w, 4)
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
        'constraints': 'S', 'fields': 'S', 'runtime': 'F',
        'memory': 'F', 'bridge': 'P', 'vocabulary': 'S',
    }
    spins = {
        'constraints': 'resolve', 'fields': 'stabilize', 'runtime': 'run',
        'memory': 'stabilize', 'bridge': 'route', 'vocabulary': 'link',
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
    for s in SECTORS:
        c_norm = centrality[s] / max_c if max_c else 0.0
        m = masses[s]
        info_mass = 0.7 + 0.7 * (m['char_count'] / max_chars) + 0.15 * m['readme_count'] + 0.20 * m['agent_count']
        coherence_weight = 0.75 + 0.35 * c_norm
        amplitude = 0.75 + 0.25 * c_norm
        preference = 0.08 + 0.12 * c_norm
        damping = 0.10 + (0.04 if s in ('runtime', 'bridge') else 0.0)
        defect = 0.02 if s != 'bridge' else 0.03
        output[s] = {
            'orbital_level': 2,
            'orbital_type': base_types[s],
            'dominant_spin': spins[s],
            'theta': round(theta0[s], 6),
            'phi': round(phases[s], 12),
            'rhythm_ratio': rhythms[s],
            'amplitude': round(amplitude, 4),
            'coherence_weight': round(coherence_weight, 4),
            'info_mass': round(info_mass, 4),
            'q_target': q_targets[s],
            'damping': round(damping, 4),
            'preference': round(preference, 4),
            'defect': round(defect, 4),
        }
    return output, centrality


def _manifests_dir(repo_root: Path) -> Path:
    return repo_root / 'manifests'


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def _build_from_manifests(repo_root: Path) -> dict:
    manifests_dir = _manifests_dir(repo_root)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    sectors_path = manifests_dir / 'sectors_global.json'
    couplings_path = manifests_dir / 'couplings_global.json'

    sectors_data = _load_json(sectors_path)
    couplings_data = _load_json(couplings_path)

    sectors = sectors_data if sectors_data and 'sectors' in sectors_data else {'sectors': DEFAULT_SECTORS}
    couplings = couplings_data if couplings_data and 'couplings' in couplings_data else {'couplings': DEFAULT_COUPLINGS}

    return {
        'repo_root': str(repo_root),
        'geometry_source': 'manifests' if sectors_data and couplings_data else 'default_minimal_geometry',
        'sectors': sectors,
        'couplings': couplings,
    }


def build(repo_root: Path) -> dict:
    omega = _find_ciel_omega_root(repo_root)
    if omega is None:
        return _build_from_manifests(repo_root)

    imports = count_import_edges(repo_root)
    readmes = scan_mesh_links(repo_root, 'README.md')
    agents = scan_mesh_links(repo_root, 'AGENT.md')
    bonus = manifest_bonus(repo_root)
    masses = compute_info_mass(repo_root)
    pair_scores, weights = normalize_pair_scores(imports, readmes, agents, bonus)
    sectors, centrality = derive_sector_scalars(repo_root, pair_scores, masses)
    for name, sec in sectors.items():
        sec['tau'] = TAU_MAP.get(sec['q_target'], 0.353)
    return {
        'imports': {f'{a}|{b}': v for (a, b), v in sorted(imports.items())},
        'readme_mesh': {f'{a}|{b}': v for (a, b), v in sorted(readmes.items())},
        'agent_mesh': {f'{a}|{b}': v for (a, b), v in sorted(agents.items())},
        'manifest_bonus': {f'{a}|{b}': v for (a, b), v in sorted(bonus.items())},
        'pair_scores': {f'{a}|{b}': v for (a, b), v in sorted(pair_scores.items())},
        'centrality': centrality,
        'masses': masses,
        'sectors': {'sectors': sectors},
        'couplings': {'couplings': weights},
    }
