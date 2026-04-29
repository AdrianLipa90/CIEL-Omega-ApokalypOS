# raport1.md — Audyt portu + debugging (CIEL/Ω)

Data: 2025-12-14 22:15:06 UTC

## 1. Cel

- Migracja kodu z folderu `.workload/` do modułowego pakietu `main/`.
- Brak importów runtime z `.workload/`.
- Dwa tryby obliczeń (FFT i no-FFT) tam gdzie ma sens.
- Działający CLI do uruchamiania kernelów/eksperymentów/dem.
- Docelowo integracja NiceGUI (UI) z modułami `main/`.

## 2. Stan repozytorium (moduły w `main/`)

Struktura:

- `main/core/`
  - `ciel_constants.py` — kanoniczne stałe + aliasy nazw.
  - `physical.py` — re-export z `ciel_constants`.
  - `compute_backend.py` — `ComputeBackend(mode=fft|nofft)`.
  - `sigma.py` — `SoulInvariantOperator` używający backendu.
  - `ethics.py` — `EthicsGuard`.
  - `reality_logger.py` — `RealityLogger` (JSONL).
  - `gpu.py` — `GPUEngine` (cupy/numba fallback).
  - `glyphs.py` — `GlyphDataset` + `GlyphInterpreter`.
  - `enums.py` — `RealityLayer`.
  - `config.py` — `CielConfig` (compute_mode, etyka, log_path itp.).

- `main/kernels/`
  - `ciel0_common.py` — baza kernela CIEL0 (wspólna ewolucja) + abstrakcyjny laplasjan.
  - `ciel0_fft.py` — implementacja laplasjanu FFT.
  - `ciel0_nofft.py` — implementacja laplasjanu no-FFT.
  - `ciel0_state.py` — stan dataclass.
  - `factory.py` — wybór kernel FFT/noFFT.
  - `registry.py` — rejestr kernelów (CLI używa `KERNELS`).
  - `unified_reality.py` — port `definitekernel.py` w wersji lite + tryb fft/nofft w gradientach.
  - `ciel0_framework.py` — port stylu `CIEL0Framework` (lite) z trybem fft/nofft.

- `main/cognition/`
  - `cognitive_loop.py` — port `ext10.py` (Perception→Intuition→Prediction→Decision) + `run_demo`.

- `main/experiments/`
  - `lab17.py` — port `ext17.py` (Batch17 experiments) przepięty na `main/omega/*`.

- `main/omega/`
  - `field_ops.py` — `laplacian2`, `field_norm`, `coherence_metric`.
  - `schumann.py` — `SchumannClock`.
  - `drift.py` — `OmegaDriftCore`.
  - `rcde.py` — `RCDECalibrator`.
  - `batch18.py` — port `ext18.py` (OmegaDriftCorePlus, BootRitual, RCDEPro, ResConnectParallel, DissociationAnalyzer, LongTermMemory, CollatzLie4Engine) + `demo`.

## 3. Zestawienie: analizowane pliki `.workload/` → pokrycie w `main/`

### 3.1 `ext1.py` (Extensions Pack)

Pokryte:

- `EthicsGuard` → `main/core/ethics.py`
- `RealityLogger` → `main/core/reality_logger.py`
- `SoulInvariantOperator` → `main/core/sigma.py` (plus `ComputeBackend`)
- `GPUEngine` → `main/core/gpu.py`
- `GlyphDataset`, `GlyphInterpreter` → `main/core/glyphs.py`
- `RealityLayer` → `main/core/enums.py`
- `KernelSpec` → częściowo: jest `main/core/interfaces.py` ale aktualne kernle nie implementują wprost tego protokołu.

Różnice / braki:

- `KernelSpec` nie jest spójnie używany jako kontrakt we wszystkich kernelach (obecnie jest interfejs „konwencją”: `step/run`).

### 3.2 `cielnofft.py` (CIEL0Framework)

Pokryte (lite):

- `I_field`, `tau_field`, `S_field`, `R_field`, `mass_field`, `Lambda0_field` → `main/kernels/ciel0_common.py` + `ciel0_framework.py`.
- Laplasjan no-FFT i FFT (w zależności od implementacji).

Braki:

- `F_field` (wektorowy aether), tensory krzywizny (`Ricci_tensor`, `Einstein_tensor`).
- Funkcje oparte o SciPy / optymalizację / wykresy.

### 3.3 `cielquantum.py` (Quantized Reality / QFT)

Status:

- Niezaimplementowane jako kernel.

Uzasadnienie techniczne:

- Plik opiera się o ciężkie zależności (`scipy.linalg`, `h5py`, gauge-fixing skeleton, QFTSystem), a dotychczasowy port skupiał się na uruchamialnym rdzeniu NumPy (bez SciPy jako runtime requirement).

