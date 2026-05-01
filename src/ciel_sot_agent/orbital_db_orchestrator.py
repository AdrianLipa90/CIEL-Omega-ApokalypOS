"""CIEL Orbital DB Orchestrator — wielki atraktor baz danych.

Jeden punkt dostępu do wszystkich baz w systemie CIEL.
Każda baza ma przypisaną masę orbitalną M_sem — im wyższa, tym wyższy priorytet
przy konfliktach i synchronizacji.

Bazy:
  TSM     — memory_ledger.db        (SQLite, M_sem~0.929) — pamięć semantyczna
  GLOSSARY— ciel_semantic_glossary  (SQLite, M_sem~0.860) — słownik kart
  WΩ      — bloch_weights.npz       (NumPy,  M_sem~0.924) — centroidy Blocha
  WPM     — wave_archive.h5         (HDF5,   M_sem~0.820) — snapshoty falowe
  CARDS   — ciel_cards.xlsx         (XLSX,   M_sem~0.800) — karty obiektów
  REGISTRIES — integration/registries/ (JSON/YAML) — rejestry kanoniczne

API:
  orc = OrbitalDBOrchestrator()
  orc.status()           → {db_id: {path, rows, m_sem, ok}}
  orc.query_tsm(...)     → wiersze z TSM
  orc.query_glossary(...)→ karty z GLOSSARY
  orc.write_tsm(...)     → zapis do TSM
  orc.sync_wo()          → online_update WΩ z TSM
  orc.ingest(path)       → ingest pliku do TSM + WΩ
  orc.rebuild_noun_index()→ przebuduj indeks słów ze wszystkich baz
  orc.full_sync()        → pełna synchronizacja wszystkich baz
"""
from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("CIEL.OrbitalOrchestrator")

# ── Ścieżki kanoniczne ────────────────────────────────────────────────────────

_ROOT = Path(__file__).parents[2]
_SRC  = _ROOT / "src"
_INTG = _ROOT / "integration"

_PATHS = {
    "TSM":      _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db",
    "GLOSSARY": _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/vocabulary/generated/ciel_semantic_glossary.db",
    "WO":       _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/bloch_weights.npz",
    "WPM":      _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5",
    "CARDS":    _INTG / "db/ciel_cards.xlsx",
    "REG_REPOS":    _INTG / "registries/repository_registry.json",
    "REG_ENTITIES": _INTG / "registries/ciel_entity_cards.yaml",
    "REG_WORDS":    _INTG / "registries/words/word_cards_registry.json",
    "REG_SECTORS":  _INTG / "Orbital/main/manifests/sectors_global.json",
    "REG_COUPLINGS":_INTG / "Orbital/main/manifests/couplings_global.json",
}

# M_sem per baza — z build_mass_table() / RELATIONAL_SEED_ORBIT_SOLVER_V0
_M_SEM = {
    "TSM":           0.929,
    "GLOSSARY":      0.860,
    "WO":            0.924,   # centroidy Blocha = bridge do encodera
    "WPM":           0.820,
    "CARDS":         0.800,
    "REG_REPOS":     0.870,
    "REG_ENTITIES":  0.940,   # relational_contract = top
    "REG_WORDS":     0.750,
    "REG_SECTORS":   0.929,
    "REG_COUPLINGS": 0.900,
}


# ── Status record ─────────────────────────────────────────────────────────────

@dataclass
class DBStatus:
    db_id: str
    path: Path
    m_sem: float
    exists: bool
    rows: int = 0
    size_kb: float = 0.0
    ok: bool = True
    error: str = ""


# ── Orkiestrator ──────────────────────────────────────────────────────────────

