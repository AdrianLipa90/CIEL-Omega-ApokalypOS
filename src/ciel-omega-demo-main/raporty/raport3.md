# raport3.md

Data/godzina: 2025-12-15 00:40 UTC

## Cel
Zweryfikować zgłoszenie: „testy nie powinny trwać godzine” oraz wskazać przyczynę wrażenia „zwisu” dla nowych komend CLI (w szczególności `omega20`).

## Reprodukcja i pomiary czasu (lokalnie)
Pomiary wykonane na komendach CLI, z `PYTHONDONTWRITEBYTECODE=1`.

- `python3 ciel_cli.py omega20 --steps 20 --n 96 --json`:
  - real ~0.23s
- `python3 ciel_cli.py omega18 --steps 12 --n 96 --json`:
  - real ~0.34s
- `python3 ciel_cli.py emotion --json`:
  - real ~0.29s
- `python3 ciel_cli.py spectral12d --json`:
  - real ~0.17s
- `python3 ciel_cli.py adam21 --json` (uruchomione z `cwd=/tmp`, żeby nie brudzić projektu plikami json):
  - real ~0.30s

Wniosek: w konfiguracji domyślnej (steps 20, n 96) `omega20` nie ma cech „zwisu” i kończy się w ułamku sekundy.

## Dlaczego mogło wyglądać jak „zwis”
- Brak jakiegokolwiek outputu w trakcie pracy.
  - Stare zachowanie `omega20` wypisywało JSON dopiero po zakończeniu pętli, więc przy większych parametrach (`--steps`/`--n`/`--backend-steps`) proces wygląda na „martwy”.
- Anulowanie kroku przez użytkownika w trakcie uruchomienia.
  - To kończy komendę bez wyniku, co może wyglądać jak „utknięcie”.
- Parametry wpływające na koszt obliczeń.
  - Złożoność w przybliżeniu skaluje się jak:
    - O(steps * backend_steps * n^2)
  - Jeśli ktoś odpali np. `--steps 50000` albo `--n 512` + `--backend-steps` duże, to czas może wzrosnąć do minut/godzin.

## Przegląd kodu pod kątem pętli nieskończonych
- `main/omega/runtime20.py`:
  - Pętla w `run_demo` jest jawnie ograniczona `range(1, steps+1)`.
  - `OmegaRuntime.step(...)` robi stałą liczbę operacji na tablicach NumPy i pętlę backendu ograniczoną `backend_steps`.
- `main/omega/field_ops.py`:
  - `laplacian2`, `field_norm`, `coherence_metric` to proste operacje wektorowe bez pętli w Pythonie.
- `main/omega/batch18.py`:
  - Pętle również ograniczone (np. `OmegaBootRitual.steps`, `for _ in range(10)`, `for _ in range(5)`).

Wniosek: nie ma tu pętli nieskończonych ani „ukrytych” dużych pętli w Pythonie. Jeżeli czas rośnie dramatycznie, to powód jest niemal na pewno parametryczny (`steps`, `n`, `backend_steps`) albo środowiskowy (obciążony CPU).

## Poprawka wdrożona (żeby testy nie wyglądały na zwis)
Zmieniono `omega20` tak, aby można było wymusić „heartbeat” i limit czasu:

1) `main/omega/runtime20.py`
- `run_demo(...)` przyjmuje teraz:
  - `every`, `progress` (drukuje postęp na stderr)
  - `max_seconds` (przerywa pętlę po przekroczeniu czasu)
  - `backend_steps`, `backend_dt`

2) `ciel_cli.py`
- `omega20` dostało nowe flagi:
  - `--backend-steps`
  - `--backend-dt`
  - `--every`
  - `--progress`
  - `--max-seconds`

Przykład użycia (bez „zwisu”):

- `python3 ciel_cli.py omega20 --steps 200 --n 96 --progress --every 10 --max-seconds 5 --json`

## Rekomendacje
- Domyślne parametry testów utrzymać małe; dla dużych uruchomień zawsze używać `--progress` + `--every` + `--max-seconds`.
- Jeśli pojawi się realny przypadek „godzinnego” działania:
  - poprosić o dokładną komendę (z parametrami) + `nproc`/obciążenie CPU,
  - wtedy dopiero rozważać optymalizacje (np. FFT laplasjanu lub redukcję backend_steps).

## Status
- Komendy CLI: `spectral12d`, `emotion`, `adam21`, `omega20` działają i kończą się szybko w ustawieniach domyślnych.
- `omega20` ma teraz mechanizmy progresu/limitu czasu, żeby wyeliminować wrażenie „zwisu”.
