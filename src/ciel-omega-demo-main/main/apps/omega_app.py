from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Any, Optional

import psutil
import requests

from main.core.ciel_constants import DEFAULT_CONSTANTS
from main.core.config import CielConfig
from main.core.hooks import attach_ethics_and_logging
from main.kernels.registry import KERNELS
from main.apps.model_catalog import MODEL_CATALOG


BASE_DIR = Path(__file__).resolve().parents[2]


def _default_data_dir() -> Path:
    override = os.environ.get('CIEL_DATA_DIR')
    if override:
        return Path(override).expanduser().resolve()

    return (Path.home() / '.ciel' / 'ciel_omega_data').expanduser()


DATA_DIR = _default_data_dir()
FILES_DIR = DATA_DIR / 'files'
MODELS_DIR = DATA_DIR / 'models'
STATE_PATH = DATA_DIR / 'state.json'

MAX_UPLOAD_MB = int(os.environ.get('CIEL_MAX_UPLOAD_MB', '4096'))
MAX_DOWNLOAD_MB = int(os.environ.get('CIEL_MAX_DOWNLOAD_MB', '8192'))


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(name: str) -> str:
    name = name.strip().replace('\x00', '')
    name = name.replace('..', '.')
    name = name.replace('/', '_').replace('\\', '_')
    if not name:
        return 'file'
    return name


def _read_text_file(path: Path, limit_chars: int = 400_000) -> str:
    data = path.read_text(encoding='utf-8', errors='replace')
    if len(data) > limit_chars:
        return data[:limit_chars] + '\n\n[...truncated...]'
    return data


def _pick_port(host: str, preferred_port: int) -> int:
    for p in range(int(preferred_port), int(preferred_port) + 21):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((host, int(p)))
                return int(p)
        except Exception:
            continue

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, 0))
        return int(s.getsockname()[1])


def _read_pdf_text(path: Path, limit_chars: int = 400_000) -> str:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError:
        return 'Missing dependency: pypdf. Install requirements to preview PDF files.'

    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        txt = page.extract_text() or ''
        parts.append(txt)
        if sum(len(p) for p in parts) > limit_chars:
            break
    data = '\n\n'.join(parts)
    if len(data) > limit_chars:
        return data[:limit_chars] + '\n\n[...truncated...]'
    return data


