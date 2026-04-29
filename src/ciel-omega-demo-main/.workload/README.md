# `.workload/` – opis zawartości

Katalog `.workload/` zawiera zestaw **eksperymentalnych / roboczych modułów Python** związanych z projektem **CIEL/Ω Quantum Consciousness Suite**. W praktyce jest to „warsztat” z:

- kolejnymi iteracjami „kernelów” (rdzeni symulacji),
- dużymi, monolitycznymi integracjami (LIE₄, 4D, „paradoxes”),
- paczkami rozszerzeń w stylu **Batch N / extN** (komponenty do spięcia z innymi modułami),
- narzędziami pobocznymi: emocje, pamięć, EEG, mosty do backendu.

Większość plików ma sekcję uruchomieniową (`if __name__ == "__main__":`) z demonstracją.

## Rdzenie / główne implementacje

- **`definitekernel.py`**
  Implementacja „Unified Reality Kernel” (CIEL/0) z:
  - zestawem stałych (`RealityConstants`),
  - prawami/operatorem ewolucji (`UnifiedRealityLaws`, `UnifiedRealityKernel`),
  - metrykami (koherencja, czystość, fidelity),
  - rozbudowaną wizualizacją (`UnifiedRealityVisualizer`) i demem.

- **`cielnofft.py`**
  „CIEL/0 Complete Unified Framework” w 2D (siatka x–t) z:
  - polami `I`, `S`, `τ`, `F`, `Λ0`, rezonansami i masą,
  - ewolucją w stylu różnic skończonych (bez FFT),
  - modułami analizy/wykresów i weryfikacją aksjomatów.

- **`cielquantum.py`**
  „CIEL/0 – Quantum‑Relativistic Reality Kernel” w wydaniu bardziej „QFT‑like”:
  - siatka 3D+1 (`Grid`), stos pól (`FieldStack`), szkielety Lagrangian/Hamiltonian,
  - stabilny ewolwer (CFL, warunki absorbujące),
  - hooki: ζ (Riemann), Collatz, Banach‑Tarski,
  - eksport obserwabli do HDF5 (`Observables`, domyślnie `ciel0_run.h5`).

## Duże integracje (LIE₄ / 4D / „paradoxy”)

- **`lie4full.py`**
  „CIEL/0 + LIE₄” (v11.2) – duży, samodzielny moduł integrujący:
  - pola, Lagrangian, dynamikę,
  - algebra LIE₄ i pole świadomości,
  - warstwę semantyczną (SCL) + „semantic‑physics bridge”,
  - tryb wizualizacji i walidację stabilności.

- **`parlie4.py`**
  „CIEL/0 + LIE₄ + 4D Universal Law Engine” (v12.1) – integracja 4D silnika (Schrödinger, Ramanujan, Collatz/TwinPrimes, Riemann ζ, Banach‑Tarski) i projekcji do pól 2D/3D.

- **`paradoxes.py`**
  „Ultimate … Paradoxes Integrated” (v13.0) – największy monolit:
  - katalog „paradox operators”,
  - 4D engine z wieloma warstwami/fieldami,
  - dużo zależności naukowych (m.in. `sympy`, `networkx`) i długie demo.

## Rozszerzenia (paczki `ext*.py`)

Poniższe pliki wyglądają jak „batch‑patches” – pojedyncze moduły zawierające nowe klocki, często „no‑FFT” i gotowe do ręcznego podpięcia.

- **`ext1.py`** – Minimal Extensions Pack
  - konfiguracja (`CielConfig`), logger (`RealityLogger`), strażnik etyki (`EthicsGuard`)
  - lekki operator Σ (wersja FFT‑owa),
  - backend GPU/CPU (`GPUEngine`, opcjonalnie `cupy`/`numba`),
  - dataset glyphów + prosty interpreter (`GlyphDataset`, `GlyphInterpreter`),
  - funkcje „attach_*” do ręcznego użycia.

- **`ext2.py`** – Batch Pack (no‑FFT)
  - `CSFSimulator`, `RCDECalibrated`, kilka „paradox resolvers”,
  - prosty „QuantumOptimiser” (strojenie stałych),
  - `CIELFullKernelLite` jako mini‑orchestrator.

- **`ext3.py`** – Batch3 (Quantum + Memory + Ethics + Σ + I/O + Bootstrap)
  - stałe fizyczne, operator Σ, pamięć (JSONL), loader danych (także HTTP),
  - `Bootstrap.ensure()` zawiera **auto‑instalację pip** (warto uważać przy uruchamianiu).

