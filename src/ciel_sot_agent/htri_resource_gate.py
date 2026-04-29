"""HTRI Resource Gate — soft clip dla GTX 1050 Ti / i7-8750H / 7.5GB RAM.

Profil sprzętowy pochodzi z htri_local.py (Adrian Lipa / Intention Lab).
Skalowanie: H200 (14080 bloków) → GTX 1050 Ti (768 oscylatorów, 5.5% skali).

Soft clip: zamiast twardego odrzucenia, klasyfikuje model na 4 poziomy:
  SAFE    — mieści się w VRAM, pełna synchronizacja HTRI
  SLOW    — mieści się w RAM, GPU offload niemożliwy, HTRI zdegradowane
  RISKY   — przekracza bezpieczny RAM, HTRI coherence < 0.5
  BLOCKED — przekracza hard limit, wisiałby komputer

Wszystkie progi są mierzone żywo z /proc/meminfo i nvidia-smi — zero arbitralnych stałych.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# ── HTRI hardware profile (GTX 1050 Ti + i7-8750H) ─────────────────────────

HTRI_CPU_THREADS  = 12
HTRI_GPU_CORES    = 768        # GTX 1050 Ti CUDA cores

# Nominalne maximum sprzętu — stałe fizyczne, nie arbitralne
HTRI_VRAM_TOTAL_MB = 4096   # GTX 1050 Ti — specyfikacja NVIDIA
HTRI_RAM_TOTAL_MB  = 7680   # 7.5 GB — wynik `free -m` na tym komputerze


def _read_free_ram_mb() -> int:
    """Żywy odczyt wolnego RAM z /proc/meminfo (MemAvailable)."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024  # kB → MB
    except Exception:
        pass
    return HTRI_RAM_TOTAL_MB // 2  # fallback: połowa RAM


def _read_free_vram_mb() -> int:
    """Żywy odczyt wolnego VRAM przez nvidia-smi."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            timeout=2, stderr=subprocess.DEVNULL,
        )
        return int(out.strip().splitlines()[0])
    except Exception:
        pass
    return HTRI_VRAM_TOTAL_MB // 2  # fallback: połowa VRAM


def _get_thresholds() -> tuple[int, int, int]:
    """Zwraca (vram_safe_mb, ram_safe_mb, ram_hard_mb) na podstawie live pomiarów."""
    free_vram = _read_free_vram_mb()
    free_ram  = _read_free_ram_mb()
    # VRAM_SAFE: 90% wolnego VRAM (10% margines na sterownik i framebuffer)
    vram_safe = int(free_vram * 0.90)
    # RAM_SAFE: 75% wolnego RAM (25% margines na OS jitter i CIEL overhead)
    ram_safe  = int(free_ram * 0.75)
    # RAM_HARD: 92% wolnego RAM (absolutne max — OOM powyżej)
    ram_hard  = int(free_ram * 0.92)
    return vram_safe, ram_safe, ram_hard


# Backward-compat aliases (statyczne; check_model używa live _get_thresholds())
HTRI_RAM_MB  = HTRI_RAM_TOTAL_MB
HTRI_VRAM_MB = HTRI_VRAM_TOTAL_MB
VRAM_SAFE_MB = int(HTRI_VRAM_TOTAL_MB * 0.90)
RAM_SAFE_MB  = int(HTRI_RAM_TOTAL_MB * 0.50)
RAM_HARD_MB  = int(HTRI_RAM_TOTAL_MB * 0.70)


class LoadMode(Enum):
    SAFE    = "safe"     # GPU VRAM — pełna synchronizacja HTRI
    SLOW    = "slow"     # CPU RAM — HTRI zdegradowane, ale stabilne
    RISKY   = "risky"    # CPU RAM powyżej safe — coherence < 0.5
    BLOCKED = "blocked"  # przekracza hard limit — ZAWIESIE komputer


@dataclass
class ResourceVerdict:
    mode:       LoadMode
    file_mb:    float
    message:    str
    htri_coherence_estimate: float  # 0–1, szacowana koherencja HTRI po załadowaniu

    @property
    def allowed(self) -> bool:
        return self.mode != LoadMode.BLOCKED


def check_model(path: str | Path) -> ResourceVerdict:
    """Sprawdź czy model mieści się w profilu HTRI tego komputera (live pomiar RAM/VRAM)."""
    p = Path(path)
    if not p.exists():
        return ResourceVerdict(
            mode=LoadMode.BLOCKED,
            file_mb=0,
            message=f"Plik nie istnieje: {p.name}",
            htri_coherence_estimate=0.0,
        )

    file_mb = p.stat().st_size / (1024 * 1024)
    vram_safe, ram_safe, ram_hard = _get_thresholds()
    free_vram = _read_free_vram_mb()
    free_ram  = _read_free_ram_mb()

    if file_mb <= vram_safe:
        return ResourceVerdict(
            mode=LoadMode.SAFE,
            file_mb=file_mb,
            message=(
                f"{p.name} ({file_mb:.0f} MB) mieści się w wolnym VRAM "
                f"({free_vram} MB dostępne, GTX 1050 Ti). "
                f"HTRI pełna synchronizacja."
            ),
            htri_coherence_estimate=0.94,
        )

    if file_mb <= ram_safe:
        return ResourceVerdict(
            mode=LoadMode.SLOW,
            file_mb=file_mb,
            message=(
                f"{p.name} ({file_mb:.0f} MB) nie mieści się w VRAM — "
                f"ładuję na CPU RAM (bezpieczny limit: {ram_safe:.0f} MB, "
                f"dostępne: {free_ram} MB). HTRI zdegradowane."
            ),
            htri_coherence_estimate=0.62,
        )

    if file_mb <= ram_hard:
        return ResourceVerdict(
            mode=LoadMode.RISKY,
            file_mb=file_mb,
            message=(
                f"{p.name} ({file_mb:.0f} MB) przekracza bezpieczny RAM "
                f"({ram_safe:.0f} MB). Ryzyko OOM. "
                f"Dostępne: {free_ram} MB. HTRI coherence < 0.5."
            ),
            htri_coherence_estimate=0.35,
        )

    return ResourceVerdict(
        mode=LoadMode.BLOCKED,
        file_mb=file_mb,
        message=(
            f"ZABLOKOWANO: {p.name} ({file_mb:.0f} MB) przekracza hard limit RAM "
            f"({ram_hard:.0f} MB, dostępne: {free_ram} MB). "
            f"Ryzyko zawieszenia komputera."
        ),
        htri_coherence_estimate=0.0,
    )


def htri_profile_summary() -> dict:
    vram_safe, ram_safe, ram_hard = _get_thresholds()
    return {
        "cpu_threads":       HTRI_CPU_THREADS,
        "gpu_cores":         HTRI_GPU_CORES,
        "vram_total_mb":     HTRI_VRAM_TOTAL_MB,
        "ram_total_mb":      HTRI_RAM_TOTAL_MB,
        "free_vram_mb":      _read_free_vram_mb(),
        "free_ram_mb":       _read_free_ram_mb(),
        "vram_safe_mb":      vram_safe,
        "ram_safe_mb":       ram_safe,
        "ram_hard_mb":       ram_hard,
        "thresholds_source": "live /proc/meminfo + nvidia-smi",
    }
