from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from main.kernels.registry import KERNELS

from .omega_app import (
    BASE_DIR,
    DATA_DIR,
    FILES_DIR,
    MODELS_DIR,
    LocalChatEngine,
    _ensure_dirs,
    _load_ciel_config_from_state,
    _load_state,
    _pick_port,
)
from .orbital_cockpit import build_default_topology
from .orbital_panels import build_event_strip, build_identity_snapshot, build_navigation_sections


ANALOGIES_DIR = BASE_DIR / 'docs' / 'analogies'


def _resolve_log_path(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return DATA_DIR / p


def _read_last_jsonl(path: Path) -> Optional[dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return None
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            size = min(end, 200_000)
            f.seek(end - size)
            data = f.read(size)
        txt = data.decode('utf-8', errors='replace')
        lines = [ln for ln in txt.splitlines() if ln.strip()]
        if not lines:
            return None
        return json.loads(lines[-1])
    except Exception:
        return None


def _tail_file(path: Path, *, max_lines: int = 80, max_bytes: int = 120_000) -> str:
    if not path.exists() or not path.is_file():
        return f'File not found: {path}'
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            size = min(end, max_bytes)
            f.seek(end - size)
            data = f.read(size)
        txt = data.decode('utf-8', errors='replace')
        lines = txt.splitlines()
        if len(lines) > max_lines:
            lines = lines[-max_lines:]
        return '\n'.join(lines)
    except Exception as ex:
        return f'Error reading {path}: {ex}'


def _count_files(folder: Path, pattern: str = '*') -> int:
    try:
        return len([p for p in folder.glob(pattern) if p.is_file()])
    except Exception:
        return 0


def _read_text_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return f'File not found: {path}'
    try:
        return path.read_text(encoding='utf-8')
    except Exception as ex:
        return f'Error reading {path}: {ex}'


def _doc_path(*parts: str) -> Path:
    return BASE_DIR.joinpath(*parts)


def _education_entry(key: str) -> tuple[str, Path, str]:
    mapping = {
        'analogies': (
            'Analogies',
            ANALOGIES_DIR / 'README.md',
            'Educational analogy layer translating formal concepts into mnemonic images and teaching bridges.',
        ),
        'analogy_registry': (
            'Analogy Registry',
            ANALOGIES_DIR / 'ANALOGY_REGISTRY.md',
            'Registry mapping formal concepts to mnemonic images and limits of analogy.',
        ),
        'truth_attractor_analogies': (
            'Truth Attractor Analogies',
            ANALOGIES_DIR / 'TRUTH_ATTRACTOR_ANALOGIES.md',
            'Analogy set for truth as attractor, convergence, nodes, white threads, and false consensus.',
        ),
        'mnemonic_book': (
            'Mnemonic Book For Kids',
            ANALOGIES_DIR / 'MNEMONIC_BOOK_FOR_KIDS.md',
            'Child-safe mnemonic guide for Omega concepts and cockpit language.',
        ),
    }
    return mapping.get(
        key,
        (
            key.replace('_', ' ').title(),
            ANALOGIES_DIR / 'README.md',
            'Educational layer entry.',
        ),
    )


def _workspace_title(key: str) -> str:
    mapping = {
        'identity': 'Identity Attractor',
        'theory': 'Theory Interface',
        'operators': 'Operators',
        'constants': 'Constants',
        'constraints': 'Constraints',
        'memory_topology': 'Memory Topology',
        'execution': 'Execution',
        'kernel': 'Kernel',
        'planner': 'Planner',
        'session_dynamics': 'Session Dynamics',
        'command_routing': 'Command Routing',
        'agent': 'Agent',
        'chat': 'Chat',
        'tools': 'Tool Interface',
        'files': 'Files',
        'models': 'Models',
        'evidence': 'Evidence',
        'observability': 'Observability',
        'tests': 'Tests',
        'audit': 'Audit',
        'provenance': 'Provenance',
        'crossrefs': 'Crossrefs',
        'boundary': 'Publication Boundary',
        'analogies': 'Analogies',
        'analogy_registry': 'Analogy Registry',
        'truth_attractor_analogies': 'Truth Attractor Analogies',
        'mnemonic_book': 'Mnemonic Book For Kids',
        'settings': 'Settings',
    }
    return mapping.get(key, key.replace('_', ' ').title())


CSS = """
<style>
  :root {
    --omega-bg0: #050814;
    --omega-bg1: #0a1024;
    --omega-surface: rgba(12, 22, 51, 0.82);
    --omega-border: rgba(0, 184, 255, 0.22);
    --omega-glow: rgba(33, 212, 253, 0.16);
    --omega-primary: #00B8FF;
    --omega-accent: #2C7BFF;
    --omega-text: #EAF2FF;
    --omega-muted: rgba(234, 242, 255, 0.68);
  }

  body {
    background:
      radial-gradient(circle at 22% 10%, rgba(0, 184, 255, 0.18), transparent 46%),
      radial-gradient(circle at 78% 0%, rgba(44, 123, 255, 0.14), transparent 46%),
      linear-gradient(180deg, var(--omega-bg0), var(--omega-bg1) 60%, #03040c);
    color: var(--omega-text);
  }

  .q-card {
    background: var(--omega-surface) !important;
    border: 1px solid var(--omega-border);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.42);
  }

  .omega-title {
    letter-spacing: 0.08em;
    font-weight: 800;
    text-transform: uppercase;
    background: linear-gradient(90deg, rgba(33, 212, 253, 1), rgba(44, 123, 255, 1));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 0 22px var(--omega-glow);
  }

  .omega-badge {
    border: 1px solid var(--omega-border);
    background: rgba(5, 8, 20, 0.50);
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    color: var(--omega-muted);
  }

  .omega-muted { color: var(--omega-muted); }
</style>
"""


def main() -> int:
    try:
        from nicegui import app, ui
    except ModuleNotFoundError as e:
        raise SystemExit(
            'Missing dependency: nicegui. Install requirements to run omega_orbital_app.'
        ) from e

    assets_dir = BASE_DIR / 'main'
    if assets_dir.exists():
        app.add_static_files('/assets', str(assets_dir))

    ui.colors(
        primary='#00B8FF',
        secondary='#0C1633',
        accent='#2C7BFF',
        dark='#050814',
        info='#21D4FD',
    )
    ui.dark_mode().enable()
    ui.add_head_html(CSS)

    _ensure_dirs()
    state = _load_state()
    cfg = _load_ciel_config_from_state(state)
    engine = LocalChatEngine()
    topology = build_default_topology()
    nav_sections = build_navigation_sections(topology)

    selected: dict[str, str] = {'key': 'identity'}
    selected_label: dict[str, Optional[Any]] = {'widget': None}
    inspector_code: dict[str, Optional[Any]] = {'widget': None}
    event_labels: dict[str, Any] = {}

    def _current_log_record() -> Optional[dict[str, Any]]:
        return _read_last_jsonl(_resolve_log_path(str(cfg.log_path)))

    def _identity_snapshot() -> dict[str, Any]:
        rec = _current_log_record() or {}
        resonance = rec.get('resonance_mean')
        coherence = rec.get('resonance_mean')
        warnings: list[str] = []
        if state.get('active_model') and not Path(str(state.get('active_model'))).exists():
            warnings.append('active model path missing')
        if rec.get('ethical_ok') in (False, 0):
            warnings.append('latest runtime record reports ethical gate failure')
        return build_identity_snapshot(
            topology=topology,
            active_model=str(state.get('active_model') or '(none)'),
            active_kernel=str(state.get('active_kernel') or 'ciel0'),
            ethics_gate='blocked' if rec.get('ethical_ok') in (False, 0) else 'open',
            export_package=str(state.get('active_export') or 'local-demo-runtime'),
            publication_boundary=str(state.get('publication_boundary') or 'unspecified'),
            coherence=None if coherence is None else float(coherence),
            resonance=None if resonance is None else float(resonance),
            warnings=warnings,
        )

    def _inspector_payload() -> dict[str, Any]:
        key = selected['key']
        node = topology.get(key)
        rec = _current_log_record()
        docs = {
            'architecture': str(_doc_path('docs', 'OMEGA_COCKPIT_1_0.md')),
            'preview_guide': str(_doc_path('docs', 'ORBITAL_PREVIEW.md')),
            'docs_index': str(_doc_path('docs', 'INDEX.md')),
            'analogies_root': str(ANALOGIES_DIR / 'README.md'),
            'analogy_registry': str(ANALOGIES_DIR / 'ANALOGY_REGISTRY.md'),
            'truth_attractor_analogies': str(ANALOGIES_DIR / 'TRUTH_ATTRACTOR_ANALOGIES.md'),
            'mnemonic_book': str(ANALOGIES_DIR / 'MNEMONIC_BOOK_FOR_KIDS.md'),
        }
        payload = {
            'selected': key,
            'title': _workspace_title(key),
            'node': None if node is None else {
                'key': node.key,
                'label': node.label,
                'orbit': int(node.orbit),
                'status': node.default_status.value,
                'description': node.description,
                'children': list(node.children),
            },
            'related_threads': [
                {
                    'source': t.source,
                    'target': t.target,
                    'relation': t.relation,
                    'strength': t.strength,
                    'freshness': t.freshness,
                    'canonical_agreement': t.canonical_agreement,
                }
                for t in topology.related_threads(key)
            ],
            'source_of_truth': {
                'state_path': str(DATA_DIR / 'state.json'),
                'log_path': str(_resolve_log_path(str(cfg.log_path))),
                'models_dir': str(MODELS_DIR),
                'files_dir': str(FILES_DIR),
                'docs': docs,
            },
            'latest_record': rec,
        }
        if key in {'analogies', 'analogy_registry', 'truth_attractor_analogies', 'mnemonic_book'}:
            title, path, summary = _education_entry(key)
            payload['education'] = {
                'title': title,
                'path': str(path),
                'summary': summary,
            }
        return payload

    def _render_identity(workspace) -> None:
        snap = _identity_snapshot()
        rec = _current_log_record() or {}
        with workspace:
            ui.label('Identity Attractor').classes('text-2xl font-bold omega-title')
            ui.label('Orbital preview: the cockpit is now organized around system identity rather than peer runtime tabs.').classes('omega-muted')
            with ui.row().classes('w-full gap-4 pt-4'):
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Identity State').classes('text-base font-semibold')
                    for k in ('identity_profile', 'active_canon_export', 'active_operator_set', 'session_phase', 'publication_boundary'):
                        ui.label(f'{k}: {snap.get(k)}').classes('text-xs')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Coherence & Ethics').classes('text-base font-semibold')
                    ui.label(f"coherence: {snap.get('coherence')}").classes('text-xs')
                    ui.label(f"resonance: {snap.get('resonance')}").classes('text-xs')
                    ui.label(f"ethics_gate: {snap.get('ethics_gate')}").classes('text-xs')
                    ui.label(f"warnings: {len(snap.get('warnings') or [])}").classes('text-xs')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Runtime Anchors').classes('text-base font-semibold')
                    ui.label(f"active_model: {snap.get('active_model')}").classes('text-xs')
                    ui.label(f"active_kernel: {snap.get('active_kernel')}").classes('text-xs')
                    ui.label(f"llama_available: {'yes' if engine.can_use_llama() else 'no'}").classes('text-xs')
                    ui.label(f"model_loaded: {'yes' if engine.is_loaded() else 'no'}").classes('text-xs')
            with ui.row().classes('w-full gap-4 pt-4'):
                with ui.card().classes('w-1/2 p-4'):
                    ui.label('System Counts').classes('text-base font-semibold')
                    ui.label(f"models: {_count_files(MODELS_DIR, '*.gguf')}").classes('text-xs')
                    ui.label(f"files: {_count_files(FILES_DIR, '*')}").classes('text-xs')
                    ui.label(f"kernels: {len(KERNELS)}").classes('text-xs')
                with ui.card().classes('w-1/2 p-4'):
                    ui.label('Latest Runtime Record').classes('text-base font-semibold')
                    ui.code(json.dumps(rec, ensure_ascii=False, indent=2) if rec else 'No runtime record found').classes('w-full')

    def _render_theory_like(workspace, root_key: str) -> None:
        node = topology.get(root_key)
        with workspace:
            ui.label(_workspace_title(root_key)).classes('text-2xl font-bold omega-title')
            if node is not None:
                ui.label(node.description).classes('omega-muted')
            ui.label('Role -> Definition -> Derivation -> Implementation -> Test -> Status -> Interpretation').classes('text-xs omega-badge')
            with ui.row().classes('w-full gap-4 pt-4'):
                for child_key in (node.children if node is not None else ()): 
                    child = topology.get(child_key)
                    if child is None:
                        continue
                    with ui.card().classes('w-72 p-4'):
                        ui.label(child.label).classes('text-base font-semibold')
                        ui.label(f'status: {child.default_status.value}').classes('text-xs omega-badge')
                        ui.label(child.description).classes('text-xs')
                        ui.separator()
                        ui.label('Definition / derivation / implementation / tests are not yet bound into the preview.').classes('text-xs omega-muted')

    def _render_execution(workspace, key: str) -> None:
        rec = _current_log_record() or {}
        with workspace:
            ui.label(_workspace_title(key)).classes('text-2xl font-bold omega-title')
            ui.label('Execution is explicitly separated from theory and agent consumption.').classes('omega-muted')
            with ui.row().classes('w-full gap-4 pt-4'):
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Runtime Config').classes('text-base font-semibold')
                    ui.label(f'compute_mode: {cfg.compute_mode}').classes('text-xs')
                    ui.label(f'enable_gpu: {cfg.enable_gpu}').classes('text-xs')
                    ui.label(f'enable_numba: {cfg.enable_numba}').classes('text-xs')
                    ui.label(f'ethics_min_coherence: {cfg.ethics_min_coherence}').classes('text-xs')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Kernel Registry').classes('text-base font-semibold')
                    for name in sorted(KERNELS.keys()):
                        ui.label(name).classes('text-xs')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Latest Metrics').classes('text-base font-semibold')
                    ui.code(json.dumps(rec, ensure_ascii=False, indent=2) if rec else 'No recent record').classes('w-full')

    def _render_agent(workspace, key: str) -> None:
        with workspace:
            ui.label(_workspace_title(key)).classes('text-2xl font-bold omega-title')
            ui.label('Chat is demoted from app center to one module inside Agent.').classes('omega-muted')
            with ui.row().classes('w-full gap-4 pt-4'):
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Agent Shell').classes('text-base font-semibold')
                    ui.label(f'active_model: {state.get("active_model") or "(none)"}').classes('text-xs')
                    ui.label(f'llama_available: {"yes" if engine.can_use_llama() else "no"}').classes('text-xs')
                    ui.label(f'loaded: {"yes" if engine.is_loaded() else "no"}').classes('text-xs')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Planner / Routing').classes('text-base font-semibold')
                    ui.label('Planner UI not yet wired.').classes('text-xs omega-muted')
                    ui.label('Command routing UI not yet wired.').classes('text-xs omega-muted')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Legacy Compatibility').classes('text-base font-semibold')
                    ui.label('The classic runtime shell remains available through `ciel-omega`.').classes('text-xs')
                    ui.label('This orbital preview reorganizes the surface without deleting legacy runtime flows.').classes('text-xs')

    def _render_files_or_models(workspace, key: str) -> None:
        folder = FILES_DIR if key == 'files' else MODELS_DIR
        pattern = '*' if key == 'files' else '*.gguf'
        rows = []
        for p in sorted(folder.glob(pattern))[:20]:
            if p.is_file():
                rows.append({'name': p.name, 'size_kb': round(p.stat().st_size / 1024, 1)})
        with workspace:
            ui.label(_workspace_title(key)).classes('text-2xl font-bold omega-title')
            ui.label('This module remains available, but is no longer treated as a top-level system axis.').classes('omega-muted')
            with ui.card().classes('w-full p-4 mt-4'):
                ui.label(f'count: {_count_files(folder, pattern)}').classes('text-xs')
                ui.table(
                    columns=[
                        {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                        {'name': 'size_kb', 'label': 'KB', 'field': 'size_kb', 'align': 'right'},
                    ],
                    rows=rows,
                    row_key='name',
                ).classes('w-full')

    def _render_evidence(workspace, key: str) -> None:
        path = _resolve_log_path(str(cfg.log_path))
        with workspace:
            ui.label(_workspace_title(key)).classes('text-2xl font-bold omega-title')
            ui.label('Evidence is promoted from generic observability to a first-class epistemic surface.').classes('omega-muted')
            with ui.row().classes('w-full gap-4 pt-4'):
                with ui.card().classes('w-1/2 p-4'):
                    ui.label('Log Tail').classes('text-base font-semibold')
                    ui.code(_tail_file(path)).classes('w-full')
                with ui.card().classes('w-1/2 p-4'):
                    ui.label('Epistemic State').classes('text-base font-semibold')
                    ui.label('tests: provisional').classes('text-xs omega-badge')
                    ui.label('audit: draft').classes('text-xs omega-badge')
                    ui.label('provenance: draft').classes('text-xs omega-badge')
                    ui.label('crossrefs: draft').classes('text-xs omega-badge')

    def _render_boundary(workspace) -> None:
        with workspace:
            ui.label('Publication Boundary').classes('text-2xl font-bold omega-title')
            ui.label('Boundary state is now treated as a top-level system layer, not hidden git trivia.').classes('omega-muted')
            with ui.row().classes('w-full gap-4 pt-4'):
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Current State').classes('text-base font-semibold')
                    ui.label(f"boundary: {state.get('publication_boundary') or 'unspecified'}").classes('text-xs')
                    ui.label(f"active_export: {state.get('active_export') or 'local-demo-runtime'}").classes('text-xs')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Visibility Classes').classes('text-base font-semibold')
                    for txt in ('private-only', 'public-exported', 'runtime-only', 'draft'):
                        ui.label(txt).classes('text-xs omega-badge')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Sanitization').classes('text-base font-semibold')
                    ui.label('sanitization issues: not yet wired').classes('text-xs omega-muted')
                    ui.label('dirty manifests: not yet wired').classes('text-xs omega-muted')

    def _render_analogies(workspace, key: str) -> None:
        title, path, summary = _education_entry(key)
        content = _read_text_file(path)
        docs_rows = [
            ('root', ANALOGIES_DIR / 'README.md'),
            ('registry', ANALOGIES_DIR / 'ANALOGY_REGISTRY.md'),
            ('truth attractor', ANALOGIES_DIR / 'TRUTH_ATTRACTOR_ANALOGIES.md'),
            ('mnemonic book', ANALOGIES_DIR / 'MNEMONIC_BOOK_FOR_KIDS.md'),
        ]
        with workspace:
            ui.label(title).classes('text-2xl font-bold omega-title')
            ui.label(summary).classes('omega-muted')
            with ui.row().classes('w-full gap-4 pt-4'):
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Educational Layer').classes('text-base font-semibold')
                    ui.label('This orbit translates formal Omega concepts into mnemonic and child-safe images.').classes('text-xs')
                    ui.label('The analogy layer is secondary to formalism, but first-class for teaching and memory.').classes('text-xs')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Analogy Entry Points').classes('text-base font-semibold')
                    for label, doc_path in docs_rows:
                        ui.label(f'{label}: {doc_path}').classes('text-xs')
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Children / Beginners').classes('text-base font-semibold')
                    ui.label('truth = valley').classes('text-xs omega-badge')
                    ui.label('node = lamp').classes('text-xs omega-badge')
                    ui.label('white thread = glowing string').classes('text-xs omega-badge')
                    ui.label('cockpit = solar system').classes('text-xs omega-badge')
            with ui.card().classes('w-full p-4 mt-4'):
                ui.label('Rendered document').classes('text-base font-semibold')
                ui.markdown(content).classes('w-full')

    def _render_settings(workspace) -> None:
        with workspace:
            ui.label('Settings').classes('text-2xl font-bold omega-title')
            ui.label('Current runtime state snapshot from local demo configuration.').classes('omega-muted')
            ui.code(json.dumps(state, ensure_ascii=False, indent=2)).classes('w-full mt-4')

    def _render_workspace() -> None:
        workspace.clear()
        key = selected['key']
        if key in ('identity',):
            _render_identity(workspace)
        elif key in ('theory', 'operators', 'constants', 'constraints', 'memory_topology'):
            root = 'theory' if key != 'theory' else key
            _render_theory_like(workspace, root)
        elif key in ('execution', 'kernel', 'planner', 'session_dynamics', 'command_routing'):
            _render_execution(workspace, key)
        elif key in ('agent', 'chat', 'tools'):
            _render_agent(workspace, key)
        elif key in ('files', 'models'):
            _render_files_or_models(workspace, key)
        elif key in ('evidence', 'observability', 'tests', 'audit', 'provenance', 'crossrefs'):
            _render_evidence(workspace, key)
        elif key == 'boundary':
            _render_boundary(workspace)
        elif key in ('analogies', 'analogy_registry', 'truth_attractor_analogies', 'mnemonic_book'):
            _render_analogies(workspace, key)
        elif key == 'settings':
            _render_settings(workspace)
        else:
            with workspace:
                ui.label(_workspace_title(key)).classes('text-2xl font-bold omega-title')
                ui.label('Workspace not yet implemented.').classes('omega-muted')
        if selected_label['widget'] is not None:
            selected_label['widget'].text = _workspace_title(key)

    def _refresh_inspector() -> None:
        payload = _inspector_payload()
        if inspector_code['widget'] is not None:
            inspector_code['widget'].content = json.dumps(payload, ensure_ascii=False, indent=2)
            inspector_code['widget'].update()

    def _refresh_event_strip() -> None:
        rec = _current_log_record() or {}
        items = build_event_strip(
            active_kernel=str(state.get('active_kernel') or 'ciel0'),
            active_model=str(state.get('active_model') or '(none)'),
            export_package=str(state.get('active_export') or 'local-demo-runtime'),
            ethics_state='blocked' if rec.get('ethical_ok') in (False, 0) else 'open',
            boundary_mode=str(state.get('publication_boundary') or 'unspecified'),
            dirty_state=bool(state.get('dirty_state', False)),
            failing_tests=None,
            recent_artifact=str(state.get('recent_artifact') or '(none)'),
        )
        for item in items:
            key = item['label']
            widget = event_labels.get(key)
            if widget is not None:
                widget.text = f"{item['label']}: {item['value']}"

    def _select(key: str) -> None:
        selected['key'] = key
        _render_workspace()
        _refresh_inspector()

    ui.query('.nicegui-content').classes('p-0')

    with ui.header().classes('items-center justify-between px-4'):
        with ui.row().classes('items-center gap-3'):
            ui.image('/assets/Logo1.png').classes('h-10 w-10')
            ui.label('CIEL').classes('text-xl omega-title')
            ui.label('Ω orbital preview').classes('text-xs omega-badge')
        with ui.column().classes('items-end gap-0'):
            selected_label['widget'] = ui.label('Identity Attractor').classes('text-sm font-semibold')
            ui.label('legacy runtime preserved').classes('text-xs omega-muted')

    with ui.row().classes('w-full').style('height: calc(100vh - 118px);'):
        with ui.column().classes('w-1/5 p-4 gap-3'):
            with ui.card().classes('w-full p-3'):
                ui.label('Orbital Navigation').classes('text-base font-semibold')
                for section in nav_sections:
                    ui.label(section.title).classes('text-xs omega-badge')
                    for item in section.items:
                        ui.button(
                            f"{item['label']} [{item['status']}]",
                            on_click=lambda _, key=item['key']: _select(key),
                        ).props('flat align=left').classes('w-full justify-start text-left')
                    ui.separator()
            with ui.card().classes('w-full p-3'):
                ui.label('Auxiliary').classes('text-base font-semibold')
                ui.button('Settings', on_click=lambda: _select('settings')).props('flat align=left').classes('w-full justify-start')
                ui.label('This preview preserves the current runtime shell instead of replacing it.').classes('text-xs omega-muted pt-2')

        workspace = ui.column().classes('w-3/5 p-4 gap-3')

        with ui.column().classes('w-1/5 p-4 gap-3'):
            with ui.card().classes('w-full p-3'):
                ui.label('Inspector').classes('text-base font-semibold')
                ui.label('Source of truth, provenance, and white-thread context for the selected node.').classes('text-xs omega-muted')
                inspector_code['widget'] = ui.code('').classes('w-full')
            with ui.card().classes('w-full p-3'):
                ui.label('Mission Strip Preview').classes('text-base font-semibold')
                ui.label('Bottom strip remains the short-form live operational state.').classes('text-xs omega-muted')

    with ui.footer().classes('items-center justify-start px-4 gap-4'):
        for label in ('Kernel', 'Model', 'Export', 'Ethics', 'Boundary', 'Dirty', 'Failing tests', 'Recent artifact'):
            event_labels[label] = ui.label(f'{label}: -').classes('text-xs omega-badge')

    _render_workspace()
    _refresh_inspector()
    _refresh_event_strip()
    ui.timer(1.0, _refresh_inspector)
    ui.timer(1.0, _refresh_event_strip)

    host = os.environ.get('CIEL_HOST', '127.0.0.1')
    preferred_port = int(os.environ.get('CIEL_PORT', '8080'))
    port = _pick_port(host, preferred_port)
    if port != preferred_port:
        print(f'Port {preferred_port} is busy; using {port}', flush=True)

    for _ in range(3):
        try:
            print(f'Omega orbital preview starting on http://{host}:{port}', flush=True)
            ui.run(title='CIEL/Ω Orbital Preview', reload=False, host=host, port=port)
            break
        except OSError as ex:
            if getattr(ex, 'errno', None) != 98:
                raise
            port = _pick_port(host, int(port) + 1)
            print(f'Port busy; retry on http://{host}:{port}', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