- **`ext4.py`** – Batch4 (Ethical Engine + Decay + Color Mapper)
  - silnik/monitor etyczny (`EthicalEngine`, `EthicalMonitor`),
  - funkcje tłumienia/konwersji energii, prosta paleta kolorów.

- **`ext5.py`** – Batch5 (Lie4 + Σ‑series + ParadoxFilters + VisualCore)
  - `Lie4MatrixEngine` (generatory i komutatory 4×4),
  - `SigmaSeries` (Σ(t)),
  - filtry stabilizujące i przygotowanie tensorów wizualnych.

- **`ext6.py`** – Batch6 (RealityExpander + UnifiedSigmaField + PsychField)
  - nieliniowy „rozrost” pola (dyfuzja + wzrost),
  - „żywe Σ(x,t)”,
  - empatyczna interakcja pól.

- **`ext7.py`** – Batch7 (część 1 i 2 w jednym pliku)
  - `QuantumResonanceKernel` + `CrystalFieldReceiver`,
  - `EEGProcessor`, `RealTimeController`, `VoiceMemoryUI`.

- **`ext8.py`** – Batch8 (Symbolic Kit)
  - loader datasetów CVOS (JSON/TXT),
  - `GlyphNodeInterpreter`, `GlyphPipeline`, `SymbolicBridge`.

- **`ext9.py`** – Batch9 (Emotion + Empathy + EEG→Affect)
  - rdzeń emocji (`EmotionCore`), pole afektu, empatia,
  - mapper EEG→emocje i orkiestrator afektywny.

- **`ext10.py`** – Batch10 (Cognitive Loop)
  - pętla poznawcza: percepcja → intuicja → predykcja → decyzja,
  - orkiestrator z hookami dostawców pól.

- **`ext17.py`** – Batch17 (Experimental Lab)
  - `SchumannClock`, `OmegaDriftCore`, `RCDECalibrator`,
  - rejestr/runner eksperymentów i zestaw 10 micro‑testów.

- **`ext18.py`** – Batch18 (Drift & Memory Layer)
  - rozszerzony dryf Ω (sweep harmoniczny, jitter), rytuał boot,
  - RCDE „Pro”, równoległy rezonans między nodami, pamięć długoterminowa,
  - eksperymentalny most Collatz ↔ LIE₄.

- **`ext19.py`** – Batch19 (CSF2 + Pamięć/Introspekcja + Stress + BackendGlue)
  - stan CSF2 (Ψ–Σ–Λ–Ω), synchronizacja pamięci, introspekcja,
  - „glue” do zewnętrznego backendu (`cielFullQuantumCore` – referencja interfejsu).

- **`ext20.py`** – Batch20 (Backend Bridge & Runtime Orchestrator)
  - spina elementy Batch17/19 do backendu (adapter + runtime),
  - tryb awaryjny, gdy backend nie jest dostępny.

- **`ext21.py`** – Batch21 (Adam Core Extensions + Ritual Module)
  - trwała pamięć interakcji (`AdamMemoryKernel`, zapis JSON),
  - optymalizacja rezonansu odpowiedzi, tracker misji/zadań,
  - moduł rytualny (operatory z obrazów, sekwencje rytuałów),
  - wrapper `AdamCore` z demem bootstrap.

## Pozostałe

- **`extemot.py`**
  „Emotional Collatz Engine (CQCL layer)” – kompiluje intencję do profilu emocji, steruje zmodyfikowaną transformacją Collatza i liczy metryki.

- **`extfwcku.py`**
  Minimalny, testowy stub „spectral wave field” (`FourierWaveConsciousnessKernel12D` / `SpectralWaveField12D`) – wygląda na plik utrzymywany pod testy/importy.

## Uwagi praktyczne

- **Zależności**: w tych plikach pojawiają się m.in. `numpy`, `scipy`, `matplotlib`, `sympy`, `networkx`, `h5py`, `requests`, opcjonalnie `cupy`/`numba`.
- **Skutki uboczne**: część dem zapisuje pliki (np. HDF5), część uruchamia wizualizacje, a `ext3.py` może próbować instalować pakiety przez `pip`.
- **Charakter roboczy**: nazwa folderu sugeruje, że to warstwa „work-in-progress”/sandbox, a niekoniecznie stabilne API biblioteki.
