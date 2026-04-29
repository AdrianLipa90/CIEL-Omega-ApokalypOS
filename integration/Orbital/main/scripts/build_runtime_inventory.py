from __future__ import annotations
from pathlib import Path
import ast, csv

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
CANON = PROJECT_ROOT / 'src' / 'CIEL_OMEGA_COMPLETE_SYSTEM'
REG = ROOT / 'registries'
TOKENS = {
    'contains_phase': ['phase', 'gamma', 'berry', 'euler'],
    'contains_memory': ['memory'],
    'contains_reduction': ['reduction', 'collapse'],
    'contains_truth': ['truth'],
    'contains_holonomy': ['holonomy', 'white-thread', 'white_thread', 'aharonov', 'berry'],
    'contains_tau': ['tau'],
    'contains_registry': ['registry', 'record', 'entity'],
    'contains_constraint': ['constraint', 'euler_constraint'],
    'contains_potential': ['potential', 'lambda_0', 'lagrangian'],
    'contains_orchestrator': ['orchestrator'],
}

py_files = sorted(CANON.rglob('*.py'))
module_index: dict[str, str] = {}
for p in py_files:
    rel = p.relative_to(CANON).as_posix()
    mod = rel[:-3].replace('/', '.')
    if mod.endswith('.__init__'):
        mod = mod[:-9]
    module_index[mod] = rel

files_rows = []
func_rows = []
edge_rows = []

for p in sorted(CANON.rglob('*')):
    if not p.is_file():
        continue
    rel = p.relative_to(CANON).as_posix()
    ext = p.suffix
    try:
        txt = p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        txt = ''
    lc = txt.count('\n') + (1 if txt else 0)
    row = {
        'canonical_path': rel,
        'extension': ext,
        'size_bytes': p.stat().st_size,
        'line_count': lc,
        'py_functions': 0,
        'py_classes': 0,
        'import_in_repo_count': 0,
        'import_external_count': 0,
    }
    low = txt.lower()
    for col, toks in TOKENS.items():
        row[col] = int(any(t in low for t in toks))
    if ext == '.py':
        try:
            tree = ast.parse(txt)
            imports_in = 0
            imports_ex = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    row['py_classes'] += 1
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    row['py_functions'] += 1
                    cls = ''
                    qual = node.name
                    args = len(getattr(node.args, 'args', []))
                    decs = len(getattr(node, 'decorator_list', []))
                    seg = ast.get_source_segment(txt, node) or ''
                    ls = seg.lower()
                    returns_value = int(any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node)))
                    func_rows.append({
                        'file_path': rel,
                        'qualname': qual,
                        'function_name': node.name,
                        'class_name': cls,
                        'arg_count': args,
                        'decorator_count': decs,
                        'returns_value': returns_value,
                        'touches_state': int(any(t in ls for t in ['state', 'phase_state', 'systemstate'])),
                        'touches_memory': int('memory' in ls),
                        'touches_phase': int(any(t in ls for t in ['phase', 'gamma', 'berry', 'euler'])),
                        'touches_reduction': int(any(t in ls for t in ['reduction', 'collapse'])),
                        'touches_registry': int(any(t in ls for t in ['registry', 'entity', 'record'])),
                        'touches_io': int(any(t in ls for t in ['open(', 'read_', 'write_', 'json', 'yaml', 'sqlite', 'db'])),
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        nm = alias.name
                        if nm in module_index:
                            imports_in += 1
                            edge_rows.append({'src': rel, 'dst': module_index[nm], 'edge_type': 'import'})
                        else:
                            imports_ex += 1
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ''
                    if node.level:
                        imports_in += 1
                    elif mod in module_index:
                        imports_in += 1
                        edge_rows.append({'src': rel, 'dst': module_index[mod], 'edge_type': 'import'})
                    else:
                        imports_ex += 1
            row['import_in_repo_count'] = imports_in
            row['import_external_count'] = imports_ex
        except Exception:
            pass
    files_rows.append(row)

REG.mkdir(exist_ok=True)
with open(REG/'runtime_files.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(files_rows[0].keys()))
    w.writeheader(); w.writerows(files_rows)
with open(REG/'runtime_functions.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = list(func_rows[0].keys()) if func_rows else ['file_path']
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader(); w.writerows(func_rows)
with open(REG/'orchestrator_graph_edges.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['src', 'dst', 'edge_type'])
    w.writeheader(); w.writerows(edge_rows)
print('runtime_files', len(files_rows))
print('runtime_functions', len(func_rows))
print('graph_edges', len(edge_rows))