class OrbitalDBOrchestrator:
    """Wielki atraktor — jeden punkt dostępu do wszystkich baz CIEL."""

    def __init__(self) -> None:
        self._noun_index: dict[str, float] = {}
        self._noun_index_built = False
        log.info("OrbitalDBOrchestrator init, tracking %d data stores", len(_PATHS))

    # ── Status ────────────────────────────────────────────────────────────────

    def status(self) -> dict[str, DBStatus]:
        """Zwróć status wszystkich baz — istnienie, rozmiar, liczba wierszy."""
        results: dict[str, DBStatus] = {}
        for db_id, path in _PATHS.items():
            s = DBStatus(
                db_id=db_id,
                path=path,
                m_sem=_M_SEM.get(db_id, 0.5),
                exists=path.exists(),
            )
            if s.exists:
                try:
                    s.size_kb = path.stat().st_size / 1024
                    if path.suffix == ".db":
                        s.rows = self._sqlite_row_count(path)
                    elif path.suffix == ".json":
                        raw = json.loads(path.read_text())
                        s.rows = self._json_count(raw)
                    elif path.suffix in (".yaml", ".yml"):
                        s.rows = -1  # nie liczymy bez pyyaml
                    elif path.suffix == ".npz":
                        s.rows = -1  # array, nie wiersze
                    elif path.suffix == ".h5":
                        s.rows = -1
                except Exception as exc:
                    s.ok = False
                    s.error = str(exc)
            results[db_id] = s
        return results

    def print_status(self) -> None:
        stats = self.status()
        # Sortuj po M_sem malejąco
        sorted_stats = sorted(stats.values(), key=lambda s: -s.m_sem)
        print(f"\n{'DB':<16} {'M_sem':>6} {'rows':>6} {'size_kb':>8} {'ok':>4}  path")
        print("-" * 80)
        for s in sorted_stats:
            mark = "✓" if s.ok and s.exists else ("✗" if not s.exists else "!")
            rows_str = str(s.rows) if s.rows >= 0 else "~"
            print(f"{s.db_id:<16} {s.m_sem:>6.3f} {rows_str:>6} {s.size_kb:>8.1f} {mark:>4}  {s.path.name}")

    # ── TSM ───────────────────────────────────────────────────────────────────

    def query_tsm(
        self,
        sql: str,
        params: tuple = (),
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Wykonaj SELECT na TSM. Zwraca listę dicts."""
        path = _PATHS["TSM"]
        if not path.exists():
            return []
        conn = self._tsm_conn()
        try:
            cursor = conn.execute(sql + (f" LIMIT {limit}" if "LIMIT" not in sql.upper() else ""), params)
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def write_tsm(self, entry: dict[str, Any]) -> str:
        """Zapisz wpis do TSM. Zwraca memorise_id."""
        import hashlib
        path = _PATHS["TSM"]
        conn = self._tsm_conn()
        try:
            mem_id = entry.get("memorise_id") or (
                "orch_" + hashlib.sha256(
                    str(entry.get("D_sense", "")).encode()
                ).hexdigest()[:12]
            )
            now = datetime.now(timezone.utc).isoformat()
            exists = conn.execute(
                "SELECT 1 FROM memories WHERE memorise_id=?", (mem_id,)
            ).fetchone()
            if not exists:
                conn.execute(
                    """INSERT INTO memories
                       (memorise_id, created_at, D_id, D_sense, D_type, D_context, source)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        mem_id, now,
                        entry.get("D_id", mem_id),
                        entry.get("D_sense", ""),
                        entry.get("D_type", "text"),
                        entry.get("D_context", ""),
                        entry.get("source", "orchestrator"),
                    )
                )
                conn.commit()
                log.info("TSM write: %s", mem_id)
            return mem_id
        finally:
            conn.close()

    def tsm_row_count(self) -> int:
        return self._sqlite_row_count(_PATHS["TSM"])

    # ── GLOSSARY ──────────────────────────────────────────────────────────────

    def query_glossary(
        self,
        symbol: str | None = None,
        card_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Szukaj kart w GLOSSARY po symbolu lub typie."""
        path = _PATHS["GLOSSARY"]
        if not path.exists():
            return []
        conn = sqlite3.connect(str(path), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            where, params = [], []
            if symbol:
                where.append("symbol LIKE ?")
                params.append(f"%{symbol}%")
            if card_type:
                where.append("card_type = ?")
                params.append(card_type)
            clause = ("WHERE " + " AND ".join(where)) if where else ""
            cursor = conn.execute(
                f"SELECT * FROM cards {clause} LIMIT {limit}", params
            )
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ── WΩ / BlochEncoder ─────────────────────────────────────────────────────

    def sync_wo(self, limit: int = 100, lr: float = 0.05) -> int:
        """Online update WΩ centroidów z ostatnich wpisów TSM."""
        try:
            import sys, importlib.util
            enc_path = _PATHS["WO"].parent / "ciel_bloch_encoder.py"
            spec = importlib.util.spec_from_file_location("ciel_bloch_encoder", enc_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["ciel_bloch_encoder"] = mod
            spec.loader.exec_module(mod)
            enc = mod.CIELBlochEncoder()
            n = enc.online_update_from_tsm(limit=limit, lr=lr)
            log.info("WΩ sync: %d updates", n)
            return n
        except Exception as exc:
            log.warning("WΩ sync failed: %s", exc)
            return 0

    # ── Document ingest ───────────────────────────────────────────────────────

    def ingest(self, path: Path, lr: float = 0.03) -> dict:
        """Ingestuj plik do TSM + online update WΩ.

        Używa ciel_doc_ingest z Heisenberg clipem.
        """
        try:
            import sys, importlib.util
            ing_path = (
                _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/ciel_doc_ingest.py"
            )
            spec = importlib.util.spec_from_file_location("ciel_doc_ingest", ing_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["ciel_doc_ingest"] = mod
            spec.loader.exec_module(mod)
            result = mod.ingest_file(Path(path), lr=lr)
            log.info("Ingest %s: %s", path, result)
            return result
        except Exception as exc:
            log.warning("Ingest failed: %s", exc)
            return {"error": str(exc), "path": str(path)}

    # ── Noun index — łączy wszystkie bazy w jeden indeks tokenów ─────────────

    def rebuild_noun_index(self) -> dict[str, float]:
        """Przebuduj indeks słów → M_sem ze wszystkich baz.

        Hierarchia źródeł (wyższy M_sem wygrywa przy kolizji):
        1. REG_ENTITIES (ciel_entity_cards.yaml) — M_sem z entity
        2. REG_SECTORS (sectors_global.json) — M_sem z sektora
        3. REG_REPOS (repository_registry.json) — M_sem z repo
        4. GLOSSARY (ciel_semantic_glossary.db) — symbole i tagi
        5. TSM (memory_ledger.db) — D_sense tokenów z winding_n
        """
        import re
        import sys

        index: dict[str, float] = {}

        def _add(word: str, msem: float) -> None:
            w = word.lower().strip()
            if len(w) > 2 and w.isalpha():
                if w not in index or index[w] < msem:
                    index[w] = msem

        def _tokenize(text: str) -> list[str]:
            return re.findall(r"[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", str(text))

        # 1+2+3: ciel_geometry.semantic_mass → build_mass_table
        try:
            geo_root = _SRC
            if str(geo_root) not in sys.path:
                sys.path.insert(0, str(geo_root))
            from ciel_geometry.semantic_mass import build_mass_table
            table = build_mass_table(include_entities=True, include_repos=True)
            for rec in table:
                clean = rec.id.replace("sector:", "").replace("entity:", "").replace("repo:", "")
                for w in _tokenize(clean):
                    _add(w, rec.M_sem)
        except Exception as exc:
            log.debug("Noun index: mass_table failed: %s", exc)

        # 4: GLOSSARY — symbole, nazwy, tagi
        if _PATHS["GLOSSARY"].exists():
            try:
                conn = sqlite3.connect(str(_PATHS["GLOSSARY"]), timeout=5)
                for row in conn.execute("SELECT symbol, name FROM cards").fetchall():
                    for field_val in row:
                        if field_val:
                            for w in _tokenize(str(field_val)):
                                _add(w, 0.75)  # GLOSSARY baseline
                for row in conn.execute("SELECT tag FROM tags").fetchall():
                    if row[0]:
                        for w in _tokenize(row[0]):
                            _add(w, 0.65)
                conn.close()
            except Exception as exc:
                log.debug("Noun index: GLOSSARY failed: %s", exc)

        # 5: TSM — D_sense z winding_n > 0 (słowa które przeżyły cykle orbitalne)
        if _PATHS["TSM"].exists():
            try:
                conn = self._tsm_conn()
                rows = conn.execute(
                    "SELECT D_sense, winding_n, D_type FROM memories "
                    "WHERE D_sense IS NOT NULL AND winding_n > 0 "
                    "ORDER BY winding_n DESC LIMIT 500"
                ).fetchall()
                conn.close()
                import math
                for sense, winding, dtype in rows:
                    base = math.log1p(winding) / math.log1p(200)
                    type_boost = {"ethical_anchor": 0.3, "identity": 0.2, "episodic": 0.1}.get(dtype or "", 0.0)
                    msem = min(0.85, 0.40 + base * 0.45 + type_boost)
                    for w in _tokenize(str(sense)):
                        _add(w, msem)
            except Exception as exc:
                log.debug("Noun index: TSM failed: %s", exc)

        self._noun_index = index
        self._noun_index_built = True
        log.info("Noun index rebuilt: %d words", len(index))
        return index

    def get_noun_index(self) -> dict[str, float]:
        """Zwróć noun index — buduje jeśli nie zbudowany."""
        if not self._noun_index_built:
            self.rebuild_noun_index()
        return self._noun_index

    def top_words(self, n: int = 30) -> list[tuple[str, float]]:
        """Zwróć n najcięższe semantycznie słowa."""
        idx = self.get_noun_index()
        return sorted(idx.items(), key=lambda x: -x[1])[:n]

    # ── Full sync ─────────────────────────────────────────────────────────────

    def full_sync(self, lr: float = 0.05) -> dict[str, Any]:
        """Pełna synchronizacja:
        1. Status wszystkich baz
        2. Rebuild noun index
        3. Sync WΩ z TSM
        Zwraca raport.
        """
        report: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": {},
            "noun_index_words": 0,
            "wo_updates": 0,
            "errors": [],
        }

        # Status
        stats = self.status()
        for db_id, s in stats.items():
            report["status"][db_id] = {
                "exists": s.exists,
                "rows": s.rows,
                "m_sem": s.m_sem,
                "ok": s.ok,
            }

        # Noun index
        try:
            idx = self.rebuild_noun_index()
            report["noun_index_words"] = len(idx)
        except Exception as exc:
            report["errors"].append(f"noun_index: {exc}")

        # WΩ sync
        try:
            n = self.sync_wo(lr=lr)
            report["wo_updates"] = n
        except Exception as exc:
            report["errors"].append(f"wo_sync: {exc}")

        return report

    # ── Internals ─────────────────────────────────────────────────────────────

    def _tsm_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(_PATHS["TSM"]), timeout=15)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=15000")
        return conn

    @staticmethod
    def _sqlite_row_count(path: Path) -> int:
        try:
            conn = sqlite3.connect(str(path), timeout=5)
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            total = sum(
                conn.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
                for t in tables
            )
            conn.close()
            return total
        except Exception:
            return -1

    @staticmethod
    def _json_count(raw: Any) -> int:
        if isinstance(raw, list):
            return len(raw)
        if isinstance(raw, dict):
            for key in ("cards", "entities", "repositories", "edges", "sectors"):
                if key in raw:
                    v = raw[key]
                    if isinstance(v, (list, dict)):
                        return len(v)
            return len(raw)
        return 0


# ── Singleton ─────────────────────────────────────────────────────────────────

_orchestrator: OrbitalDBOrchestrator | None = None


def get_orchestrator() -> OrbitalDBOrchestrator:
    """Zwróć globalny singleton orkiestratora."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrbitalDBOrchestrator()
    return _orchestrator


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")

    orc = OrbitalDBOrchestrator()

    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        orc.print_status()

    elif cmd == "sync":
        report = orc.full_sync()
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif cmd == "words":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        top = orc.top_words(n)
        print(f"\nTop {n} semantic words:")
        for w, m in top:
            print(f"  {w:<25} {m:.4f}")

    elif cmd == "ingest":
        if len(sys.argv) < 3:
            print("Usage: orbital_db_orchestrator.py ingest <path>")
            sys.exit(1)
        r = orc.ingest(Path(sys.argv[2]))
        print(json.dumps(r, indent=2, ensure_ascii=False))

    elif cmd == "query":
        sql = sys.argv[2] if len(sys.argv) > 2 else "SELECT memorise_id, D_type, D_sense FROM memories LIMIT 10"
        rows = orc.query_tsm(sql)
        for r in rows:
            print(r)

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: status | sync | words [n] | ingest <path> | query <sql>")
