"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Lightweight bootstrapper — verify and optionally install core dependencies.

Source: ext3.Bootstrap
"""

from __future__ import annotations

import subprocess
import sys


class Bootstrap:
    """Check that core packages are importable; install missing ones."""

    required = {"numpy": "numpy", "scipy": "scipy", "matplotlib": "matplotlib"}

    @staticmethod
    def ensure():
        print("🔍 Checking core dependencies...")
        for lib, pkg in Bootstrap.required.items():
            try:
                __import__(lib)
                print(f"  ✓ {lib}")
            except ImportError:
                print(f"  ⚠ {lib} missing — installing...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print("  Environment verified ✓")


__all__ = ["Bootstrap"]
