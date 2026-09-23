from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OMEGA_ROOT = ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"


def test_engine_default_factories_construct_without_hang() -> None:
    code = r'''
import sys
from pathlib import Path
root = Path.cwd() / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"
omega = root / "ciel_omega"
sys.path.insert(0, str(root))
sys.path.insert(0, str(omega))

def mark(name):
    print(name, file=sys.stderr, flush=True)

from ciel_omega.config.ciel_config import CielConfig
from ciel_omega.fields.intention_field import IntentionField
from ciel_omega.ciel_wave.fourier_kernel import SpectralWaveField12D
from ciel_omega.memory.monolith.orchestrator import UnifiedMemoryOrchestrator
from ciel_omega.integration.information_flow import InformationFlow
from ciel_omega.memory.orchestrator import HolonomicMemoryOrchestrator
from ciel_omega.ciel.orbital_memory_persistence import PersistentOrbitalSectorMemory
from ciel_omega.bridge.memory_core_phase_bridge import MemoryCorePhaseBridge
from ciel_omega.emotion.emotion_core import EmotionCore
from ciel_omega.emotion.cqcl.emotional_collatz import EmotionalCollatzEngine
from ciel_omega.ethics.ethics_guard import EthicsGuard
from ciel_omega.ethics.ethical_engine import EthicalEngine
from ciel_omega.fields.soul_invariant import SoulInvariant
from ciel_omega.calibration.rcde import RCDECalibratorPro
from ciel_omega.mathematics.lie4.collatz_lie4 import ColatzLie4Engine

factories = [
    ("config", CielConfig),
    ("intention", IntentionField),
    ("kernel", SpectralWaveField12D),
    ("memory", UnifiedMemoryOrchestrator),
    ("information_flow", InformationFlow),
    ("nonlocal_memory", HolonomicMemoryOrchestrator),
    ("sector_memory_store", lambda: PersistentOrbitalSectorMemory(HolonomicMemoryOrchestrator())),
    ("bridge", MemoryCorePhaseBridge),
    ("emotion", EmotionCore),
    ("cqcl", EmotionalCollatzEngine),
    ("ethics_guard", lambda: EthicsGuard(block=False)),
    ("ethics_engine", EthicalEngine),
    ("soul", SoulInvariant),
    ("rcde", RCDECalibratorPro),
    ("lie4", ColatzLie4Engine),
]
for name, factory in factories:
    mark(name + ":start")
    factory()
    mark(name + ":done")
'''
    env = os.environ.copy()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        pytest.fail(f"engine component construction timed out; trace:\n{stderr}")
    assert proc.returncode == 0, proc.stderr
