from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.check_call(cmd, cwd=str(cwd), env=env)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--venv', default=os.environ.get('VENV_DIR', '.venv'))
    parser.add_argument(
        '--install-llama',
        action='store_true',
        default=os.environ.get('INSTALL_LLAMA', '0') == '1',
    )
    parser.add_argument(
        '--llama-backend',
        choices=['cpu', 'cuda'],
        default=os.environ.get('LLAMA_BACKEND', 'cpu'),
    )
    args = parser.parse_args(argv)

    if sys.platform.startswith('win'):
        raise SystemExit('This installer is intended for Linux/macOS. Use scripts/install_local.ps1 on Windows.')

    root = Path(__file__).resolve().parents[1]
    venv_dir = Path(args.venv).expanduser()

    _run([sys.executable, '-m', 'venv', str(venv_dir)], cwd=root)

    venv_python = venv_dir / 'bin' / 'python'
    if not venv_python.exists():
        raise SystemExit(f'Venv python not found: {venv_python}')

    _run([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'], cwd=root)

    env = os.environ.copy()
    if args.install_llama and args.llama_backend == 'cuda':
        env['CMAKE_ARGS'] = '-DLLAMA_CUBLAS=on'
        env['FORCE_CMAKE'] = '1'

    if args.install_llama:
        _run([str(venv_python), '-m', 'pip', 'install', '-e', '.[llama]'], cwd=root, env=env)
    else:
        _run([str(venv_python), '-m', 'pip', 'install', '-e', '.'], cwd=root, env=env)

    print('Installed.')
    print(f'Run UI:   {venv_dir}/bin/ciel-omega')
    print(f'Run CLI:  {venv_dir}/bin/ciel-cli list')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
