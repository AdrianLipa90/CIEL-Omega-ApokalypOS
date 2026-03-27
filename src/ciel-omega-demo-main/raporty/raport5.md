# raport5.md — instalatory (Linux/Windows) + bundle PyInstaller + CI + README (po raport4)

Data: 2025-12-16 22:08:00 UTC

## 1. Kontekst i cel

Po `raport4` priorytetem było domknięcie projektu pod **production-ready local demo (single-user)**:

- ujednolicić uruchamianie i konfigurację host/port,
- przygotować praktyczny „installer” dla Linux i Windows,
- dodać wariant dystrybucji bez Pythona (bundle/binary),
- dołożyć CI do budowy artefaktów,
- dopisać kompletną dokumentację uruchomieniową.

## 2. Zmiany wykonane po raport4

### 2.1 Uruchamianie UI: host/port z ENV (bezpieczny default)

- Ustawiono domyślne wiązanie UI na **localhost**:
  - `CIEL_HOST` domyślnie `127.0.0.1`
  - `CIEL_PORT` domyślnie `8080`
- Konfiguracja została podłączona do `ui.run(..., host=..., port=...)`.

Efekt: demo jest bezpieczniejsze domyślnie (nie wystawia UI na sieć), a port/host pozostaje konfigurowalny.

### 2.2 Skrypty startowe (Linux)

Dodano wygodne launchery pracujące na `.venv`:

- `scripts/run_ui.sh`
- `scripts/run_cli.sh`

Wymuszają obecność `.venv` i uruchamiają entrypointy `ciel-omega` / `ciel-cli`.

### 2.3 Instalatory skryptowe (Windows)

Dodano zestaw instalacyjny dla Windows (venv + editable install):

- `scripts/install_local.ps1`
- `scripts/run_ui.ps1`
- `scripts/run_cli.ps1`

Oraz wrappery ułatwiające uruchomienie bez walki z ExecutionPolicy:

- `scripts/install_local.cmd`
- `scripts/run_ui.cmd`
- `scripts/run_cli.cmd`

Parametry instalatora PowerShell:

- `-InstallLlama 1` (opcjonalna instalacja backendu GGUF)
- `-LlamaBackend cpu|cuda`

### 2.4 Bundle / binarki (PyInstaller)

Wprowadzono wariant dystrybucji jako jednoplikowe binarki (per-OS) z użyciem PyInstaller.

Dodane pliki:

- `scripts/entry_omega.py` (entry dla UI)
- `scripts/entry_cli.py` (entry dla CLI)
- `scripts/build_bundle.py` (build PyInstaller UI + CLI)
- `scripts/build_bundle.sh`
- `scripts/build_bundle.ps1`

Zaktualizowano zależności:

- `pyproject.toml`:
  - dodano optional group `bundle = ["pyinstaller>=6.0.0"]`

### 2.5 Assets w bundlu (Logo1.png)

UI używa zasobu `/assets/Logo1.png`. W bundlu PyInstaller ścieżki runtime są inne, więc dodano obsługę trybu bundla:

- w `main/apps/omega_app.py` wykrywanie `sys._MEIPASS` i ustawienie `assets_dir` na `Path(sys._MEIPASS) / 'main'`.

Dodatkowo `scripts/build_bundle.py` dodaje dane:

- `--add-data main/Logo1.png:main` (Linux)
- `--add-data main\Logo1.png;main` (Windows)

### 2.6 CI: budowa artefaktów Windows/Linux

Dodano workflow:

- `.github/workflows/build_bundles.yml`

Workflow:

- buduje na `ubuntu-latest` i `windows-latest`
- instaluje `.[bundle]`
- uruchamia `python scripts/build_bundle.py`
- pakuje wynik do:
  - `ciel-bundle-windows.zip`
  - `ciel-bundle-linux.tar.gz`
- publikuje archiwa jako artifacts

### 2.7 `.gitignore` (artefakty bundla)

Dodano ignorowanie katalogów buildowych:

- `dist_bundle/`
- `build_bundle/`
- `spec_bundle/`

### 2.8 Dokumentacja

Utworzono kompletne `README.md`, zawierające:

- opis CIEL (local demo, UI+CLI, GGUF opcjonalnie)
- właściwości systemu + ograniczenia
- instrukcje instalacji i uruchomienia:
  - Linux/Windows
  - wariant venv
  - wariant bundle PyInstaller
- lista ENV (`CIEL_HOST`, `CIEL_PORT`, `CIEL_DATA_DIR`, limity upload/download, feature-flag pip)
- opis lokalizacji danych (`~/.ciel/ciel_omega_data`)

## 3. Sanity-check i weryfikacja

### 3.1 Składnia

- `python3 -m py_compile` dla kluczowych modułów → OK
- `bash -n` dla skryptów bash → OK

### 3.2 Lokalny test bundla (Linux)

Wykonano lokalny build PyInstaller i smoke-test UI:

- zbudowano `dist_bundle/ciel-omega` i `dist_bundle/ciel-cli`
- uruchomiono `ciel-omega` na `127.0.0.1:18080`
- zweryfikowano dostępność zasobu: `GET /assets/Logo1.png` → OK

Wniosek: mechanizm assetów w trybie `sys._MEIPASS` działa poprawnie.

## 4. Wynik końcowy

Po pracach opisanych w `raport5` projekt ma:

- gotowy wariant **installerowy (venv)** dla Linux i Windows,
- gotowy wariant **bundle/binary** (PyInstaller) + CI do budowy,
- domyślne bezpieczne uruchamianie UI na localhost,
- dopiętą dokumentację uruchomieniową.

## 5. Znane ograniczenia / uwagi

- `llama-cpp-python` pozostaje opcjonalne i zależne od środowiska (CPU/GPU/toolchain). Bundle PyInstaller nie jest domyślnie targetowany do „wbudowania” całego llama backendu.
- Brak autoryzacji i trybu multi-user — to świadomie local demo.

## 6. Status

- Instalatory (Linux/Windows): gotowe.
- Bundle (PyInstaller) + assets: gotowe, zweryfikowane lokalnie na Linux.
- CI build artefaktów: gotowe.
- README: gotowe.

---

Koniec raportu.
