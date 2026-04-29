from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class ResolvedSymbol:
    symbol: str
    canonical_id: str
    cls: Optional[str]
    record: Dict[str, Any]
    binding: Dict[str, Any]


class VocabularyResolver:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        with self.path.open('r', encoding='utf-8') as f:
            self.vocab = yaml.safe_load(f) or {}

        raw_alias_index: Dict[str, str] = self.vocab.get('alias_index', {}) or {}
        self.alias_index: Dict[str, str] = {}
        records = self.vocab.get('records', []) or []
        self.records: Dict[str, Dict[str, Any]] = {r['canonical_id']: r for r in records if 'canonical_id' in r}

        for k, v in raw_alias_index.items():
            self.alias_index.setdefault(k, v)
            self.alias_index.setdefault(k.lower(), v)

        # backfill alias_index from records if file-level alias index is incomplete
        for record in records:
            cid = record.get('canonical_id')
            if not cid:
                continue
            sym = record.get('symbol', cid)
            self.alias_index.setdefault(sym, cid)
            self.alias_index.setdefault(sym.lower(), cid)
            for alias in record.get('aliases', []) or []:
                self.alias_index.setdefault(alias, cid)
                self.alias_index.setdefault(alias.lower(), cid)

    def canonicalize(self, symbol: str) -> str:
        return self.alias_index.get(symbol, self.alias_index.get(symbol.lower(), symbol))

    def get_record(self, canonical_id: str) -> Optional[Dict[str, Any]]:
        return self.records.get(canonical_id)

    def get_binding(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return record.get('runtime_binding', {}) or {}

    def resolve(self, symbol: str) -> ResolvedSymbol:
        cid = self.canonicalize(symbol)
        record = self.get_record(cid)
        if record is None:
            raise KeyError(f'Unknown symbol: {symbol}')
        return ResolvedSymbol(
            symbol=symbol,
            canonical_id=cid,
            cls=record.get('class'),
            record=record,
            binding=self.get_binding(record),
        )

    def try_resolve(self, symbol: str) -> Optional[ResolvedSymbol]:
        try:
            return self.resolve(symbol)
        except KeyError:
            return None

    def known_symbols(self) -> List[str]:
        return sorted(self.alias_index.keys())
