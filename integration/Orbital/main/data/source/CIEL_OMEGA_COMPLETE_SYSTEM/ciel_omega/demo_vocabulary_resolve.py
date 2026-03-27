from __future__ import annotations

from pathlib import Path
import sys

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from ciel_omega.vocabulary_tools import VocabularyResolver, SymbolExtractor


def main():
    resolver = VocabularyResolver(_THIS_DIR / 'vocabulary.yaml')
    extractor = SymbolExtractor(resolver)
    text = 'Ea stabilizes closure through WhiteThreads while Euler Constraint measures winding and phase.'
    extracted = extractor.extract(text)
    print('EXTRACTED:')
    for item in extracted:
        print(f'- {item.surface!r} -> {item.canonical_id} [{item.start}:{item.end}]')
    print('\nRESOLVED:')
    for item in extracted:
        r = resolver.resolve(item.surface)
        print(f'- {r.symbol!r} -> class={r.cls} binding={r.binding}')


if __name__ == '__main__':
    main()