def _read_docx_text(path: Path, limit_chars: int = 400_000) -> str:
    try:
        from docx import Document as DocxDocument
    except ModuleNotFoundError:
        return 'Missing dependency: python-docx. Install requirements to preview DOCX files.'

    doc = DocxDocument(str(path))
    parts: list[str] = []
    for p in doc.paragraphs:
        parts.append(p.text)
        if sum(len(x) for x in parts) > limit_chars:
            break
    data = '\n'.join(parts)
    if len(data) > limit_chars:
        return data[:limit_chars] + '\n\n[...truncated...]'
    return data


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {
            'models': [],
            'active_model': None,
            'llama_settings': {
                'n_ctx': 2048,
                'n_threads': None,
                'n_gpu_layers': 0,
                'temperature': 0.7,
                'top_p': 0.95,
                'max_tokens': 256,
                'repeat_penalty': 1.1,
            },
        }
    try:
        return json.loads(STATE_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {
            'models': [],
            'active_model': None,
            'llama_settings': {
                'n_ctx': 2048,
                'n_threads': None,
                'n_gpu_layers': 0,
                'temperature': 0.7,
                'top_p': 0.95,
                'max_tokens': 256,
                'repeat_penalty': 1.1,
            },
        }


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def _load_ciel_config_from_state(state: dict[str, Any]) -> CielConfig:
    raw = state.get('ciel_config')
    if not isinstance(raw, dict):
        raw = {}
    return CielConfig(
        enable_gpu=bool(raw.get('enable_gpu', True)),
        enable_numba=bool(raw.get('enable_numba', True)),
        compute_mode=str(raw.get('compute_mode', 'fft')),
        log_path=str(raw.get('log_path', 'logs/reality.jsonl')),
        ethics_min_coherence=float(raw.get('ethics_min_coherence', 0.4)),
        ethics_block_on_violation=bool(raw.get('ethics_block_on_violation', True)),
        dataset_path=None if raw.get('dataset_path') in (None, '') else str(raw.get('dataset_path')),
    )


def _write_ciel_config_to_state(state: dict[str, Any], cfg: CielConfig) -> None:
    state['ciel_config'] = {
        'enable_gpu': bool(cfg.enable_gpu),
        'enable_numba': bool(cfg.enable_numba),
        'compute_mode': str(cfg.compute_mode),
        'log_path': str(cfg.log_path),
        'ethics_min_coherence': float(cfg.ethics_min_coherence),
        'ethics_block_on_violation': bool(cfg.ethics_block_on_violation),
        'dataset_path': None if cfg.dataset_path in (None, '') else str(cfg.dataset_path),
    }


@dataclass
class ModelEntry:
    name: str
    path: str


class LocalChatEngine:
    def __init__(self) -> None:
        self._llama = None
        self._model_path: Optional[str] = None
        self._settings: dict[str, Any] = {}

    def can_use_llama(self) -> bool:
        try:
            import llama_cpp  # noqa: F401

            return True
        except Exception:
            return False

    def is_loaded(self) -> bool:
        return self._llama is not None

    def load(
        self,
        model_path: str,
        *,
        n_ctx: int = 2048,
        n_threads: Optional[int] = None,
        n_gpu_layers: int = 0,
        temperature: float = 0.7,
        top_p: float = 0.95,
        max_tokens: int = 256,
        repeat_penalty: float = 1.1,
    ) -> None:
        from llama_cpp import Llama

        if n_threads is None:
            n_threads = int(os.cpu_count() or 4)
        self._settings = {
            'n_ctx': int(n_ctx),
            'n_threads': int(n_threads),
            'n_gpu_layers': int(n_gpu_layers),
            'temperature': float(temperature),
            'top_p': float(top_p),
            'max_tokens': int(max_tokens),
            'repeat_penalty': float(repeat_penalty),
        }
        self._llama = Llama(
            model_path=model_path,
            n_ctx=int(n_ctx),
            n_threads=int(n_threads),
            n_gpu_layers=int(n_gpu_layers),
        )
        self._model_path = model_path

    def unload(self) -> None:
        self._llama = None
        self._model_path = None

    async def chat(self, user_text: str, history: list[dict[str, str]]) -> str:
        if self._llama is None:
            return (
                'Nie mam jeszcze załadowanego modelu GGUF.\n'
                'Wejdź w zakładkę Models, pobierz/wybierz model i kliknij Load.\n\n'
                f'Twoja wiadomość: {user_text}'
            )

        messages: list[dict[str, str]] = []
        for m in history[-30:]:
            if m.get('role') in ('user', 'assistant'):
                messages.append({'role': m['role'], 'content': m.get('content', '')})
        messages.append({'role': 'user', 'content': user_text})

        def _run() -> str:
            try:
                temperature = float(self._settings.get('temperature', 0.7))
                top_p = float(self._settings.get('top_p', 0.95))
                max_tokens = int(self._settings.get('max_tokens', 256))
                repeat_penalty = float(self._settings.get('repeat_penalty', 1.1))
                result = self._llama.create_chat_completion(
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                    repeat_penalty=repeat_penalty,
                )
                return result['choices'][0]['message']['content']
            except Exception as e:
                return f'[LLM error] {e}'

        return await asyncio.to_thread(_run)


@dataclass
class DownloadTask:
    url: str
    dest: Path
    total: Optional[int] = None
    done: bool = False
    error: Optional[str] = None


def _download_to_file(task: DownloadTask) -> None:
    try:
        with requests.get(task.url, stream=True, timeout=30) as r:
            r.raise_for_status()
            cl = r.headers.get('content-length')
            if cl is not None:
                try:
                    task.total = int(cl)
                except Exception:
                    task.total = None

            max_bytes = int(MAX_DOWNLOAD_MB) * 1024 * 1024
            if task.total is not None and task.total > max_bytes:
                raise RuntimeError(f'download too large (>{MAX_DOWNLOAD_MB} MB)')
            tmp = task.dest.with_suffix(task.dest.suffix + '.part')
            with open(tmp, 'wb') as f:
                written = 0
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    written += len(chunk)
                    if written > max_bytes:
                        raise RuntimeError(f'download too large (>{MAX_DOWNLOAD_MB} MB)')
                    f.write(chunk)
            tmp.replace(task.dest)
        task.done = True
    except Exception as e:
        task.error = str(e)
        task.done = True


def _list_files(folder: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in sorted(folder.glob('*')):
        if not p.is_file():
            continue
        st = p.stat()
        rows.append(
            {
                'name': p.name,
                'size_kb': round(st.st_size / 1024, 1),
                'modified': datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'path': str(p),
            }
        )
    return rows


def _try_render_file(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix in {'.txt', '.md', '.py', '.json', '.yaml', '.yml', '.toml', '.csv', '.log'}:
        return ('text', _read_text_file(path))
    if suffix == '.pdf':
        return ('text', _read_pdf_text(path))
    if suffix == '.docx':
        return ('text', _read_docx_text(path))
    return ('text', f'Podgląd dla typu {suffix} nie jest jeszcze dostępny. Możesz pobrać plik.')


def main() -> int:
    try:
        from nicegui import app, ui
    except ModuleNotFoundError as e:
        raise SystemExit(
            "Missing dependency: nicegui. Install requirements (e.g. `pip install -r requirements.txt`) to run ciel_omega_app.py."
        ) from e

    if hasattr(sys, '_MEIPASS'):
        assets_dir = Path(getattr(sys, '_MEIPASS')) / 'main'
        entry_script_runpy = Path(getattr(sys, '_MEIPASS')) / 'scripts' / 'entry_omega_runpy.py'
        if entry_script_runpy.exists():
            sys.argv[0] = str(entry_script_runpy)
    else:
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
    ui.add_head_html(
        """
<style>
  :root {
    --ciel-bg0: #050814;
    --ciel-bg1: #070b1a;
    --ciel-surface: rgba(12, 22, 51, 0.80);
    --ciel-border: rgba(0, 184, 255, 0.24);
    --ciel-glow: rgba(33, 212, 253, 0.18);
    --ciel-primary: #00B8FF;
    --ciel-accent: #2C7BFF;
    --ciel-text: #EAF2FF;
    --ciel-muted: rgba(234, 242, 255, 0.70);
  }

  body {
    background:
      radial-gradient(circle at 22% 10%, rgba(0, 184, 255, 0.18), transparent 46%),
      radial-gradient(circle at 78% 0%, rgba(44, 123, 255, 0.14), transparent 46%),
      linear-gradient(180deg, var(--ciel-bg0), var(--ciel-bg1) 60%, #03040c);
    color: var(--ciel-text);
  }

  .q-header {
    background: linear-gradient(90deg, rgba(5, 8, 20, 0.80), rgba(12, 22, 51, 0.72));
    border-bottom: 1px solid var(--ciel-border);
    backdrop-filter: blur(10px);
  }

  .q-tab, .q-tab__label { color: var(--ciel-muted); }
  .q-tab--active .q-tab__label { color: var(--ciel-text); }
  .q-tab__indicator { background: linear-gradient(90deg, var(--ciel-primary), var(--ciel-accent)); }

  .q-card {
    background: var(--ciel-surface) !important;
    border: 1px solid var(--ciel-border);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
  }

  .q-table__card {
    background: transparent !important;
  }

  .q-btn {
    border-radius: 12px;
  }

  .q-btn.bg-primary {
    background: linear-gradient(90deg, var(--ciel-primary), var(--ciel-accent)) !important;
  }

  .q-field--outlined .q-field__control:before {
    border-color: rgba(234, 242, 255, 0.18) !important;
  }

  .q-field--outlined.q-field--focused .q-field__control:before {
    border-color: rgba(0, 184, 255, 0.55) !important;
  }

  .ciel-title {
    letter-spacing: 0.08em;
    font-weight: 800;
    text-transform: uppercase;
    background: linear-gradient(90deg, rgba(33, 212, 253, 1), rgba(44, 123, 255, 1));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 0 22px var(--ciel-glow);
  }

  .ciel-badge {
    border: 1px solid var(--ciel-border);
    background: rgba(5, 8, 20, 0.50);
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    color: var(--ciel-muted);
  }
</style>
"""
    )

    _ensure_dirs()
    state = _load_state()
    engine = LocalChatEngine()

    allow_pip_install = (
        bool(state.get('allow_pip_install'))
        if 'allow_pip_install' in state
        else os.environ.get('CIEL_ALLOW_PIP_INSTALL', '0') == '1'
    )

    global MAX_UPLOAD_MB, MAX_DOWNLOAD_MB
    if 'max_upload_mb' in state:
        try:
            MAX_UPLOAD_MB = int(state.get('max_upload_mb') or MAX_UPLOAD_MB)
        except Exception:
            pass
    if 'max_download_mb' in state:
        try:
            MAX_DOWNLOAD_MB = int(state.get('max_download_mb') or MAX_DOWNLOAD_MB)
        except Exception:
            pass

    ciel_cfg = _load_ciel_config_from_state(state)

    chat_history: list[dict[str, str]] = []

    model_load_state: dict[str, Any] = {'busy': False}

    async def _load_active_model() -> None:
        if bool(model_load_state.get('busy')):
            return
        model_load_state['busy'] = True
        try:
            if not engine.can_use_llama():
                ui.notify('Install llama-cpp-python to use GGUF locally', type='warning')
                return
            model_path = state.get('active_model')
            if not model_path:
                ui.notify('Set active model first', type='warning')
                return
            if not Path(str(model_path)).exists():
                ui.notify('Active model file missing', type='negative')
                return

            settings = state.get('llama_settings') or {}
            ui.notify('Loading model...')

            def _load() -> None:
                engine.load(
                    str(model_path),
                    n_ctx=int(settings.get('n_ctx', 2048)),
                    n_threads=settings.get('n_threads'),
                    n_gpu_layers=int(settings.get('n_gpu_layers', 0)),
                    temperature=float(settings.get('temperature', 0.7)),
                    top_p=float(settings.get('top_p', 0.95)),
                    max_tokens=int(settings.get('max_tokens', 256)),
                    repeat_penalty=float(settings.get('repeat_penalty', 1.1)),
                )

            await asyncio.to_thread(_load)
            ui.notify('Model loaded')
        except Exception as ex:
            ui.notify(f'Load error: {ex}', type='negative')
        finally:
            model_load_state['busy'] = False

    def _get_models_from_state() -> list[ModelEntry]:
        models: list[ModelEntry] = []
        for m in state.get('models', []):
            if isinstance(m, dict) and 'name' in m and 'path' in m:
                models.append(ModelEntry(name=str(m['name']), path=str(m['path'])))
        return models

    def _scan_models_folder() -> list[ModelEntry]:
        models: list[ModelEntry] = []
        for p in sorted(MODELS_DIR.glob('*.gguf')):
            if p.is_file():
                models.append(ModelEntry(name=p.name, path=str(p)))
        return models

    def _merged_models() -> list[ModelEntry]:
        seen: set[str] = set()
        out: list[ModelEntry] = []
        for m in _scan_models_folder() + _get_models_from_state():
            if m.path in seen:
                continue
            seen.add(m.path)
            out.append(m)
        return out

    def _set_active_model(model_path: Optional[str]) -> None:
        state['active_model'] = model_path
        _save_state(state)

    def _add_model(name: str, path: str) -> None:
        models = state.get('models', [])
        for m in models:
            if isinstance(m, dict) and str(m.get('path')) == str(path):
                return
        models.append({'name': name, 'path': path})
        state['models'] = models
        _save_state(state)

    ui.query('.nicegui-content').classes('p-0')

    with ui.header().classes('items-center justify-between'):
        with ui.row().classes('items-center gap-3'):
            ui.image('/assets/Logo1.png').classes('h-10 w-10')
            ui.label('CIEL').classes('text-xl ciel-title')
            ui.label('Ω client').classes('text-xs ciel-badge')
        with ui.row().classes('items-center gap-2'):
            urls_label = ui.label('')

            def _render_urls() -> None:
                try:
                    urls = getattr(app, 'urls', None)
                    if urls is None:
                        urls_label.text = ''
                        return
                    urls_label.text = ', '.join(sorted(str(u) for u in list(urls)))
                except Exception:
                    urls_label.text = ''

            _render_urls()
            ui.timer(1.0, _render_urls)

    with ui.tabs().classes('w-full') as tabs:
        ui.tab('Dashboard')
        ui.tab('Kernel')
        ui.tab('Chat')
        ui.tab('Files')
        ui.tab('Models')
        ui.tab('Observability')
        ui.tab('Settings')

    with ui.tab_panels(tabs, value='Dashboard').classes('w-full'):

        with ui.tab_panel('Dashboard'):
            def _go_tab(name: str) -> None:
                try:
                    tabs.value = name
                    tabs.update()
                except Exception:
                    pass

            hero_title = ui.label('CIEL/Ω').classes('text-2xl font-bold px-4 pt-4 ciel-title')
            hero_sub = ui.label('Local AI workspace: models, kernels, observability.').classes('text-sm px-4 text-gray-300')

            with ui.row().classes('w-full p-4 gap-4'):
                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Mission Control').classes('text-base font-semibold')
                    mission_status = ui.label('').classes('text-xs text-gray-400')
                    ethics_status = ui.label('').classes('text-xs text-gray-400')
                    log_status = ui.label('').classes('text-xs text-gray-400')

                    def _refresh_mission() -> None:
                        cfg = _load_ciel_config_from_state(state)
                        model_path = state.get('active_model')
                        model_ok = bool(model_path) and Path(str(model_path)).exists()
                        llama_ok = engine.can_use_llama()
                        loaded = engine.is_loaded()
                        mission_status.text = (
                            f"Model: {'set' if model_ok else 'missing'} | "
                            f"llama: {'yes' if llama_ok else 'no'} | "
                            f"loaded: {'yes' if loaded else 'no'}"
                        )
                        ethics_status.text = (
                            f"Ethics: min_coherence={cfg.ethics_min_coherence:.2f} | "
                            f"block={ 'yes' if cfg.ethics_block_on_violation else 'no' }"
                        )
                        log_status.text = f"Log path: {cfg.log_path}"

                    _refresh_mission()
                    ui.timer(1.0, _refresh_mission)

                    with ui.row().classes('w-full gap-2 pt-2'):
                        ui.button('Models', on_click=lambda: _go_tab('Models'))
                        ui.button('Chat', on_click=lambda: _go_tab('Chat'))
                        ui.button('Kernel', on_click=lambda: _go_tab('Kernel'))

                    with ui.row().classes('w-full gap-2 pt-2'):
                        ui.button('Load active model', on_click=_load_active_model)
                        ui.button('Unload model', on_click=lambda: (engine.unload(), ui.notify('Model unloaded')))

                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Reality Pulse').classes('text-base font-semibold')
                    pulse_status = ui.label('').classes('text-xs text-gray-400')
                    pulse_gauge_options: dict[str, Any] = {
                        'series': [
                            {
                                'type': 'gauge',
                                'min': 0,
                                'max': 1,
                                'startAngle': 210,
                                'endAngle': -30,
                                'progress': {'show': True, 'width': 10},
                                'axisLine': {'lineStyle': {'width': 10}},
                                'pointer': {'show': True, 'width': 4},
                                'axisTick': {'show': False},
                                'splitLine': {'length': 10, 'lineStyle': {'width': 1}},
                                'axisLabel': {'color': 'rgba(234, 242, 255, 0.70)'},
                                'title': {'show': True, 'offsetCenter': [0, '65%'], 'color': 'rgba(234, 242, 255, 0.70)'},
                                'detail': {'valueAnimation': True, 'formatter': '{value}', 'color': '#EAF2FF'},
                                'data': [{'value': 0.0, 'name': 'resonance'}],
                            }
                        ],
                    }
                    pulse_gauge = ui.echart(pulse_gauge_options).classes('w-full')
                    pulse_gauge.style('height: 180px;')
                    pulse_view = ui.code('').classes('w-full')
                    pulse_view.style('height: 220px; overflow: auto;')

                    def _resolve_log_path(path_str: str) -> Path:
                        p = Path(path_str).expanduser()
                        if p.is_absolute():
                            return p
                        return DATA_DIR / p

                    def _read_last_jsonl(path: Path) -> Optional[dict[str, Any]]:
                        if not path.exists() or not path.is_file():
                            return None
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
                        try:
                            return json.loads(lines[-1])
                        except Exception:
                            return None

                    def _refresh_pulse() -> None:
                        cfg = _load_ciel_config_from_state(state)
                        p = _resolve_log_path(str(cfg.log_path))
                        rec = _read_last_jsonl(p)
                        if rec is None:
                            pulse_status.text = f'No recent log record (expected: {p})'
                            pulse_view.content = ''
                            pulse_view.update()
                            pulse_gauge_options['series'][0]['data'][0]['value'] = 0.0
                            pulse_gauge.update()
                            return

                        step = rec.get('step')
                        t = rec.get('t')
                        age = None
                        try:
                            age = None if t is None else (time.time() - float(t))
                        except Exception:
                            age = None
                        resonance = rec.get('resonance_mean')
                        ethical_ok = rec.get('ethical_ok')
                        age_txt = '-' if age is None else f'{age:.1f}s ago'
                        pulse_status.text = f"step={step} | resonance={resonance} | ethical_ok={ethical_ok} | {age_txt}"
                        try:
                            r_val = 0.0 if resonance is None else float(resonance)
                            r_val = max(0.0, min(1.0, r_val))
                        except Exception:
                            r_val = 0.0
                        pulse_gauge_options['series'][0]['data'][0]['value'] = r_val
                        pulse_gauge.update()
                        pulse_view.content = json.dumps(rec, ensure_ascii=False, indent=2)
                        pulse_view.update()

                    _refresh_pulse()
                    ui.timer(1.0, _refresh_pulse)

                    with ui.row().classes('w-full justify-end gap-2 pt-2'):
                        ui.button('Open Observability', on_click=lambda: _go_tab('Observability'))

                with ui.card().classes('w-1/3 p-4'):
                    ui.label('Data Vault').classes('text-base font-semibold')
                    vault_status = ui.label('').classes('text-xs text-gray-400')
                    ui.label(f'Data dir: {DATA_DIR}').classes('text-xs text-gray-400')
                    ui.label(f'Models dir: {MODELS_DIR}').classes('text-xs text-gray-400')
                    ui.label(f'Files dir: {FILES_DIR}').classes('text-xs text-gray-400')

                    def _refresh_vault() -> None:
                        try:
                            models_n = len([p for p in MODELS_DIR.glob('*.gguf') if p.is_file()])
                        except Exception:
                            models_n = 0
                        try:
                            files_n = len([p for p in FILES_DIR.glob('*') if p.is_file()])
                        except Exception:
                            files_n = 0
                        vault_status.text = f'models: {models_n} | files: {files_n} | state: {STATE_PATH.name}'

                    _refresh_vault()
                    ui.timer(2.0, _refresh_vault)

                    with ui.row().classes('w-full gap-2 pt-2'):
                        ui.button('Models', on_click=lambda: _go_tab('Models'))
                        ui.button('Files', on_click=lambda: _go_tab('Files'))
                        ui.button('Settings', on_click=lambda: _go_tab('Settings'))

            with ui.row().classes('w-full gap-4 p-4'):
                cpu_label = ui.label('CPU: -')
                ram_label = ui.label('RAM: -')
                proc_label = ui.label('Process: -')

            chart_options: dict[str, Any] = {
                'tooltip': {'trigger': 'axis'},
                'legend': {'data': ['CPU %', 'RAM %']},
                'xAxis': {'type': 'category', 'data': []},
                'yAxis': {'type': 'value', 'min': 0, 'max': 100},
                'series': [
                    {'type': 'line', 'name': 'CPU %', 'data': [], 'showSymbol': False},
                    {'type': 'line', 'name': 'RAM %', 'data': [], 'showSymbol': False},
                ],
                'animation': False,
                'grid': {'left': 40, 'right': 20, 'top': 40, 'bottom': 30},
            }

            with ui.card().classes('w-full m-4'):
                chart = ui.echart(chart_options).classes('w-full').style('height: 320px')

            def update_dashboard() -> None:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent
                p = psutil.Process(os.getpid())
                rss_mb = p.memory_info().rss / (1024 * 1024)

                cpu_label.text = f'CPU: {cpu:.1f}%'
                ram_label.text = f'RAM: {ram:.1f}%'
                proc_label.text = f'Process RSS: {rss_mb:.1f} MB'

                now = datetime.now().strftime('%H:%M:%S')
                xs: list[str] = chart_options['xAxis']['data']
                xs.append(now)
                chart_options['series'][0]['data'].append(round(cpu, 2))
                chart_options['series'][1]['data'].append(round(ram, 2))

                if len(xs) > 120:
                    xs.pop(0)
                    chart_options['series'][0]['data'].pop(0)
                    chart_options['series'][1]['data'].pop(0)

                chart.update()

            ui.timer(1.0, update_dashboard)

        with ui.tab_panel('Kernel'):
            kernel_state: dict[str, Any] = {
                'kernel': None,
                'running': False,
                'busy': False,
                'step': 0,
                'last': {},
                'error': None,
                'error_tb': None,
                'guard': None,
                'logger': None,
                'x': [],
                'resonance': [],
                'mass': [],
                'lambda0': [],
            }

            with ui.row().classes('w-full gap-4 p-4'):
                kernel_select = ui.select(sorted(KERNELS.keys()), value='ciel0', label='Kernel')
                mode_select = ui.select(['fft', 'nofft'], value=str(ciel_cfg.compute_mode), label='Mode')
                grid_input = ui.number(label='Grid', value=64, min=8, max=1024)
                length_input = ui.number(label='Length (FFT)', value=10.0, min=0.1, max=1_000.0)
                dt_input = ui.number(label='dt', value=0.1, min=1e-6, max=10.0)

            with ui.row().classes('w-full gap-4 px-4'):
                step_label = ui.label('step: 0')
                status_label = ui.label('status: idle')
                last_label = ui.label('metrics: {}').classes('truncate')

            chart_options_kernel: dict[str, Any] = {
                'tooltip': {'trigger': 'axis'},
                'legend': {'data': ['resonance_mean', 'mass_mean', 'lambda0_mean']},
                'xAxis': {'type': 'category', 'data': []},
                'yAxis': {'type': 'value'},
                'series': [
                    {'type': 'line', 'name': 'resonance_mean', 'data': [], 'showSymbol': False},
                    {'type': 'line', 'name': 'mass_mean', 'data': [], 'showSymbol': False},
                    {'type': 'line', 'name': 'lambda0_mean', 'data': [], 'showSymbol': False},
                ],
                'animation': False,
                'grid': {'left': 50, 'right': 20, 'top': 40, 'bottom': 30},
            }

            with ui.card().classes('w-full m-4'):
                kernel_chart = ui.echart(chart_options_kernel).classes('w-full').style('height: 320px')

            def _build_kernel() -> None:
                cfg_base = _load_ciel_config_from_state(state)
                cfg = CielConfig(
                    enable_gpu=cfg_base.enable_gpu,
                    enable_numba=cfg_base.enable_numba,
                    compute_mode=str(mode_select.value),
                    log_path=cfg_base.log_path,
                    ethics_min_coherence=cfg_base.ethics_min_coherence,
                    ethics_block_on_violation=cfg_base.ethics_block_on_violation,
                    dataset_path=cfg_base.dataset_path,
                )
                name = str(kernel_select.value)
                grid = int(grid_input.value or 64)
                length = float(length_input.value or 10.0)
                factory = KERNELS[name]
                kernel_state['kernel'] = factory(cfg, grid, DEFAULT_CONSTANTS, length)
                guard, logger = attach_ethics_and_logging(kernel_state['kernel'], cfg)
                kernel_state['guard'] = guard
                kernel_state['logger'] = logger
                kernel_state['step'] = 0
                kernel_state['last'] = {}
                kernel_state['error'] = None
                kernel_state['x'] = []
                kernel_state['resonance'] = []
                kernel_state['mass'] = []
                kernel_state['lambda0'] = []
                chart_options_kernel['xAxis']['data'].clear()
                for s in chart_options_kernel['series']:
                    s['data'].clear()
                kernel_chart.update()
                step_label.text = 'step: 0'
                status_label.text = 'status: ready'
                last_label.text = 'metrics: {}'

            def _start_kernel() -> None:
                if kernel_state['kernel'] is None:
                    _build_kernel()
                kernel_state['running'] = True
                status_label.text = 'status: running'

            def _stop_kernel() -> None:
                kernel_state['running'] = False
                status_label.text = 'status: stopped'

            def _reset_kernel() -> None:
                kernel_state['running'] = False
                kernel_state['kernel'] = None
                _build_kernel()

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Build', on_click=_build_kernel)
                ui.button('Start', on_click=_start_kernel)
                ui.button('Stop', on_click=_stop_kernel)
                ui.button('Reset', on_click=_reset_kernel)

            async def _kernel_tick() -> None:
                if not kernel_state['running']:
                    return
                if kernel_state['busy']:
                    return
                if kernel_state['kernel'] is None:
                    return

                kernel_state['busy'] = True
                try:
                    dt = float(dt_input.value or 0.1)

                    def _do_step():
                        return kernel_state['kernel'].step(dt=dt)

                    metrics = await asyncio.to_thread(_do_step)

                    guard = kernel_state.get('guard')
                    if guard is not None:
                        coherence = metrics.get('resonance_mean')
                        coherence = 1.0 if coherence is None else float(coherence)
                        ethical_ok_val = metrics.get('ethical_ok')
                        ethical_ok = True if ethical_ok_val is None else float(ethical_ok_val) >= 0.5
                        guard.check_step(coherence=coherence, ethical_ok=ethical_ok, info_fidelity=1.0)

                    logger = kernel_state.get('logger')
                    if logger is not None:
                        logger.record(int(kernel_state['step']) + 1, metrics)

                    kernel_state['step'] += 1
                    kernel_state['last'] = metrics
                    kernel_state['error'] = None

                    x = kernel_state['step']
                    chart_options_kernel['xAxis']['data'].append(x)

                    r = metrics.get('resonance_mean')
                    m = metrics.get('mass_mean')
                    l0 = metrics.get('lambda0_mean')
                    chart_options_kernel['series'][0]['data'].append(None if r is None else float(r))
                    chart_options_kernel['series'][1]['data'].append(None if m is None else float(m))
                    chart_options_kernel['series'][2]['data'].append(None if l0 is None else float(l0))

                    if len(chart_options_kernel['xAxis']['data']) > 200:
                        chart_options_kernel['xAxis']['data'].pop(0)
                        for s in chart_options_kernel['series']:
                            s['data'].pop(0)

                    kernel_chart.update()
                    step_label.text = f"step: {kernel_state['step']}"
                    last_label.text = f"metrics: {json.dumps(metrics, ensure_ascii=False)}"
                except Exception as ex:
                    kernel_state['error'] = str(ex)
                    kernel_state['error_tb'] = traceback.format_exc()
                    kernel_state['running'] = False
                    status_label.text = f"status: error: {ex}"
                finally:
                    kernel_state['busy'] = False

            def _schedule_kernel_tick() -> None:
                asyncio.create_task(_kernel_tick())

            ui.timer(0.2, _schedule_kernel_tick)

        with ui.tab_panel('Chat'):
            with ui.row().classes('w-full h-[calc(100vh-140px)]'):
                with ui.column().classes('w-full p-4 gap-3'):
                    with ui.card().classes('w-full p-3'):
                        ui.label('Chat Runtime').classes('text-base font-semibold')
                        chat_status = ui.label('').classes('text-xs text-gray-400')

                        def _refresh_chat_status() -> None:
                            model_path = state.get('active_model')
                            model_ok = bool(model_path) and Path(str(model_path)).exists()
                            llama_ok = engine.can_use_llama()
                            loaded = engine.is_loaded()
                            chat_status.text = (
                                f"Active model: {model_path or '(none)'} | "
                                f"exists: {'yes' if model_ok else 'no'} | "
                                f"llama: {'yes' if llama_ok else 'no'} | "
                                f"loaded: {'yes' if loaded else 'no'}"
                            )

                        _refresh_chat_status()
                        ui.timer(1.0, _refresh_chat_status)

                        with ui.row().classes('w-full justify-end gap-2'):
                            ui.button('Load active model', on_click=_load_active_model)

                    with ui.scroll_area().classes('w-full').style('height: calc(100vh - 260px)'):
                        chat_container = ui.column().classes('w-full gap-2')

                    message_input = ui.textarea(label='Message').classes('w-full')

                    async def send_message() -> None:
                        text = (message_input.value or '').strip()
                        if not text:
                            return

                        if not engine.is_loaded():
                            ui.notify('Model is not loaded. Click "Load active model" first.', type='warning')
                            return

                        chat_history.append({'role': 'user', 'content': text})
                        with chat_container:
                            ui.chat_message(text=text, name='You', sent=True)

                        message_input.value = ''

                        with chat_container:
                            thinking = ui.chat_message(text='...', name='CIEL/Ω', sent=False)

                        reply = await engine.chat(text, chat_history)
                        chat_history.append({'role': 'assistant', 'content': reply})

                        thinking.delete()
                        with chat_container:
                            ui.chat_message(text=reply, name='CIEL/Ω', sent=False)

                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Send', on_click=send_message)

        with ui.tab_panel('Files'):
            with ui.row().classes('w-full p-4 gap-4'):
                with ui.card().classes('w-1/2'):
                    ui.label('Upload / Library').classes('text-base font-semibold')

                    files_table = ui.table(
                        columns=[
                            {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                            {'name': 'size_kb', 'label': 'KB', 'field': 'size_kb', 'align': 'right'},
                            {'name': 'modified', 'label': 'Modified', 'field': 'modified', 'align': 'left'},
                        ],
                        rows=[],
                        row_key='path',
                        selection='single',
                    ).classes('w-full')

                    def refresh_files() -> None:
                        files_table.rows = _list_files(FILES_DIR)
                        files_table.update()

                    async def on_upload(e) -> None:
                        name = _safe_name(getattr(e, 'name', 'upload.bin'))
                        dest = FILES_DIR / name

                        def _save() -> None:
                            src = getattr(e, 'content', None)
                            if src is None:
                                raise RuntimeError('upload has no content')
                            with open(dest, 'wb') as f:
                                written = 0
                                max_bytes = int(MAX_UPLOAD_MB) * 1024 * 1024
                                while True:
                                    chunk = src.read(1024 * 1024)
                                    if not chunk:
                                        break
                                    written += len(chunk)
                                    if written > max_bytes:
                                        raise RuntimeError(f'upload too large (>{MAX_UPLOAD_MB} MB)')
                                    f.write(chunk)

                        try:
                            await asyncio.to_thread(_save)
                            ui.notify(f'Uploaded: {name}')
                            refresh_files()
                        except Exception as ex:
                            ui.notify(f'Upload error: {ex}', type='negative')

                    ui.upload(on_upload=on_upload, auto_upload=True).classes('w-full')

                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Refresh', on_click=refresh_files)

                    refresh_files()

                    file_delete_dialog = ui.dialog()

                    def delete_selected_file() -> None:
                        selection = files_table.selected
                        if not selection:
                            ui.notify('Select a file first')
                            return
                        p = Path(selection[0]['path'])
                        if p.exists() and p.is_file() and p.parent == FILES_DIR:
                            p.unlink()
                            ui.notify(f'Deleted: {p.name}')
                            refresh_files()

                    with ui.row().classes('w-full justify-end gap-2 mt-2'):
                        ui.button(
                            'Download',
                            on_click=lambda: (files_table.selected and ui.download.file(files_table.selected[0]['path'])),
                        )
                        ui.button('Delete', color='negative', on_click=lambda: file_delete_dialog.open())

                    with file_delete_dialog:
                        with ui.card():
                            ui.label('Delete selected file?')
                            with ui.row().classes('justify-end gap-2'):
                                ui.button('Cancel', on_click=file_delete_dialog.close)
                                ui.button(
                                    'Delete',
                                    color='negative',
                                    on_click=lambda: (delete_selected_file(), file_delete_dialog.close()),
                                )

                with ui.card().classes('w-1/2'):
                    ui.label('Preview / Create').classes('text-base font-semibold')

                    preview_title = ui.label('No file selected').classes('font-semibold')
                    preview_area = ui.code('').classes('w-full')
                    preview_area.style('height: 360px; overflow: auto;')

                    def update_preview() -> None:
                        selection = files_table.selected
                        if not selection:
                            preview_title.text = 'No file selected'
                            preview_area.content = ''
                            preview_area.update()
                            return
                        p = Path(selection[0]['path'])
                        if not p.exists():
                            preview_title.text = 'Missing file'
                            preview_area.content = ''
                            preview_area.update()
                            return

                        preview_title.text = p.name
                        kind, content = _try_render_file(p)
                        if kind == 'text':
                            preview_area.content = content
                            preview_area.update()

                    files_table.on('selection', lambda _: update_preview())

                    ui.separator()

                    new_name = ui.input('New file name (txt/md)').classes('w-full')
                    new_content = ui.textarea('Content').classes('w-full')

                    def save_new_file() -> None:
                        name = _safe_name(new_name.value or '')
                        if not name:
                            ui.notify('Enter file name')
                            return
                        if not (name.lower().endswith('.txt') or name.lower().endswith('.md')):
                            ui.notify('Only .txt or .md for now')
                            return
                        dest = FILES_DIR / name
                        dest.write_text(new_content.value or '', encoding='utf-8')
                        ui.notify(f'Saved: {name}')
                        refresh_files()

                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Save file', on_click=save_new_file)

        with ui.tab_panel('Models'):
            with ui.row().classes('w-full p-4 gap-4'):
                with ui.card().classes('w-1/2'):
                    ui.label('GGUF Model Library').classes('text-base font-semibold')

                    ui.label(f'Models folder: {MODELS_DIR}').classes('text-xs text-gray-500')
                    limits_label = ui.label(
                        f'Limits: upload {MAX_UPLOAD_MB} MB, download {MAX_DOWNLOAD_MB} MB'
                    ).classes('text-xs text-gray-500')

                    models_table = ui.table(
                        columns=[
                            {'name': 'active', 'label': 'Active', 'field': 'active', 'align': 'left'},
                            {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                            {'name': 'size_mb', 'label': 'MB', 'field': 'size_mb', 'align': 'right'},
                            {'name': 'modified', 'label': 'Modified', 'field': 'modified', 'align': 'left'},
                            {'name': 'path', 'label': 'Path', 'field': 'path', 'align': 'left'},
                        ],
                        rows=[],
                        row_key='path',
                        selection='single',
                    ).classes('w-full')

                    def refresh_models() -> None:
                        rows: list[dict[str, Any]] = []
                        active = str(state.get('active_model') or '')
                        for m in _merged_models():
                            p = Path(m.path)
                            size_mb = round((p.stat().st_size / (1024 * 1024)), 2) if p.exists() and p.is_file() else None
                            modified = (
                                datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                                if p.exists() and p.is_file()
                                else None
                            )
                            rows.append(
                                {
                                    'active': '✓' if str(m.path) == active else '',
                                    'name': m.name,
                                    'size_mb': size_mb,
                                    'modified': modified,
                                    'path': m.path,
                                }
                            )
                        models_table.rows = rows
                        models_table.update()

                    refresh_models()

                    async def on_model_upload(e) -> None:
                        name = _safe_name(getattr(e, 'name', 'model.gguf'))
                        if not name.lower().endswith('.gguf'):
                            ui.notify('Only .gguf files are allowed', type='warning')
                            return
                        dest = MODELS_DIR / name
                        if dest.exists():
                            ui.notify('File already exists in models folder', type='warning')
                            return

                        def _save() -> None:
                            src = getattr(e, 'content', None)
                            if src is None:
                                raise RuntimeError('upload has no content')
                            with open(dest, 'wb') as f:
                                written = 0
                                max_bytes = int(MAX_UPLOAD_MB) * 1024 * 1024
                                while True:
                                    chunk = src.read(1024 * 1024)
                                    if not chunk:
                                        break
                                    written += len(chunk)
                                    if written > max_bytes:
                                        raise RuntimeError(f'upload too large (>{MAX_UPLOAD_MB} MB)')
                                    f.write(chunk)

                        try:
                            await asyncio.to_thread(_save)
                            _add_model(dest.name, str(dest))
                            ui.notify(f'Uploaded: {dest.name}')
                            refresh_models()
                        except Exception as ex:
                            ui.notify(f'Upload error: {ex}', type='negative')

                    ui.upload(on_upload=on_model_upload, auto_upload=True).classes('w-full')

                    url_input = ui.input('GGUF URL').classes('w-full')
                    fname_input = ui.input('Save as (e.g. model.gguf)').classes('w-full')

                    catalog_rows = [
                        {
                            'key': m.key,
                            'name': m.display_name,
                            'ram': m.recommended_ram_gb,
                            'vram': m.recommended_vram_gb,
                            'notes': m.notes,
                            'filename': m.gguf_filename_hint,
                            'url': m.url_hint,
                        }
                        for m in MODEL_CATALOG
                    ]
                    if catalog_rows:
                        ui.separator()
                        ui.label('Recommended models (pick -> paste URL -> download)').classes('text-sm font-semibold')

                        catalog_select = ui.select(
                            options=[{'label': r['name'], 'value': r['key']} for r in catalog_rows],
                            label='Catalog',
                        ).classes('w-full')
                        catalog_info = ui.label('').classes('text-xs text-gray-500')

                        def _apply_catalog_choice() -> None:
                            k = catalog_select.value
                            if not k:
                                return
                            row = next((r for r in catalog_rows if r['key'] == k), None)
                            if not row:
                                return
                            fname_input.value = row['filename']
                            url_input.value = ''
                            vram_txt = '-' if row['vram'] is None else f"{row['vram']:.1f} GB"
                            catalog_info.text = (
                                f"RAM: {row['ram']:.1f} GB | VRAM: {vram_txt} | {row['notes']} | URL: {row['url']}"
                            )

                        ui.button('Apply selection', on_click=_apply_catalog_choice)

                    progress = ui.linear_progress(value=0).classes('w-full')
                    progress.visible = False
                    progress.update()
                    status_label = ui.label('')

                    current_task: dict[str, Optional[DownloadTask]] = {'task': None}

                    def _start_download() -> None:
                        url = (url_input.value or '').strip()
                        fname = _safe_name(fname_input.value or '').strip()
                        if not url:
                            ui.notify('Provide URL')
                            return
                        if not fname.lower().endswith('.gguf'):
                            ui.notify('Filename must end with .gguf')
                            return

                        dest = MODELS_DIR / fname
                        t = DownloadTask(url=url, dest=dest)
                        current_task['task'] = t
                        progress.value = 0
                        progress.visible = True
                        progress.update()
                        status_label.text = 'Downloading...'

                        Thread(target=_download_to_file, args=(t,), daemon=True).start()

                    def _poll_download() -> None:
                        t = current_task.get('task')
                        if t is None:
                            return
                        if t.total:
                            if t.dest.exists():
                                size = t.dest.stat().st_size
                            else:
                                part = t.dest.with_suffix(t.dest.suffix + '.part')
                                size = part.stat().st_size if part.exists() else 0
                            progress.value = min(1.0, size / max(1, t.total))
                            progress.update()
                        if t.done:
                            progress.visible = False
                            progress.update()
                            if t.error:
                                status_label.text = f'Error: {t.error}'
                            else:
                                status_label.text = f'Done: {t.dest.name}'
                                _add_model(t.dest.name, str(t.dest))
                                refresh_models()
                            current_task['task'] = None

                    ui.timer(0.5, _poll_download)

                    delete_dialog = ui.dialog()

                    def delete_selected_model() -> None:
                        selection = models_table.selected
                        if not selection:
                            ui.notify('Select a model first')
                            return
                        p = Path(selection[0]['path'])
                        if not (p.exists() and p.is_file()):
                            ui.notify('Model file missing', type='warning')
                            refresh_models()
                            return
                        if p.parent != MODELS_DIR:
                            ui.notify('Can only delete models inside models folder', type='warning')
                            return
                        p.unlink()
                        models = [m for m in state.get('models', []) if not (isinstance(m, dict) and str(m.get('path')) == str(p))]
                        state['models'] = models
                        if str(state.get('active_model') or '') == str(p):
                            state['active_model'] = None
                        _save_state(state)
                        ui.notify(f'Deleted: {p.name}')
                        refresh_models()

                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Download GGUF', on_click=_start_download)
                        ui.button('Scan Folder', on_click=refresh_models)
                        ui.button('Refresh', on_click=refresh_models)
                        ui.button('Delete', color='negative', on_click=lambda: delete_dialog.open())

                    with delete_dialog:
                        with ui.card():
                            ui.label('Delete selected GGUF from models folder?')
                            with ui.row().classes('justify-end gap-2'):
                                ui.button('Cancel', on_click=delete_dialog.close)
                                ui.button(
                                    'Delete',
                                    color='negative',
                                    on_click=lambda: (delete_selected_model(), delete_dialog.close()),
                                )

                with ui.card().classes('w-1/2'):
                    ui.label('Active Model / Engine').classes('text-base font-semibold')

                    ui.label('Workflow: Upload/Download → Select in table → Set Active → Load → Chat').classes('text-xs text-gray-400')

                    llama_available = engine.can_use_llama()
                    llama_label = ui.label(f'llama-cpp-python available: {"yes" if llama_available else "no"}')

                    install_state: dict[str, Any] = {'running': False, 'done': False, 'ok': False, 'output': ''}
                    install_log = ui.code('').classes('w-full')
                    install_log.style('height: 180px; overflow: auto;')
                    install_log.visible = False
                    install_dialog = ui.dialog()

                    def _start_install_llama() -> None:
                        if install_state.get('running'):
                            return
                        install_state['running'] = True
                        install_state['done'] = False
                        install_state['ok'] = False
                        install_state['output'] = ''
                        install_log.visible = True
                        install_log.content = 'Installing llama-cpp-python...\n'
                        install_log.update()

                        def _run() -> None:
                            p = subprocess.run(
                                [sys.executable, '-m', 'pip', 'install', 'llama-cpp-python'],
                                capture_output=True,
                                text=True,
                            )
                            out = (p.stdout or '') + ('\n' if p.stdout else '') + (p.stderr or '')
                            if len(out) > 200_000:
                                out = out[:200_000] + '\n\n[...truncated...]'
                            install_state['output'] = out
                            install_state['ok'] = p.returncode == 0
                            install_state['done'] = True
                            install_state['running'] = False

                        Thread(target=_run, daemon=True).start()

                    def _poll_install() -> None:
                        if not install_state.get('done'):
                            return
                        install_state['done'] = False
                        install_log.content = install_state.get('output', '')
                        install_log.update()
                        ok = bool(install_state.get('ok'))
                        if ok:
                            ui.notify('llama-cpp-python installed')
                        else:
                            ui.notify('Install failed; see log', type='warning')
                        avail = engine.can_use_llama()
                        llama_label.text = f'llama-cpp-python available: {"yes" if avail else "no"}'

                    ui.timer(0.5, _poll_install)

                    if not llama_available:
                        if allow_pip_install:
                            ui.button('Install llama-cpp-python', on_click=lambda: install_dialog.open())
                            with install_dialog:
                                with ui.card():
                                    ui.label('Install llama-cpp-python now?')
                                    ui.label('This runs pip and may take a while.').classes('text-xs text-gray-500')
                                    with ui.row().classes('justify-end gap-2'):
                                        ui.button('Cancel', on_click=install_dialog.close)
                                        ui.button(
                                            'Install',
                                            on_click=lambda: (_start_install_llama(), install_dialog.close()),
                                        )
                        else:
                            ui.label('Install llama-cpp-python via installer (recommended).').classes('text-xs text-gray-500')

                    active_path = state.get('active_model')
                    active_label = ui.label(f'Active model: {active_path or "(none)"}')

                    settings = state.get('llama_settings') or {}
                    n_ctx_input = ui.number(label='n_ctx', value=settings.get('n_ctx', 2048), min=256, max=32768)
                    n_threads_input = ui.number(
                        label='n_threads (0=auto)',
                        value=int(settings.get('n_threads') or 0),
                        min=0,
                        max=256,
                    )
                    n_gpu_layers_input = ui.number(label='n_gpu_layers', value=settings.get('n_gpu_layers', 0), min=0, max=200)
                    temperature_input = ui.number(label='temperature', value=settings.get('temperature', 0.7), min=0.0, max=2.0)
                    top_p_input = ui.number(label='top_p', value=settings.get('top_p', 0.95), min=0.0, max=1.0)
                    max_tokens_input = ui.number(label='max_tokens', value=settings.get('max_tokens', 256), min=1, max=8192)
                    repeat_penalty_input = ui.number(label='repeat_penalty', value=settings.get('repeat_penalty', 1.1), min=0.8, max=2.0)

                    def _save_llama_settings() -> dict[str, Any]:
                        s = {
                            'n_ctx': int(n_ctx_input.value or 2048),
                            'n_threads': None if int(n_threads_input.value or 0) <= 0 else int(n_threads_input.value),
                            'n_gpu_layers': int(n_gpu_layers_input.value or 0),
                            'temperature': float(temperature_input.value or 0.7),
                            'top_p': float(top_p_input.value or 0.95),
                            'max_tokens': int(max_tokens_input.value or 256),
                            'repeat_penalty': float(repeat_penalty_input.value or 1.1),
                        }
                        state['llama_settings'] = s
                        _save_state(state)
                        return s

                    def set_active_from_selection() -> None:
                        selection = models_table.selected
                        if not selection:
                            ui.notify('Select a model first')
                            return
                        p = selection[0]['path']
                        _set_active_model(p)
                        active_label.text = f'Active model: {p}'

                    async def set_active_and_load() -> None:
                        set_active_from_selection()
                        await load_engine()

                    async def load_engine() -> None:
                        if not engine.can_use_llama():
                            ui.notify('Install llama-cpp-python to use GGUF locally', type='warning')
                            return
                        model_path = state.get('active_model')
                        if not model_path:
                            ui.notify('Set active model first', type='warning')
                            return
                        if not Path(model_path).exists():
                            ui.notify('Active model file missing', type='negative')
                            return

                        ui.notify('Loading model...')

                        s = _save_llama_settings()

                        def _load() -> None:
                            engine.load(
                                model_path,
                                n_ctx=int(s.get('n_ctx', 2048)),
                                n_threads=s.get('n_threads'),
                                n_gpu_layers=int(s.get('n_gpu_layers', 0)),
                                temperature=float(s.get('temperature', 0.7)),
                                top_p=float(s.get('top_p', 0.95)),
                                max_tokens=int(s.get('max_tokens', 256)),
                                repeat_penalty=float(s.get('repeat_penalty', 1.1)),
                            )

                        await asyncio.to_thread(_load)
                        ui.notify('Model loaded')

                    def unload_engine() -> None:
                        engine.unload()
                        ui.notify('Model unloaded')

                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Set Active', on_click=set_active_from_selection)
                        ui.button('Set Active + Load', on_click=set_active_and_load)
                        ui.button('Load', on_click=load_engine)
                        ui.button('Unload', on_click=unload_engine)

        with ui.tab_panel('Observability'):
            diag_state: dict[str, Any] = {
                'cupy_ok': False,
                'cupy_info': None,
                'numba_ok': False,
                'numba_info': None,
            }

            try:
                import cupy  # type: ignore

                diag_state['cupy_ok'] = True
                try:
                    n = int(cupy.cuda.runtime.getDeviceCount())
                    diag_state['cupy_info'] = f'CUDA devices: {n}'
                except Exception as ex:
                    diag_state['cupy_info'] = f'cupy import ok, cuda error: {ex}'
            except Exception as ex:
                diag_state['cupy_ok'] = False
                diag_state['cupy_info'] = f'cupy unavailable: {ex}'

            try:
                import numba  # type: ignore

                diag_state['numba_ok'] = True
                diag_state['numba_info'] = f'numba {getattr(numba, "__version__", "?")}'
            except Exception as ex:
                diag_state['numba_ok'] = False
                diag_state['numba_info'] = f'numba unavailable: {ex}'

            with ui.row().classes('w-full p-4 gap-4'):
                with ui.card().classes('w-1/2'):
                    ui.label('Diagnostics').classes('text-base font-semibold')

                    py_label = ui.label('Python: -').classes('text-xs')
                    exe_label = ui.label('Executable: -').classes('text-xs')
                    data_label = ui.label('Data dir: -').classes('text-xs')
                    cwd_label = ui.label('CWD: -').classes('text-xs')
                    llama_label = ui.label('llama-cpp-python: -').classes('text-xs')
                    model_label = ui.label('Active model: -').classes('text-xs')
                    cupy_label = ui.label('GPU/cupy: -').classes('text-xs')
                    numba_label = ui.label('numba: -').classes('text-xs')

                    def _refresh_diag() -> None:
                        py_label.text = f'Python: {sys.version.splitlines()[0]}'
                        exe_label.text = f'Executable: {sys.executable}'
                        data_label.text = f'Data dir: {DATA_DIR}'
                        cwd_label.text = f'CWD: {Path.cwd()}'

                        llama_ok = engine.can_use_llama()
                        llama_loaded = engine.is_loaded()
                        llama_label.text = f'llama-cpp-python: {"yes" if llama_ok else "no"} | loaded: {"yes" if llama_loaded else "no"}'
                        model_label.text = f'Active model: {state.get("active_model") or "(none)"}'

                        cupy_ok = bool(diag_state.get('cupy_ok'))
                        cupy_info = diag_state.get('cupy_info')
                        cupy_label.text = f'GPU/cupy: {"yes" if cupy_ok else "no"} | {cupy_info}'

                        numba_ok = bool(diag_state.get('numba_ok'))
                        numba_info = diag_state.get('numba_info')
                        numba_label.text = f'numba: {"yes" if numba_ok else "no"} | {numba_info}'

                    _refresh_diag()
                    ui.timer(1.0, _refresh_diag)

                with ui.card().classes('w-1/2'):
                    ui.label('Kernel Errors').classes('text-base font-semibold')

                    err_short = ui.label('No error').classes('text-xs')
                    err_trace = ui.code('').classes('w-full')
                    err_trace.style('height: 260px; overflow: auto;')

                    def _refresh_error() -> None:
                        e = kernel_state.get('error')
                        tb = kernel_state.get('error_tb')
                        if not e:
                            err_short.text = 'No error'
                            err_trace.content = ''
                        else:
                            err_short.text = f'Last error: {e}'
                            err_trace.content = str(tb or '')
                        err_trace.update()

                    def _clear_error() -> None:
                        kernel_state['error'] = None
                        kernel_state['error_tb'] = None
                        _refresh_error()

                    _refresh_error()
                    ui.timer(0.5, _refresh_error)
                    with ui.row().classes('w-full justify-end'):
                        ui.button('Clear', on_click=_clear_error)

            with ui.card().classes('w-full m-4'):
                ui.label('Logs').classes('text-base font-semibold')

                log_info = ui.label('').classes('text-xs text-gray-500')
                log_lines_input = ui.number(label='Tail lines', value=200, min=10, max=2000)
                log_auto = ui.switch('Auto refresh', value=True)
                log_view = ui.code('').classes('w-full')
                log_view.style('height: 320px; overflow: auto;')

                def _pick_log_file(path_str: str) -> tuple[Path, list[Path]]:
                    p = Path(path_str).expanduser()
                    if p.is_absolute():
                        return p, [p]
                    cands = [DATA_DIR / p, Path.cwd() / p]
                    for c in cands:
                        if c.exists():
                            return c, cands
                    return cands[0], cands

                def _tail_file(path: Path, *, max_lines: int, max_bytes: int = 200_000) -> str:
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

                def _refresh_logs() -> None:
                    cfg = _load_ciel_config_from_state(state)
                    p, cands = _pick_log_file(str(cfg.log_path))
                    exists = 'yes' if p.exists() else 'no'
                    log_info.text = f'log_path: {cfg.log_path} | resolved: {p} | exists: {exists} | candidates: {", ".join(str(x) for x in cands)}'

                    if not bool(log_auto.value):
                        return
                    max_lines = int(log_lines_input.value or 200)
                    log_view.content = _tail_file(p, max_lines=max_lines)
                    log_view.update()

                _refresh_logs()
                ui.timer(1.0, _refresh_logs)

        with ui.tab_panel('Settings'):
            with ui.row().classes('w-full p-4 gap-4'):
                with ui.card().classes('w-1/2'):
                    ui.label('Runtime').classes('text-base font-semibold')

                    max_upload_input = ui.number(label='Max upload (MB)', value=int(MAX_UPLOAD_MB), min=1, max=200_000)
                    max_download_input = ui.number(label='Max download (MB)', value=int(MAX_DOWNLOAD_MB), min=1, max=200_000)
                    allow_pip_install_input = ui.switch('Allow pip install from UI', value=bool(allow_pip_install))

                with ui.card().classes('w-1/2'):
                    ui.label('CielConfig').classes('text-base font-semibold')

                    enable_gpu_input = ui.switch('Enable GPU (cupy if available)', value=bool(ciel_cfg.enable_gpu))
                    enable_numba_input = ui.switch('Enable numba (if available)', value=bool(ciel_cfg.enable_numba))
                    compute_mode_input = ui.select(
                        ['fft', 'nofft'],
                        value=str(ciel_cfg.compute_mode),
                        label='Default compute mode',
                    )
                    log_path_input = ui.input('Log path', value=str(ciel_cfg.log_path)).classes('w-full')
                    ethics_min_coherence_input = ui.number(
                        label='Ethics min coherence',
                        value=float(ciel_cfg.ethics_min_coherence),
                        min=0.0,
                        max=1.0,
                        step=0.01,
                    )
                    ethics_block_input = ui.switch(
                        'Block on ethics violation',
                        value=bool(ciel_cfg.ethics_block_on_violation),
                    )
                    dataset_path_input = ui.input(
                        'Dataset path (optional)',
                        value='' if ciel_cfg.dataset_path is None else str(ciel_cfg.dataset_path),
                    ).classes('w-full')

            effective_code = ui.code('').classes('w-full')
            dirty_label = ui.label('').classes('text-xs text-gray-500 px-4')

            def _defaults_dict() -> dict[str, Any]:
                return {
                    'max_upload_mb': 4096,
                    'max_download_mb': 8192,
                    'allow_pip_install': False,
                    'ciel_config': {
                        'enable_gpu': True,
                        'enable_numba': True,
                        'compute_mode': 'fft',
                        'log_path': 'logs/reality.jsonl',
                        'ethics_min_coherence': 0.4,
                        'ethics_block_on_violation': True,
                        'dataset_path': None,
                    },
                }

            def _state_dict() -> dict[str, Any]:
                cfg = _load_ciel_config_from_state(state)
                return {
                    'max_upload_mb': int(state.get('max_upload_mb') or MAX_UPLOAD_MB),
                    'max_download_mb': int(state.get('max_download_mb') or MAX_DOWNLOAD_MB),
                    'allow_pip_install': bool(state.get('allow_pip_install'))
                    if 'allow_pip_install' in state
                    else bool(allow_pip_install),
                    'ciel_config': {
                        'enable_gpu': bool(cfg.enable_gpu),
                        'enable_numba': bool(cfg.enable_numba),
                        'compute_mode': str(cfg.compute_mode),
                        'log_path': str(cfg.log_path),
                        'ethics_min_coherence': float(cfg.ethics_min_coherence),
                        'ethics_block_on_violation': bool(cfg.ethics_block_on_violation),
                        'dataset_path': None if cfg.dataset_path in (None, '') else str(cfg.dataset_path),
                    },
                }

            def _inputs_dict() -> dict[str, Any]:
                return {
                    'max_upload_mb': int(max_upload_input.value or MAX_UPLOAD_MB),
                    'max_download_mb': int(max_download_input.value or MAX_DOWNLOAD_MB),
                    'allow_pip_install': bool(allow_pip_install_input.value),
                    'ciel_config': {
                        'enable_gpu': bool(enable_gpu_input.value),
                        'enable_numba': bool(enable_numba_input.value),
                        'compute_mode': str(compute_mode_input.value or 'fft'),
                        'log_path': str(log_path_input.value or 'logs/reality.jsonl'),
                        'ethics_min_coherence': float(ethics_min_coherence_input.value or 0.4),
                        'ethics_block_on_violation': bool(ethics_block_input.value),
                        'dataset_path': None
                        if (dataset_path_input.value or '') == ''
                        else str(dataset_path_input.value),
                    },
                }

            def _fill_inputs(d: dict[str, Any]) -> None:
                max_upload_input.value = int(d.get('max_upload_mb') or 4096)
                max_download_input.value = int(d.get('max_download_mb') or 8192)
                allow_pip_install_input.value = bool(d.get('allow_pip_install'))

                cfg = d.get('ciel_config')
                if not isinstance(cfg, dict):
                    cfg = {}
                enable_gpu_input.value = bool(cfg.get('enable_gpu', True))
                enable_numba_input.value = bool(cfg.get('enable_numba', True))
                compute_mode_input.value = str(cfg.get('compute_mode', 'fft'))
                log_path_input.value = str(cfg.get('log_path', 'logs/reality.jsonl'))
                ethics_min_coherence_input.value = float(cfg.get('ethics_min_coherence', 0.4))
                ethics_block_input.value = bool(cfg.get('ethics_block_on_violation', True))
                dataset_path_input.value = '' if cfg.get('dataset_path') in (None, '') else str(cfg.get('dataset_path'))

            def _refresh_effective() -> None:
                effective_code.content = json.dumps(_state_dict(), ensure_ascii=False, indent=2)
                effective_code.update()

            def _refresh_dirty() -> None:
                dirty = _inputs_dict() != _state_dict()
                dirty_label.text = 'Unsaved changes' if dirty else 'All changes applied'

            _refresh_effective()
            _refresh_dirty()
            ui.timer(0.5, _refresh_dirty)

            def _apply_settings() -> None:
                nonlocal allow_pip_install
                global MAX_UPLOAD_MB, MAX_DOWNLOAD_MB

                d = _inputs_dict()
                state['max_upload_mb'] = int(d['max_upload_mb'])
                state['max_download_mb'] = int(d['max_download_mb'])
                allow_pip_install = bool(d['allow_pip_install'])
                state['allow_pip_install'] = allow_pip_install

                cfg_raw = d.get('ciel_config')
                if not isinstance(cfg_raw, dict):
                    cfg_raw = {}
                cfg = CielConfig(
                    enable_gpu=bool(cfg_raw.get('enable_gpu', True)),
                    enable_numba=bool(cfg_raw.get('enable_numba', True)),
                    compute_mode=str(cfg_raw.get('compute_mode', 'fft')),
                    log_path=str(cfg_raw.get('log_path', 'logs/reality.jsonl')),
                    ethics_min_coherence=float(cfg_raw.get('ethics_min_coherence', 0.4)),
                    ethics_block_on_violation=bool(cfg_raw.get('ethics_block_on_violation', True)),
                    dataset_path=None if cfg_raw.get('dataset_path') in (None, '') else str(cfg_raw.get('dataset_path')),
                )
                _write_ciel_config_to_state(state, cfg)

                MAX_UPLOAD_MB = int(state.get('max_upload_mb') or MAX_UPLOAD_MB)
                MAX_DOWNLOAD_MB = int(state.get('max_download_mb') or MAX_DOWNLOAD_MB)

                try:
                    limits_label.text = f'Limits: upload {MAX_UPLOAD_MB} MB, download {MAX_DOWNLOAD_MB} MB'
                except Exception:
                    pass

                try:
                    mode_select.value = str(cfg.compute_mode)
                except Exception:
                    pass

                _save_state(state)
                _refresh_effective()
                _refresh_dirty()
                ui.notify('Applied settings')

            def _discard_settings() -> None:
                _fill_inputs(_state_dict())
                _refresh_dirty()
                ui.notify('Discarded changes')

            def _reset_defaults() -> None:
                _fill_inputs(_defaults_dict())
                _refresh_dirty()
                ui.notify('Reset to defaults (not applied yet)')

            with ui.row().classes('w-full justify-end p-4 gap-2'):
                ui.button('Reset defaults', on_click=_reset_defaults)
                ui.button('Discard', on_click=_discard_settings)
                ui.button('Apply', on_click=_apply_settings)

    host = os.environ.get('CIEL_HOST', '127.0.0.1')
    preferred_port = int(os.environ.get('CIEL_PORT', '8080'))
    port = _pick_port(host, preferred_port)
    if port != preferred_port:
        print(f'Port {preferred_port} is busy; using {port} instead', flush=True)

    for _ in range(3):
        try:
            print(f'NiceGUI starting on http://{host}:{port}', flush=True)
            ui.run(title='CIEL/Ω', reload=False, host=host, port=port)
            break
        except OSError as ex:
            if getattr(ex, 'errno', None) != 98:
                raise
            port = _pick_port(host, int(port) + 1)
            print(f'Port busy; retry on http://{host}:{port}', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
