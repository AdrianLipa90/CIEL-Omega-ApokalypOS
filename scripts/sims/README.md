# CIEL Simulations & Benchmarks

Katalog skryptów symulacyjnych i benchmarkowych.
Zachowywane żeby nie regenerować między sesjami.

| Skrypt | Opis | Wyniki (ostatnie) |
|---|---|---|
| `energy_benchmark.py` | Zużycie energii CIEL vs Claude API | M0-M8: ~98mJ/krok, pipeline: ~23J, Claude server: ~5040J/call |
| `htri_mini.py` *(symlink → ../htri_mini.py)* | Kuramoto 768 oscylatorów na CPU/GPU | — (nie uruchamiany na GPU) |

## Konwencja

- Każdy skrypt zawiera docstring z opisem, parametrami i ostatnimi wynikami.
- Wyniki zapisywać w docstringu przy każdym uruchomieniu z datą.
- Nie usuwać skryptów bez powodu — nawet "jednorazowe" mogą być przydatne.
