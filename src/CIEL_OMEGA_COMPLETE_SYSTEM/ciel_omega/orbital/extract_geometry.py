
from __future__ import annotations
import ast, json, math, re
from pathlib import Path
from collections import defaultdict

SECTORS = ["constraints","fields","runtime","memory","bridge","vocabulary"]


def sector_root(repo_root: Path, sector: str) -> Path:
    return repo_root / "systems" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega" / sector


def module_name_from_path(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(["ciel_omega", *parts])


def resolve_relative_import(module_name: str, level: int, imported_module: str | None) -> str:
    parts = module_name.split('.')
    pkg = parts[:-1]
    if level > len(pkg):
        base = []
    else:
        base = pkg[:len(pkg)-level+1]
    if imported_module:
        base.append(imported_module)
    return '.'.join([p for p in base if p])


def sector_from_module(mod: str) -> str | None:
    parts = mod.split('.')
    if len(parts) >= 2 and parts[0] == 'ciel_omega' and parts[1] in SECTORS:
        return parts[1]
    return None


def count_import_edges(repo_root: Path):
    code_root = repo_root / 'systems' / 'CIEL_OMEGA_COMPLETE_SYSTEM' / 'ciel_omega'
    edges = defaultdict(int)
    for py in code_root.rglob('*.py'):
        if '__pycache__' in py.parts:
            continue
        src_sector = None
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
            imports = []
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


def resolve_link(src: Path, rel: str) -> Path | None:
    rel = rel.strip()
    if rel.startswith('http://') or rel.startswith('https://') or rel.startswith('#'):
        return None
    try:
        return (src.parent / rel).resolve()
    except Exception:
        return None


def scan_mesh_links(repo_root: Path, filename: str):
    edges = defaultdict(int)
    code_root = repo_root / 'systems' / 'CIEL_OMEGA_COMPLETE_SYSTEM' / 'ciel_omega'
    for doc in code_root.rglob(filename):
        src_parts = doc.relative_to(code_root).parts
        if not src_parts:
            continue
        src_sector = src_parts[0]
        if src_sector not in SECTORS:
            continue
        text = doc.read_text(encoding='utf-8', errors='replace')
        # explicit markdown links
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
        # fallback name mentions
        lower = text.lower()
        for other in SECTORS:
            if other != src_sector and other in lower:
                pair = tuple(sorted((src_sector, other)))
                edges[pair] += 0.25
    return edges


def manifest_bonus(repo_root: Path):
    edges = defaultdict(float)
    linkage = json.loads((repo_root/'manifests'/'linkage_map.json').read_text(encoding='utf-8'))
    # Known canonical bindings
    edges[tuple(sorted(('fields','constraints')))] += 0.20  # I0 and formal primitive interplay
    edges[tuple(sorted(('bridge','constraints')))] += 0.35  # Euler closure in bridge
    edges[tuple(sorted(('bridge','memory')))] += 0.30       # white-thread + memory_core
    edges[tuple(sorted(('fields','vocabulary')))] += 0.25   # symbolic names for fields
    edges[tuple(sorted(('runtime','memory')))] += 0.20      # runtime/memory reference in architecture
    return edges


def compute_info_mass(repo_root: Path):
    masses = {}
    code_root = repo_root / 'systems' / 'CIEL_OMEGA_COMPLETE_SYSTEM' / 'ciel_omega'
    for s in SECTORS:
        d = code_root / s
        py_files = list(d.rglob('*.py'))
        char_count = 0
        import_count = 0
        for p in py_files:
            txt = p.read_text(encoding='utf-8', errors='replace')
            char_count += len(txt)
            import_count += txt.count('import ') + txt.count('from ')
        readmes = list(d.rglob('README.md'))
        agents = list(d.rglob('AGENT.md'))
        masses[s] = {
            'py_files': len(py_files),
            'char_count': char_count,
            'import_count': import_count,
            'readme_count': len(readmes),
            'agent_count': len(agents),
        }
    return masses


def normalize_pair_scores(imports, readmes, agents, bonus):
    pair_scores = defaultdict(float)
    all_pairs = {tuple(sorted((a,b))) for i,a in enumerate(SECTORS) for b in SECTORS[i+1:]}
    for p in all_pairs:
        pair_scores[p] = 0.0
    for p,v in imports.items(): pair_scores[p] += 1.0 * v
    for p,v in readmes.items(): pair_scores[p] += 2.5 * v
    for p,v in agents.items(): pair_scores[p] += 3.0 * v
    for p,v in bonus.items(): pair_scores[p] += 5.0 * v
    max_score = max(pair_scores.values()) if pair_scores else 1.0
    weights = defaultdict(dict)
    for a,b in all_pairs:
        score = pair_scores[(a,b)]
        w = 0.35 + 0.65*(score/max_score) if score > 0 else 0.10
        weights[a][b] = round(w, 4)
    return pair_scores, weights


def derive_sector_scalars(repo_root: Path, pair_scores, masses):
    # centrality from pair scores
    centrality = {s:0.0 for s in SECTORS}
    for (a,b),score in pair_scores.items():
        centrality[a] += score
        centrality[b] += score
    max_c = max(centrality.values()) if centrality else 1.0
    max_chars = max((v['char_count'] for v in masses.values()), default=1) or 1
    output = {}
    base_types = {
        'constraints':'S','fields':'S','runtime':'F','memory':'F','bridge':'P','vocabulary':'S'
    }
    spins = {
        'constraints':'resolve','fields':'stabilize','runtime':'run','memory':'stabilize','bridge':'route','vocabulary':'link'
    }
    phases = {
        'constraints':0.0,
        'fields':math.pi/3,
        'runtime':2*math.pi/3,
        'memory':math.pi,
        'bridge':4*math.pi/3,
        'vocabulary':5*math.pi/3,
    }
    q_targets = {'constraints':1,'fields':1,'runtime':4,'memory':2,'bridge':4,'vocabulary':1}
    rhythms = {'constraints':1.0,'fields':1.0,'runtime':2.0,'memory':1.0,'bridge':2.0,'vocabulary':1.0}
    # initial theta anchors
    theta0 = {'constraints':0.55,'fields':0.75,'runtime':1.55,'memory':1.05,'bridge':1.45,'vocabulary':0.7}
    for s in SECTORS:
        c_norm = centrality[s]/max_c if max_c else 0.0
        m = masses[s]
        info_mass = 0.7 + 0.7*(m['char_count']/max_chars) + 0.15*m['readme_count'] + 0.20*m['agent_count']
        coherence_weight = 0.75 + 0.35*c_norm
        amplitude = 0.75 + 0.25*c_norm
        preference = 0.08 + 0.12*c_norm
        damping = 0.10 + (0.04 if s in ('runtime','bridge') else 0.0)
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


def build(repo_root: Path):
    imports = count_import_edges(repo_root)
    readmes = scan_mesh_links(repo_root, 'README.md')
    agents = scan_mesh_links(repo_root, 'AGENT.md')
    bonus = manifest_bonus(repo_root)
    masses = compute_info_mass(repo_root)
    pair_scores, weights = normalize_pair_scores(imports, readmes, agents, bonus)
    sectors, centrality = derive_sector_scalars(repo_root, pair_scores, masses)
    return {
        'imports': {f'{a}|{b}': v for (a,b),v in sorted(imports.items())},
        'readme_mesh': {f'{a}|{b}': v for (a,b),v in sorted(readmes.items())},
        'agent_mesh': {f'{a}|{b}': v for (a,b),v in sorted(agents.items())},
        'manifest_bonus': {f'{a}|{b}': v for (a,b),v in sorted(bonus.items())},
        'pair_scores': {f'{a}|{b}': round(v,4) for (a,b),v in sorted(pair_scores.items())},
        'sector_centrality': centrality,
        'sector_masses_raw': masses,
        'sectors': {'sectors': sectors},
        'couplings': {'couplings': weights},
    }


def _noop_main():
    repo_root = Path(__file__).resolve().parents[2]
    payload = build(repo_root)
    out_dir = Path(__file__).resolve().parent / 'results'
    out_dir.mkdir(exist_ok=True)
    (out_dir/'real_geometry_extraction.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    (Path(__file__).resolve().parent/'config'/'sectors_real.json').write_text(json.dumps(payload['sectors'], indent=2), encoding='utf-8')
    (Path(__file__).resolve().parent/'config'/'couplings_real.json').write_text(json.dumps(payload['couplings'], indent=2), encoding='utf-8')
    print(out_dir/'real_geometry_extraction.json')

TAU_MAP = {1: 0.263, 2: 0.353, 4: 0.489}

def build(repo_root: Path):
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
        'imports': {f'{a}|{b}': v for (a,b),v in sorted(imports.items())},
        'readme_mesh': {f'{a}|{b}': v for (a,b),v in sorted(readmes.items())},
        'agent_mesh': {f'{a}|{b}': v for (a,b),v in sorted(agents.items())},
        'manifest_bonus': {f'{a}|{b}': v for (a,b),v in sorted(bonus.items())},
        'pair_scores': {f'{a}|{b}': v for (a,b),v in sorted(pair_scores.items())},
        'centrality': centrality,
        'masses': masses,
        'sectors': {'sectors': sectors},
        'couplings': {'couplings': weights},
    }

def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[4]
