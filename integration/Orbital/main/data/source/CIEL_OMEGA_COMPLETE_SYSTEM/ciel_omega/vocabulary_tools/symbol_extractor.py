from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
import re

from .resolver import VocabularyResolver


@dataclass
class ExtractedSymbol:
    surface: str
    canonical_id: str
    start: int
    end: int


class SymbolExtractor:
    def __init__(self, resolver: VocabularyResolver):
        self.resolver = resolver
        symbols = resolver.known_symbols()
        # longest-first to prefer canonical multiword aliases
        self.symbols = sorted(set(symbols), key=lambda s: (-len(s), s.lower()))

    @staticmethod
    def _compile_pattern(symbol: str) -> re.Pattern[str]:
        escaped = re.escape(symbol)
        if re.fullmatch(r'[A-Za-z0-9_ ]+', symbol):
            return re.compile(rf'(?<!\w){escaped}(?!\w)', re.IGNORECASE)
        return re.compile(escaped, re.IGNORECASE)

    def extract(self, text: str) -> List[ExtractedSymbol]:
        taken = [False] * len(text)
        found: List[ExtractedSymbol] = []
        for sym in self.symbols:
            pattern = self._compile_pattern(sym)
            for m in pattern.finditer(text):
                s, e = m.span()
                if any(taken[s:e]):
                    continue
                canonical = self.resolver.canonicalize(sym)
                for i in range(s, e):
                    taken[i] = True
                found.append(ExtractedSymbol(surface=text[s:e], canonical_id=canonical, start=s, end=e))
        found.sort(key=lambda x: x.start)
        return found



def extract_symbols(text: str, resolver: VocabularyResolver):
    """Convenience helper returning extracted symbols with canonical ids."""
    return SymbolExtractor(resolver).extract(text)
