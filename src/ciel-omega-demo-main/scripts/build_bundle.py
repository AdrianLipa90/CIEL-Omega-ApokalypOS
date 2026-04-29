from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _rm_tree(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    dist = Path(os.environ.get('CIEL_BUNDLE_DIST', str(root / 'dist_bundle')))
    work = Path(os.environ.get('CIEL_BUNDLE_WORK', str(root / 'build_bundle')))
    spec = Path(os.environ.get('CIEL_BUNDLE_SPEC', str(root / 'spec_bundle')))

    _rm_tree(dist)
    _rm_tree(work)
    _rm_tree(spec)

    sep = ';' if sys.platform.startswith('win') else ':'
    logo_src = root / 'main' / 'Logo1.png'
    add_data_logo = f"{logo_src}{sep}main"
    entry_omega_src = root / 'scripts' / 'entry_omega.py'
    add_data_entry_omega = f"{entry_omega_src}{sep}scripts"
    entry_omega_runpy_src = root / 'scripts' / 'entry_omega_runpy.py'
    add_data_entry_omega_runpy = f"{entry_omega_runpy_src}{sep}scripts"

    base = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--noconfirm',
        '--clean',
        '--distpath',
        str(dist),
        '--workpath',
        str(work),
        '--specpath',
        str(spec),
    ]

    subprocess.check_call(
        base
        + [
            '--onefile',
            '--name',
            'ciel-omega',
            str(root / 'scripts' / 'entry_omega.py'),
            '--add-data',
            add_data_logo,
            '--add-data',
            add_data_entry_omega,
            '--add-data',
            add_data_entry_omega_runpy,
            '--collect-all',
            'nicegui',
        ]
    )

    subprocess.check_call(
        base
        + [
            '--onefile',
            '--name',
            'ciel-cli',
            str(root / 'scripts' / 'entry_cli.py'),
        ]
    )

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
