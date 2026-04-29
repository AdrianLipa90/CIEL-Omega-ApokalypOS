# raport4.md — GGUF client polish + architektura entrypointów + full sanity/debug

Data: 2025-12-16 20:01:00 UTC

## 1. Cel

- Uporządkować architekturę runtime (entrypointy tylko jako launchery, logika w `main/`).
- Dopięścić klienta (NiceGUI) pod kątem obsługi GGUF: biblioteka modeli, pobieranie/upload, wybór aktywnego modelu, ustawienia inferencji i opcjonalna instalacja backendu.
- Wykonać pełny sanity-check/debugging w sandboxie.

## 2. Zmiany architektoniczne

### 2.1 Entry pointy i runtime

- CLI:
  - Dodano `main/apps/cli.py` jako właściwe źródło runtime.
  - `ciel_cli.py` jest cienkim wrapperem, deleguje do `main.apps.cli.main()`.
- UI:
  - Dodano `main/apps/omega_app.py` jako właściwe źródło runtime dla aplikacji NiceGUI.
  - `ciel_omega_app.py` jest entrypointem delegującym do `main.apps.omega_app.main()` i celowo blokuje import (żeby unikać side-effectów).

### 2.2 `.workload/`

- Zweryfikowano brak runtime importów/referencji do `.workload/` w kodzie Python.

## 3. GGUF — dopięcie klienta

### 3.1 Zarządzanie modelami

W `main/apps/omega_app.py` rozbudowano zakładkę **Models**:

- Biblioteka GGUF bazuje na folderze: `ciel_omega_data/models`.
- Dodano:
  - skan folderu (wykrywanie `*.gguf`),
  - upload plików `.gguf` z poziomu klienta,
  - pobieranie `.gguf` z URL (z paskiem postępu),
  - tabela z metadanymi (aktywny model, rozmiar, mtime, ścieżka),
  - bezpieczne kasowanie (tylko modele znajdujące się w folderze modeli).

### 3.2 Silnik lokalny (llama.cpp)

- `LocalChatEngine` obsługuje `llama-cpp-python` i GGUF.
- Dodano:
  - parametry ładowania modelu (m.in. `n_ctx`, `n_threads`, `n_gpu_layers`),
  - parametry generacji (`temperature`, `top_p`, `max_tokens`, `repeat_penalty`),
  - `unload()`.
- Ustawienia są zapisywane w `state.json` pod kluczem `llama_settings`.

### 3.3 Instalacja backendu z poziomu UI

- Dodano przycisk instalacji `llama-cpp-python` z poziomu klienta.
- Instalacja jest uruchamiana dopiero po potwierdzeniu w dialogu.
- Log instalacji (stdout/stderr) jest wyświetlany w UI.

## 4. Debugging i testy (sandbox)

### 4.1 Kompilacja

- `python3 -m compileall -q .` → OK
- `python3 -m py_compile main/apps/omega_app.py` → OK

### 4.2 CLI sanity-check

- `python3 ciel_cli.py list` → OK
- `python3 ciel_cli.py omega20 --steps 2 --n 16 --backend-steps 1 --backend-dt 0.02 --every 1 --max-seconds 1 --progress` → OK

### 4.3 Import-check (brak side-effectów)

- `python3 -c "import main.apps.cli; import main.apps.omega_app"` → OK

### 4.4 Zachowanie bez zależności UI

- W sandboxie brak `nicegui` powoduje kontrolowany komunikat przy uruchomieniu UI (zamiast crasha na importach).

## 5. Znane ograniczenia / ryzyka

- Instalacja `llama-cpp-python` może wymagać odpowiedniego środowiska build (kompilator, zależności systemowe); w niektórych środowiskach instalacja może się nie udać.
- Pobieranie modeli z URL jest wygodne, ale użytkownik odpowiada za źródło (bezpieczeństwo/licencje/wielkość plików).
- Ten projekt działa jako klient/host dla GGUF (uruchomienie lokalnego modelu) — nie jest to „własny wytrenowany model”, tylko uruchamianie modelu kompatybilnego z llama.cpp.

## 6. Rekomendowane następne kroki

- Dodać tryb „standalone” bez UI:
  - komenda CLI typu `chat` lub
  - lokalny serwer HTTP do chatowania (np. do integracji z innymi aplikacjami).
- Dodać walidację pobieranych plików (np. minimalne sprawdzenia rozmiaru/rozszerzenia, kontrola nadpisywania).

## 7. Status

- Architektura entrypointów: uporządkowana.
- GGUF w kliencie: dopięty i rozszerzony (biblioteka + ustawienia + opcjonalny install backendu).
- Sanity-check/debugging: wykonane, brak błędów kompilacji, CLI działa.

---

Koniec raportu.
