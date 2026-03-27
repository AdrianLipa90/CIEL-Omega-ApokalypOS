from __future__ import annotations

if __name__ == '__main__':
    from main.apps.omega_app import main

    raise SystemExit(main())

raise ImportError('ciel_omega_app.py is an entrypoint script; import main.apps.omega_app instead.')

import asyncio
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Any, Optional

import psutil
import requests
from main.core.ciel_constants import DEFAULT_CONSTANTS
from main.core.config import CielConfig
from main.kernels.registry import KERNELS


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'ciel_omega_data'
FILES_DIR = DATA_DIR / 'files'
MODELS_DIR = DATA_DIR / 'models'
STATE_PATH = DATA_DIR / 'state.json'


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


try:
    from nicegui import app, ui
except ModuleNotFoundError as e:
    raise SystemExit(
        "Missing dependency: nicegui. Install requirements (e.g. `pip install -r requirements.txt`) to run ciel_omega_app.py."
    ) from e


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
        }
    try:
        return json.loads(STATE_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {
            'models': [],
            'active_model': None,
        }


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


@dataclass
class ModelEntry:
    name: str
    path: str


class LocalChatEngine:
    def __init__(self) -> None:
        self._llama = None
        self._model_path: Optional[str] = None

    def can_use_llama(self) -> bool:
        try:
            import llama_cpp  # noqa: F401

            return True
        except Exception:
            return False

    def is_loaded(self) -> bool:
        return self._llama is not None

    def load(self, model_path: str) -> None:
        from llama_cpp import Llama

        self._llama = Llama(model_path=model_path)
        self._model_path = model_path

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
                result = self._llama.create_chat_completion(messages=messages)
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
            tmp = task.dest.with_suffix(task.dest.suffix + '.part')
            with open(tmp, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
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


_ensure_dirs()
state = _load_state()
engine = LocalChatEngine()

chat_history: list[dict[str, str]] = []


def _get_models_from_state() -> list[ModelEntry]:
    models: list[ModelEntry] = []
    for m in state.get('models', []):
        if isinstance(m, dict) and 'name' in m and 'path' in m:
            models.append(ModelEntry(name=str(m['name']), path=str(m['path'])))
    return models


def _set_active_model(model_path: Optional[str]) -> None:
    state['active_model'] = model_path
    _save_state(state)


def _add_model(name: str, path: str) -> None:
    models = state.get('models', [])
    models.append({'name': name, 'path': path})
    state['models'] = models
    _save_state(state)


ui.query('.nicegui-content').classes('p-0')

with ui.header().classes('items-center justify-between'):
    ui.label('CIEL/Ω — Live Digital Intelligence Engine').classes('text-lg font-semibold')
    with ui.row().classes('items-center gap-2'):
        ui.label().bind_text_from(app, 'urls')

with ui.tabs().classes('w-full') as tabs:
    ui.tab('Dashboard')
    ui.tab('Kernel')
    ui.tab('Chat')
    ui.tab('Files')
    ui.tab('Models')

with ui.tab_panels(tabs, value='Dashboard').classes('w-full'):

    with ui.tab_panel('Dashboard'):
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
            'x': [],
            'resonance': [],
            'mass': [],
            'lambda0': [],
        }

        with ui.row().classes('w-full gap-4 p-4'):
            kernel_select = ui.select(sorted(KERNELS.keys()), value='ciel0', label='Kernel')
            mode_select = ui.select(['fft', 'nofft'], value='fft', label='Mode')
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
            cfg = CielConfig(compute_mode=str(mode_select.value))
            name = str(kernel_select.value)
            grid = int(grid_input.value or 64)
            length = float(length_input.value or 10.0)
            factory = KERNELS[name]
            kernel_state['kernel'] = factory(cfg, grid, DEFAULT_CONSTANTS, length)
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

        with ui.row().classes('w-full justify-end gap-2 px-4 pb-2'):
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
                with ui.scroll_area().classes('w-full').style('height: calc(100vh - 260px)'):
                    chat_container = ui.column().classes('w-full gap-2')

                message_input = ui.textarea(label='Message').classes('w-full')

                async def send_message() -> None:
                    text = (message_input.value or '').strip()
                    if not text:
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
                            while True:
                                chunk = src.read(1024 * 1024)
                                if not chunk:
                                    break
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
                    ui.button('Download', on_click=lambda: (files_table.selected and ui.download.file(files_table.selected[0]['path'])))
                    ui.button('Delete', color='negative', on_click=lambda: file_delete_dialog.open())

                with file_delete_dialog:
                    with ui.card():
                        ui.label('Delete selected file?')
                        with ui.row().classes('justify-end gap-2'):
                            ui.button('Cancel', on_click=file_delete_dialog.close)
                            ui.button('Delete', color='negative', on_click=lambda: (delete_selected_file(), file_delete_dialog.close()))

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

                models_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
                        {'name': 'path', 'label': 'Path', 'field': 'path', 'align': 'left'},
                    ],
                    rows=[],
                    row_key='path',
                    selection='single',
                ).classes('w-full')

                def refresh_models() -> None:
                    rows: list[dict[str, Any]] = []
                    for m in _get_models_from_state():
                        rows.append({'name': m.name, 'path': m.path})
                    models_table.rows = rows
                    models_table.update()

                refresh_models()

                url_input = ui.input('GGUF URL').classes('w-full')
                fname_input = ui.input('Save as (e.g. model.gguf)').classes('w-full')

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

                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Download GGUF', on_click=_start_download)
                    ui.button('Refresh', on_click=refresh_models)

            with ui.card().classes('w-1/2'):
                ui.label('Active Model / Engine').classes('text-base font-semibold')

                llama_available = engine.can_use_llama()
                ui.label(f'llama-cpp-python available: {"yes" if llama_available else "no"}')

                active_path = state.get('active_model')
                active_label = ui.label(f'Active model: {active_path or "(none)"}')

                def set_active_from_selection() -> None:
                    selection = models_table.selected
                    if not selection:
                        ui.notify('Select a model first')
                        return
                    p = selection[0]['path']
                    _set_active_model(p)
                    active_label.text = f'Active model: {p}'

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

                    def _load() -> None:
                        engine.load(model_path)

                    await asyncio.to_thread(_load)
                    ui.notify('Model loaded')

                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Set Active', on_click=set_active_from_selection)
                    ui.button('Load', on_click=load_engine)


ui.run(title='CIEL/Ω', reload=False)