### 3.4 `definitekernel.py` (UnifiedRealityKernel)

Pokryte:

- Law1–Law4 (quantization, mass emergence, temporal flow, ethics preservation) → `main/kernels/unified_reality.py`.

Braki:

- Law5–Law7 (coherence bound, entanglement, information conservation) — nie zaimplementowane w `main/kernels/unified_reality.py`.

### 3.5 `lie4full.py` (Hyper-unified kernel)

Status:

- Nieportowane (poza częścią stałych/aliasów i ogólnej architektury backendów).

### 3.6 `ext10.py` (Cognitive Loop)

Pokryte:

- `PerceptiveLayer`, `IntuitiveCortex`, `PredictiveCore`, `DecisionCore`, `CognitionOrchestrator` → `main/cognition/cognitive_loop.py`.
- CLI: `ciel_cli.py cognition`.

### 3.7 `ext17.py` (Batch17 experiments)

Pokryte:

- `ExpRegistry` + 10 eksperymentów → `main/experiments/lab17.py`.
- CLI: `ciel_cli.py experiments`.

### 3.8 `ext18.py` (Drift & Memory Layer)

Pokryte:

- Port do `main/omega/batch18.py`.
- CLI: `ciel_cli.py omega18`.

## 4. CLI — funkcjonalność i testy

### 4.1 Dostępne komendy

- `python3 ciel_cli.py list`
- `python3 ciel_cli.py run --kernel ... --mode fft|nofft --grid N --steps S --dt DT --every K [--json]`
- `python3 ciel_cli.py cognition [--steps] [--n] [--json]`
- `python3 ciel_cli.py experiments --list [--json]`
- `python3 ciel_cli.py experiments --names a,b,c [--json]`
- `python3 ciel_cli.py omega18 [--steps] [--n] [--json]`

### 4.2 Wyniki smoke-testów (runtime)

Środowisko:

- Python: 3.12.3
- Uwaga: w systemie nie ma `python`, jest `python3`.

Testy wykonane:

- `python3 -m py_compile ciel_cli.py` → OK
- `python3 ciel_cli.py list` → OK (kernle: `ciel0`, `ciel0_framework`, `unified_reality`)
- `python3 ciel_cli.py run --kernel ciel0 --mode nofft --steps 5` → OK
- `python3 ciel_cli.py run --kernel ciel0 --mode fft --steps 5` → OK
- `python3 ciel_cli.py run --kernel unified_reality --mode nofft --steps 3` → OK
- `python3 ciel_cli.py run --kernel unified_reality --mode fft --steps 3` → OK
- `python3 ciel_cli.py run --kernel ciel0_framework --mode fft/nofft --steps 3` → OK
- `python3 ciel_cli.py experiments --list` → OK
- `python3 ciel_cli.py experiments --names VYCH_BOOT_RITUAL --json` → OK
- `python3 ciel_cli.py cognition --json` → OK
- `python3 ciel_cli.py omega18 --json` → OK

Wykryte kwestie jakościowe:

- `UnifiedRealityKernel` często raportuje `ethical_ok=0.0` (w obu trybach). To nie crash, ale sugeruje nieskalibrowane warunki początkowe / bound.

## 5. NiceGUI (`ciel_omega_app.py`) — status integracji z `main/`

Stan faktyczny:

- `ciel_omega_app.py` jest monolitem.
- Nie importuje `main.*` (brak integracji z kernelami/rdzeniem/omega/experiments/cognition).
- Zakładki UI: `Dashboard`, `Chat`, `Files`, `Models`.
- Dashboard pokazuje CPU/RAM procesu, ale nie metryki kernela.

Wniosek:

- Panel aplikacji nie jest jeszcze skonfigurowany do obsługi nowej architektury (brak panelu do wyboru kernela/mode/grid/dt/metryk).

## 6. Rekomendowany plan uzupełnień (kolejność)

- 1) UI: dodać zakładkę `Kernel`/`Reality` i wpiąć `main.kernels.registry.KERNELS`.
- 2) UI: dodać `KernelRunner` (thread/timer) do wykonywania `step()` i aktualizacji wykresów.
- 3) Ujednolicić interfejs kernelów (np. protokół `step(dt=...) -> metrics` dla wszystkich).
- 4) Rozważyć port “heavy”:
  - `cielquantum.py` i/lub `lie4full.py` jako oddzielne, opcjonalne kernle zależne od SciPy/h5py.

## 7. Status na koniec raportu

- CLI: działa.
- Kernle: działają w trybach fft/nofft.
- Batch17/18: działają (CLI).
- NiceGUI: działa jako monolit, ale **nie jest połączone z `main/`**.

---

Koniec raportu.
