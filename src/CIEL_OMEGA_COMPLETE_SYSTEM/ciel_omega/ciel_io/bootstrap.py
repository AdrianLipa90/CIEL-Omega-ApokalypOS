"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Lightweight bootstrapper — verify and optionally install core dependencies.

Source: ext3.Bootstrap
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _find_vendor_dir() -> Path | None:
    """Return the vendor wheel directory for offline installs, or None.

    Resolution order:
    1. ``CIEL_VENDOR_PATH`` environment variable (explicit override).
    2. ``packaging/vendor/`` relative to any parent directory that contains
       both ``pyproject.toml`` and ``packaging/``.
    """
    env_path = os.environ.get("CIEL_VENDOR_PATH", "").strip()
    if env_path:
        p = Path(env_path)
        if p.is_dir():
            return p

    # Walk up from this file looking for the repo root (pyproject.toml marker).
    anchor = Path(__file__).resolve()
    for parent in anchor.parents:
        candidate = parent / "packaging" / "vendor"
        if (parent / "pyproject.toml").is_file() and candidate.is_dir():
            return candidate

    return None


class Bootstrap:
    """Check that core packages are importable; install missing ones."""

    required = {"numpy": "numpy", "scipy": "scipy", "matplotlib": "matplotlib"}

    @staticmethod
    def ensure():
        print("🔍 Checking core dependencies...")
        vendor_dir = _find_vendor_dir()
        whl_count = 0
        if vendor_dir is not None:
            whl_count = sum(1 for f in vendor_dir.iterdir() if f.suffix == ".whl" or f.name.endswith(".tar.gz"))
            if whl_count > 0:
                print(f"  📦 Offline mode — using {whl_count} wheel(s) from: {vendor_dir}")

        for lib, pkg in Bootstrap.required.items():
            try:
                __import__(lib)
                print(f"  ✓ {lib}")
            except ImportError:
                print(f"  ⚠ {lib} missing — installing...")
                cmd = [sys.executable, "-m", "pip", "install"]
                if vendor_dir is not None and whl_count > 0:
                    cmd += ["--no-index", "--find-links", str(vendor_dir)]
                cmd.append(pkg)
                subprocess.check_call(cmd)
        print("  Environment verified ✓")


__all__ = ["Bootstrap"]
