# raport2.md — Integracja UI (NiceGUI) z `main/` + debugging end-to-end

Data: 2025-12-16 19:18:00 UTC

## 1. Zakres wykonanych prac od `raport1.md`

- Dodano integrację NiceGUI z modułami `main/` poprzez nową zakładkę **Kernel** w `ciel_omega_app.py`.
- UI korzysta z rejestru kernelów `main.kernels.registry.KERNELS` i buduje kernel w zależności od parametrów.
- Dodano pętlę wykonywania `step(dt=...)` w tle (non-blocking) oraz wykres realtime metryk.

## 2. Zmiany w `ciel_omega_app.py`

### 2.1 Nowe importy (integracja z `main/`)

- `from main.core.ciel_constants import DEFAULT_CONSTANTS`
- `from main.core.config import CielConfig`
- `from main.kernels.registry import KERNELS`

### 2.2 Nowa zakładka: `Kernel`

Dodano nowy tab w UI:

- `Dashboard`
- `Kernel`
- `Chat`
- `Files`
- `Models`

Funkcje zakładki `Kernel`:

- wybór kernela: `ciel0`, `ciel0_framework`, `unified_reality`
- wybór trybu: `fft` / `nofft`
- parametry: `grid`, `length` (dla FFT), `dt`
- przyciski: `Build`, `Start`, `Stop`, `Reset`
- metryki:
  - etykieta kroku
  - status (idle/ready/running/error)
  - ostatnie metryki jako JSON
- wykres `ui.echart` (series):
  - `resonance_mean`
  - `mass_mean`
  - `lambda0_mean`

### 2.3 Runner/loop

- `ui.timer(0.2, ...)` uruchamia cyklicznie `asyncio.create_task(_kernel_tick())`.
- `_kernel_tick()`:
  - zabezpieczenia: `running`, `busy`, `kernel != None`
  - wykonanie `kernel.step(dt=dt)` przez `asyncio.to_thread`, aby nie blokować UI
  - aktualizacja etykiet i danych wykresu
  - limit historii do 200 punktów
  - przy wyjątku: zatrzymanie runnera i pokazanie błędu w statusie

## 3. Debugging / testy

### 3.1 Kompilacja

- `python3 -m py_compile ciel_omega_app.py` → OK

### 3.2 Spójność z CLI

Po integracji UI wykonano sanity-check, że CLI nadal działa:

- `python3 ciel_cli.py list` → OK
- `python3 ciel_cli.py omega18 --json` → OK

## 4. Znane ograniczenia (świadome)

- `unified_reality` nie zwraca `lambda0_mean`, więc wykres pokazuje `None` dla tej serii.
  - To nie jest błąd runtime, ale oznacza niespójność metryk między kernelami.
  - Rekomendacja: ustandaryzować metryki (np. zawsze zwracać `lambda0_mean`, nawet jeśli 0/None).

- Zakładka `Kernel` jest pierwszą integracją UI↔`main/` i nie obejmuje jeszcze:
  - `omega18` demo w UI
  - `experiments` (Batch17) w UI
  - `cognition` w UI

## 5. Rekomendacje następnych kroków

- Dodać w UI zakładkę `Experiments` (Batch17) i `Omega18` (demo), bazując na istniejącym kodzie z CLI.
- Ujednolicić kontrakt metryk kernelów (klucze + typy) i dodać walidację.
- Dodać możliwość zapisu logu metryk do pliku (np. przez `main/core/reality_logger.py`).

## 6. Status na koniec raportu

- NiceGUI: ma podstawową integrację z `main/` poprzez nową zakładkę `Kernel`.
- CLI: działa po zmianach.
- Debugging: kompilacja + podstawowe sanity-checki przeszły.

## 7. Dodatkowy debugging (sandbox) + stabilność zależności

- `ciel_omega_app.py` crashował przy braku `python-docx` / `pypdf` przez importy na poziomie modułu.
- Naprawiono to tak, aby importy `pypdf` oraz `python-docx` były wykonywane dopiero w momencie podglądu pliku danego typu.
- Brak `nicegui` jest teraz obsłużony przewidywalnie: uruchomienie kończy się czytelnym komunikatem o brakującej zależności.

## 8. Naprawa architektury entrypointów (runtime w `main/`)

- CLI:
  - dodano `main/apps/cli.py` jako źródło runtime dla CLI,
  - `ciel_cli.py` jest cienkim wrapperem delegującym do `main.apps.cli.main()`.
- UI:
  - dodano `main/apps/omega_app.py` jako źródło runtime dla aplikacji NiceGUI,
  - `ciel_omega_app.py` został ustawiony jako entrypoint delegujący do `main.apps.omega_app.main()` i blokuje import jako moduł.

## 9. Status

- CLI: działa po refaktorze (`python3 ciel_cli.py list`).
- UI: przy braku `nicegui` kończy się kontrolowanym komunikatem (zamiast crasha na importach).

---

Koniec raportu.
