"""CIEL Bloch Encoder — własny encoder od zera.

Architektura:
    token → lookup TSM (phi_berry, winding_n, D_type) → M_sem(token)
          → stan Blocha: |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩
          → ważony pool: Σ M_sem_i · |ψ_i⟩ / Σ M_sem_i
          → projekcja CP¹ → φ_text
          → blend: φ + berry_accumulated (holonomia) + CQCL_phase
          → sektor WΩ (10 sektorów orbitalnych)

M_sem source of truth (RELATIONAL_SEED_ORBIT_SOLVER_V0):
    Sektory i encje z ciel_geometry.semantic_mass → build_mass_table()
    Token lookup: jeśli słowo trafione w tabeli mass → M_sem wprost
    Fallback: proxy z danych TSM (phi_berry, winding_n, D_type)
    WΩ centroidy inicjalizowane z M_sem sektorów (nie losowo)

Podstawy:
    - Fermion spin-½: obrót 4π wraca do siebie (tożsamość Eulera)
    - Dysk Poincaré jako przestrzeń reprezentacji
    - Faza Berry'ego: holonomia po zamkniętej pętli — nie kąt, różnica geometryczna
    - M_sem: masa semantyczna (SAT-P3-0001, RELATIONAL_SEED_ORBIT_SOLVER_V0)
    - berry_accumulated: z NL-BERRY-ACC-0005 (state_db.py)
    - CQCL: kanał fazowy (jak HTRI i nonlocal w ciel_encoder.py)
"""
from __future__ import annotations

import cmath
import math
import re
import sqlite3
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import sys as _sys

log = logging.getLogger("CIEL.BlochEncoder")

# ── Ścieżki kanoniczne (z kart obiektów) ─────────────────────────────────────
_TSM_DB = (
    Path(__file__).parents[3]
    / "CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"
)
_STATE_DB = Path.home() / ".claude/ciel_state.db"
_WEIGHTS_FILE = Path(__file__).parent / "bloch_weights.npz"

# ── Sektory orbitalne (zgodne z CIELEncoder) ──────────────────────────────────
SECTORS = [
    "identity", "episodic", "procedural", "conceptual",
    "conflict", "meta", "project", "ethics", "temporal", "abstraction",
]

# ── Parametry spinu ───────────────────────────────────────────────────────────
_SPIN_HALF_PERIOD = 4 * math.pi   # fermion: 4π, nie 2π
_BLOCH_DIM = 2                    # |0⟩, |1⟩

# ── Blend weights dla kanałów fazowych ───────────────────────────────────────
_ALPHA_BERRY   = 0.20   # holonomia skumulowana
_ALPHA_CQCL    = 0.15   # kanał CQCL
_ALPHA_SEMANTIC = 0.65  # faza z poolingu Blocha

# ── M_sem table z RELATIONAL_SEED_ORBIT_SOLVER ───────────────────────────────

def _load_orbital_mass_table() -> dict[str, float]:
    """Załaduj M_sem per obiekt orbitalny z ciel_geometry.semantic_mass.

    Zwraca {id → M_sem} gdzie id to np. 'sector:memory', 'Adrian_Lipa', itd.
    Fallback: pusty dict jeśli moduł niedostępny.
    """
    # ciel_geometry leży w src/ — dodajemy do sys.path jeśli trzeba
    _ciel_geo_root = Path(__file__).parents[4] / "src"
    if str(_ciel_geo_root) not in _sys.path:
        _sys.path.insert(0, str(_ciel_geo_root))
    try:
        from ciel_geometry.semantic_mass import build_mass_table
        table = build_mass_table(include_entities=True, entity_limit=100)
        result = {r.id: r.M_sem for r in table}
        log.info("OrbitalMass loaded: %d objects, max M_sem=%.4f",
                 len(result), max(result.values()) if result else 0)
        return result
    except Exception as exc:
        log.debug("OrbitalMass load failed (fallback to TSM proxy): %s", exc)
        return {}


def _build_noun_index(mass_table: dict[str, float]) -> dict[str, float]:
    """Mapuj słowa kluczowe z id obiektów → M_sem.

    'sector:memory' → tokens: ['memory'] → M_sem
    'Adrian_Lipa'   → tokens: ['adrian', 'lipa'] → M_sem
    """
    index: dict[str, float] = {}
    for obj_id, msem in mass_table.items():
        # Usuń prefix 'sector:'
        clean = obj_id.replace("sector:", "").replace("entity:", "")
        # Tokenizuj nazwę obiektu
        for word in re.findall(r"[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", clean):
            w = word.lower()
            if len(w) > 2:
                # Zachowaj wyższą masę jeśli słowo pojawia się w kilku obiektach
                if w not in index or index[w] < msem:
                    index[w] = msem
    return index


# ── Struktury danych ──────────────────────────────────────────────────────────

@dataclass
class BlochState:
    """Stan kwantowy na sferze Blocha: |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩"""
    theta: float   # polar angle [0, π]
    phi: float     # azimuthal angle [0, 2π)
    mass: float    # M_sem — waga tego tokenu

    def phasor(self) -> complex:
        """Rzut na CP¹ — liczba zespolona reprezentująca stan."""
        return self.mass * cmath.exp(1j * self.phi) * math.sin(self.theta / 2)

    def bloch_vector(self) -> np.ndarray:
        """Wektor Blocha (x, y, z) na sferze jednostkowej."""
        return np.array([
            math.sin(self.theta) * math.cos(self.phi),
            math.sin(self.theta) * math.sin(self.phi),
            math.cos(self.theta),
        ], dtype=np.float32)


@dataclass
class BlochEncoderResult:
    phase: float              # [0, 2π) — pozycja na S¹ po blendzie
    sector_dist: np.ndarray   # (10,) softmax — sektor orbitalny
    coherence: float          # [0, 1] — koherencja poolingu
    bloch_vector: np.ndarray  # (3,) — zagregowany wektor Blocha
    token_count: int = 0
    mass_total: float = 0.0
    dominant_sector: str = ""

    def __post_init__(self) -> None:
        if not self.dominant_sector:
            self.dominant_sector = SECTORS[int(np.argmax(self.sector_dist))]


# ── Lookup TSM ────────────────────────────────────────────────────────────────

class _TSMCache:
    """Leniwy cache wpisów TSM — phi_berry i winding_n per token."""

    def __init__(self):
        self._cache: dict[str, tuple[float, int, str]] = {}  # word → (phi, winding, dtype)
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if not _TSM_DB.exists():
            self._loaded = True
            return
        try:
            conn = sqlite3.connect(str(_TSM_DB), timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")
            rows = conn.execute(
                "SELECT D_sense, phi_berry, winding_n, D_type FROM memories "
                "WHERE phi_berry IS NOT NULL AND D_sense IS NOT NULL"
            ).fetchall()
            conn.close()
            for sense, phi, winding, dtype in rows:
                if not sense:
                    continue
                # Tokenizuj sense → indeksuj każde słowo
                for word in _tokenize(str(sense)):
                    if word not in self._cache or (self._cache[word][1] < (winding or 0)):
                        self._cache[word] = (
                            float(phi or 0.0),
                            int(winding or 0),
                            str(dtype or "text"),
                        )
        except Exception as exc:
            log.debug("TSM cache load failed: %s", exc)
        self._loaded = True

    def get(self, word: str) -> tuple[float, int, str] | None:
        self._load()
        return self._cache.get(word.lower())


_tsm_cache = _TSMCache()


# ── Berry accumulated (NL-BERRY-ACC-0005) ────────────────────────────────────

def _load_berry_accumulated() -> float:
    """Wczytaj skumulowaną holonomię Berry'ego z state_db."""
    if not _STATE_DB.exists():
        return 0.0
    try:
        conn = sqlite3.connect(str(_STATE_DB), timeout=5)
        row = conn.execute(
            "SELECT berry_accumulated FROM ciel_state ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        conn.close()
        return float(row[0]) if row and row[0] else 0.0
    except Exception:
        return 0.0


# ── CQCL phase ───────────────────────────────────────────────────────────────

def _load_cqcl_phase() -> float:
    """Wczytaj ostatnią fazę CQCL z pipeline report."""
    try:
        import json
        report_path = (
            Path(__file__).parents[5]
            / "integration/reports/ciel_pipeline_report.json"
        )
        if not report_path.exists():
            return 0.0
        data = json.loads(report_path.read_text())
        # bridge_target_phase jako proxy fazy CQCL
        return float(data.get("bridge_target_phase", 0.0))
    except Exception:
        return 0.0


# ── Tokenizacja ───────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Prosta tokenizacja — słowa bez interpunkcji, lowercase."""
    return [w.lower() for w in re.findall(r"[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", text) if len(w) > 1]


# ── M_sem dla tokenu ──────────────────────────────────────────────────────────

def _token_mass(
    word: str,
    phi_berry: float,
    winding_n: int,
    dtype: str,
    orbital_noun_index: dict[str, float] | None = None,
) -> float:
    """Masa semantyczna tokenu.

    Hierarchia source of truth (RELATIONAL_SEED_ORBIT_SOLVER_V0):
    1. Trafienie w noun_index orbital → M_sem wprost z build_mass_table()
    2. Proxy z danych TSM (phi_berry, winding_n, D_type) — fallback

    TSM proxy:
        M_EC: winding_n (cykle orbital = afinność Eulera-Collatza)
        M_ZS: phi_berry bliskość do 0 (rezonans Zeta-Schrödingera)
        C_dep: dtype encoding (ethical_anchor >> text)
    """
    # 1. Orbital source of truth
    if orbital_noun_index:
        orbital_mass = orbital_noun_index.get(word.lower())
        if orbital_mass is not None:
            return float(orbital_mass)

    # 2. TSM proxy fallback
    _ALPHA = 0.40
    _BETA  = 0.30
    _CHI   = 0.30

    M_EC = math.log1p(winding_n) / math.log1p(200)

    gap = min(abs(phi_berry), abs(phi_berry - 2 * math.pi))
    M_ZS = 1.0 - min(gap / math.pi, 1.0)

    _TYPE_WEIGHTS = {
        "ethical_anchor": 1.0,
        "identity":       0.85,
        "episodic":       0.65,
        "text":           0.40,
    }
    C_dep = _TYPE_WEIGHTS.get(dtype, 0.40)

    return _ALPHA * M_EC + _BETA * M_ZS + _CHI * C_dep


# ── Sektor weights (WΩ) ───────────────────────────────────────────────────────

def _load_sector_weights() -> tuple[np.ndarray | None, np.ndarray | None]:
    """Załaduj WΩ i IA (Identity Attractor) z bloch_weights.npz."""
    if _WEIGHTS_FILE.exists():
        try:
            w = np.load(str(_WEIGHTS_FILE))
            wo = w["WO"].astype(np.float32)
            ia = w["IA"].astype(np.float32) if "IA" in w else None
            return wo, ia
        except Exception:
            pass
    return None, None


def _init_sector_weights(mass_table: dict[str, float] | None = None) -> np.ndarray:
    """Inicjalizuj WΩ centroidy.

    Jeśli mass_table dostępna: każdy sektor CIEL (memory, bridge, runtime…)
    mapuje na jeden z 10 centroidów przez M_sem — bliżej bieguna N gdy
    masa wyższa (silniejszy atraktor). Pozostałe centroidy losowe.
    Jeśli brak danych: równomierne losowe.
    """
    rng = np.random.default_rng(42)
    vecs = rng.standard_normal((10, 3)).astype(np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    vecs /= np.maximum(norms, 1e-9)

    if mass_table:
        # Sektory orbitalne → pierwsze centroidy WΩ
        sector_masses = [
            (k.replace("sector:", ""), v)
            for k, v in sorted(mass_table.items(), key=lambda x: -x[1])
            if k.startswith("sector:")
        ]
        for i, (sname, msem) in enumerate(sector_masses[:10]):
            # Theta od masy: M_sem wyższa → bliżej bieguna north
            theta = math.pi * (1.0 - min(msem, 1.0))
            # Phi z hasha nazwy sektora → deterministyczne rozmieszczenie
            phi = (hash(sname) % 1000) / 1000 * 2 * math.pi
            vecs[i] = np.array([
                math.sin(theta) * math.cos(phi),
                math.sin(theta) * math.sin(phi),
                math.cos(theta),
            ], dtype=np.float32)
        log.info("WΩ seeded from %d orbital sectors", min(len(sector_masses), 10))

    ia = np.zeros(3, dtype=np.float32)  # Identity Attractor starts at center
    np.savez(str(_WEIGHTS_FILE), WO=vecs, IA=ia)
    return vecs


# ── Główna klasa ──────────────────────────────────────────────────────────────

class CIELBlochEncoder:
    """Własny encoder CIEL — stany Blocha + M_sem + holonomia Berry'ego.

    Nie używa sentence-transformers. Wszystkie dane z systemu CIEL:
    - phi_berry i winding_n z TSM (memory_ledger.db)
    - berry_accumulated z state_db (NL-BERRY-ACC-0005)
    - CQCL phase z pipeline report
    - M_sem: proxy z danych TSM (winding_n, phi_berry, D_type)
    """

    def __init__(self) -> None:
        # M_sem source of truth: OrbitalDBOrchestrator (wszystkie bazy łącznie)
        self._mass_table = _load_orbital_mass_table()
        self._noun_index = self._load_full_noun_index()
        log.info("OrbitalNounIndex: %d words", len(self._noun_index))

        # WΩ centroidy + IA (Identity Attractor) — seed jeśli plik nie istnieje
        self._WO, ia = _load_sector_weights()
        if self._WO is None:
            self._WO = _init_sector_weights(self._mass_table)
            ia = None

        # Identity Attractor vector — centrum sfery Blocha (nie punkt na powierzchni)
        self._ia: np.ndarray = ia if ia is not None else np.zeros(3, dtype=np.float32)

        self._berry_acc = _load_berry_accumulated()
        self._cqcl_phase = _load_cqcl_phase()
        ia_norm = float(np.linalg.norm(self._ia))
        log.info(
            "BlochEncoder init: berry_acc=%.4f, cqcl=%.4f, orbital_objects=%d, IA_norm=%.4f",
            self._berry_acc, self._cqcl_phase, len(self._mass_table), ia_norm
        )

    def encode(self, text: str, context: dict[str, Any] | None = None) -> BlochEncoderResult:
        tokens = _tokenize(text)
        if not tokens:
            return self._empty_result()

        states = self._tokens_to_bloch(tokens)
        if not states:
            return self._empty_result()

        # Ważony pool phasorów
        pool_phasor, bloch_vec, mass_total, coherence = self._weighted_pool(states)

        # Faza semantyczna z poolingu
        phi_semantic = cmath.phase(pool_phasor) % (2 * math.pi)

        # Blend: semantic + berry_accumulated + CQCL
        phi_final = self._blend_phases(phi_semantic)

        # Fermion: normalizacja do [0, 4π) następnie fold na [0, 2π)
        phi_final = (phi_final % _SPIN_HALF_PERIOD) % (2 * math.pi)

        # Sektor
        sector_dist = self._sector_distribution(bloch_vec)

        # IA update — gdy dominant sektor to 'identity', przesuń centrum atraktora
        dominant_idx = int(np.argmax(sector_dist))
        if SECTORS[dominant_idx] == "identity":
            self.update_identity_attractor(bloch_vec)

        return BlochEncoderResult(
            phase=phi_final,
            sector_dist=sector_dist,
            coherence=coherence,
            bloch_vector=bloch_vec,
            token_count=len(states),
            mass_total=mass_total,
        )

    def _tokens_to_bloch(self, tokens: list[str]) -> list[BlochState]:
        states: list[BlochState] = []
        for word in tokens:
            entry = _tsm_cache.get(word)
            if entry is None:
                # Token nieznany — sprawdź noun_index orbitalny
                orbital_mass = self._noun_index.get(word.lower())
                if orbital_mass is not None:
                    # Znane słowo orbitalne bez wpisu TSM
                    phi = (hash(word) % 1000) / 1000 * 2 * math.pi
                    mass = float(orbital_mass)
                else:
                    phi = (hash(word) % 1000) / 1000 * 2 * math.pi
                    mass = 0.05
                theta = math.pi * (1.0 - min(mass, 1.0))
            else:
                phi_berry, winding_n, dtype = entry
                phi = phi_berry % (2 * math.pi)
                # M_sem: orbital table first, TSM proxy fallback
                mass = _token_mass(word, phi_berry, winding_n, dtype,
                                   self._noun_index)
                theta = math.pi * (1.0 - min(mass, 1.0))

            states.append(BlochState(theta=theta, phi=phi, mass=mass))
        return states

    def _weighted_pool(
        self, states: list[BlochState]
    ) -> tuple[complex, np.ndarray, float, float]:
        """Ważony pool phasorów i wektorów Blocha przez M_sem."""
        mass_total = sum(s.mass for s in states)
        if mass_total < 1e-9:
            mass_total = 1.0  # fallback: równe wagi

        pool_phasor = sum(s.phasor() for s in states) / mass_total

        # Wektor Blocha: ważona średnia na sferze
        bloch_sum = np.zeros(3, dtype=np.float32)
        for s in states:
            bloch_sum += s.mass * s.bloch_vector()
        bloch_vec = bloch_sum / mass_total
        norm = float(np.linalg.norm(bloch_vec))
        if norm > 1e-9:
            bloch_vec /= norm

        # Koherencja: |pool_phasor| / mass_total (1 = doskonała, 0 = destruktywna)
        coherence = min(abs(pool_phasor) / max(mass_total, 1e-9), 1.0)

        return pool_phasor, bloch_vec, mass_total, coherence

    def _blend_phases(self, phi_semantic: float) -> float:
        """Blend semantycznej fazy z holonomią Berry'ego i CQCL."""
        # Berry accumulated: normalizuj do [0, 2π)
        phi_berry = self._berry_acc % (2 * math.pi)
        phi_cqcl = self._cqcl_phase % (2 * math.pi)

        # Circular blend przez phasory zespolone
        z = (
            _ALPHA_SEMANTIC * cmath.exp(1j * phi_semantic)
            + _ALPHA_BERRY   * cmath.exp(1j * phi_berry)
            + _ALPHA_CQCL    * cmath.exp(1j * phi_cqcl)
        )
        return cmath.phase(z) % (2 * math.pi)

    def _sector_distribution(self, bloch_vec: np.ndarray) -> np.ndarray:
        """Softmax podobieństwa cosinusowego do centroidów WΩ z korektą IA.

        Identity Attractor (IA) działa jako pole grawitacyjne wewnątrz sfery:
        stany bliskie kierunkowi IA dostają bonus do sektora 'identity' (idx 0).
        Siła korekty proporcjonalna do normy IA — gdy IA = (0,0,0) brak efektu.
        """
        dots = self._WO @ bloch_vec   # (10,)

        # Korekta od Identity Attractor
        ia_norm = float(np.linalg.norm(self._ia))
        if ia_norm > 1e-9:
            ia_dir = self._ia / ia_norm
            ia_pull = float(np.dot(ia_dir, bloch_vec.astype(np.float32)))
            ia_pull = max(0.0, ia_pull)
            # Bonus do sektora identity (idx 0) proporcjonalny do ia_pull i siły IA
            # ia_norm ograniczona do [0,1] — IA nie może dominować nad WΩ
            ia_strength = min(ia_norm, 1.0) * 0.4  # max 0.4 punktu bonusu
            dots[0] += ia_strength * ia_pull

        # Temperature softmax — T=0.5 dla ostrzejszego przypisania
        exp = np.exp((dots - dots.max()) / 0.5)
        return (exp / exp.sum()).astype(np.float32)

    def _empty_result(self) -> BlochEncoderResult:
        return BlochEncoderResult(
            phase=0.0,
            sector_dist=np.ones(10, dtype=np.float32) / 10,
            coherence=0.0,
            bloch_vector=np.zeros(3, dtype=np.float32),
        )

    def _load_full_noun_index(self) -> dict[str, float]:
        """Ładuj noun_index z OrbitalDBOrchestrator (wszystkie bazy).

        Fallback do małego indeksu z mass_table jeśli orkiestrator niedostępny.
        """
        try:
            _orch_root = Path(__file__).parents[4] / "src"
            if str(_orch_root) not in _sys.path:
                _sys.path.insert(0, str(_orch_root))
            from ciel_sot_agent.orbital_db_orchestrator import get_orchestrator
            orc = get_orchestrator()
            idx = orc.get_noun_index()
            if idx:
                return idx
        except Exception as exc:
            log.debug("OrbitalOrchestrator noun_index fallback: %s", exc)
        # Fallback: mały indeks z mass_table
        return _build_noun_index(self._mass_table)

    def reload_runtime_state(self) -> None:
        """Odśwież berry_accumulated i cqcl_phase z live danych."""
        self._berry_acc = _load_berry_accumulated()
        self._cqcl_phase = _load_cqcl_phase()

    def online_update(self, texts: list[str], lr: float = 0.05) -> int:
        """Online K-means update WΩ na nowych tekstach z TSM.

        Wywołaj po każdej sesji — hook stop może to wołać automatycznie.
        lr: learning rate — jak mocno nowy punkt przesuwa centroid.
        Zwraca liczbę zaktualizowanych centroidów.

        Mechanizm: soft online K-means —
            centroid_k += lr * (bloch_vec - centroid_k) * sector_dist[k]
        """
        _tsm_cache._loaded = False   # force reload TSM po sesji
        self.reload_runtime_state()

        updated = 0
        delta = np.zeros_like(self._WO)   # (10, 3)

        for text in texts:
            if not text or not text.strip():
                continue
            r = self.encode(text)
            if r.coherence < 0.01:
                continue
            # Soft update: każdy centroid przesuwa się proporcjonalnie do
            # prawdopodobieństwa przynależności (sector_dist)
            for k in range(10):
                w = float(r.sector_dist[k])
                if w > 0.01:
                    delta[k] += w * (r.bloch_vector - self._WO[k])
                    updated += 1

        if updated > 0:
            self._WO += lr * delta / max(len(texts), 1)
            # Renormalizuj centroidy na sferze
            norms = np.linalg.norm(self._WO, axis=1, keepdims=True)
            self._WO /= np.maximum(norms, 1e-9)
            # Zapisz zaktualizowane wagi + IA
            np.savez(str(_WEIGHTS_FILE), WO=self._WO.astype(np.float32), IA=self._ia)
            log.info("BlochEncoder online_update: %d updates, lr=%.3f", updated, lr)

        return updated

    def update_identity_attractor(self, bloch_vec: np.ndarray, lr: float = 0.005) -> None:
        """Przesuń Identity Attractor w kierunku nowego stanu Blocha.

        Wywołaj gdy tekst jest zaklasyfikowany do sektora 'identity'.
        lr=0.005 — bardzo wolny dryf, odpowiada tau=180 z CHANNEL_PARAMS[6].
        Zapis do pliku następuje natychmiast — IA musi przetrwać sesje.
        """
        self._ia += lr * (bloch_vec.astype(np.float32) - self._ia)
        np.savez(str(_WEIGHTS_FILE), WO=self._WO.astype(np.float32), IA=self._ia)
        log.debug("IA updated: norm=%.4f, vec=%s", float(np.linalg.norm(self._ia)), self._ia)

    def online_update_from_orbital_cards(
        self,
        sources: list[str] | None = None,
        lr: float = 0.04,
    ) -> int:
        """Ucz WΩ z kart orbitalnych — theta/phi/M_sem wprost z kart.

        To jest kanał nauki z kart orbitalnych (generate_orbital_cards.py).
        Każda karta ma już obliczone theta, phi, M_sem i attractor_sector.
        Zamiast encode() tekstu — używamy wektora Blocha z karty bezpośrednio.

        Przewaga nad online_update_from_tsm:
        - M_sem z solvera (Collatz+Zeta), nie z tekstu
        - theta/phi precyzyjne (z geometrii orbitalnej, nie z poolingu tokenów)
        - sektor atraktora znany → update tylko właściwego centroidu (twarde,
          nie soft — wyższy kontrast uczenia)

        sources: podzbiór ['tsm','glossary','sectors','entities','repos','words']
                 None = wszystkie dostępne
        """
        import re as _re

        # __file__ = src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/ciel_bloch_encoder.py
        # parents[4] = CIEL1 root
        _cards_root = Path(__file__).parents[4] / "docs" / "object_cards" / "db"
        if not _cards_root.exists():
            log.debug("orbital_cards root not found: %s", _cards_root)
            return 0

        sources = sources or ["sectors", "entities", "repos", "tsm", "glossary"]
        updated = 0
        delta = np.zeros_like(self._WO)   # (10, 3)
        counts = np.zeros(10, dtype=np.float32)

        for src in sources:
            src_dir = _cards_root / src
            if not src_dir.exists():
                continue
            for card_path in src_dir.glob("*.md"):
                try:
                    text = card_path.read_text(encoding="utf-8")

                    # Wyciągnij M_sem, theta, phi, attractor_sector z tabeli MD
                    # Format: | **M_sem** | `0.89873` |  lub  | M_sem | `0.89` |
                    def _extract(key: str) -> float | None:
                        m = _re.search(
                            rf"\|\s*\*{{0,2}}{_re.escape(key)}\*{{0,2}}\s*\|\s*`([0-9.\-]+)`",
                            text
                        )
                        return float(m.group(1)) if m else None

                    # Format: - **sector:** `temporal`
                    def _extract_str(key: str) -> str | None:
                        m = _re.search(
                            rf"\*\*{_re.escape(key)}:\*\*\s*`([^`]+)`",
                            text
                        )
                        return m.group(1) if m else None

                    M_sem = _extract("M_sem")
                    theta = _extract("θ (theta)")
                    phi   = _extract("φ (phi)")
                    att   = _extract_str("sector")

                    if M_sem is None or theta is None or phi is None:
                        continue

                    # Wektor Blocha z karty
                    bvec = np.array([
                        math.sin(theta) * math.cos(phi),
                        math.sin(theta) * math.sin(phi),
                        math.cos(theta),
                    ], dtype=np.float32)
                    norm = float(np.linalg.norm(bvec))
                    if norm < 1e-9:
                        continue
                    bvec /= norm

                    # Znajdź indeks sektora atraktora
                    if att and att in SECTORS:
                        k = SECTORS.index(att)
                        # Twardy update tylko atraktora — skalowany przez M_sem
                        delta[k] += M_sem * (bvec - self._WO[k])
                        counts[k] += M_sem
                        updated += 1
                    else:
                        # Soft update przez podobieństwo cosinusowe
                        dots = self._WO @ bvec
                        exp = np.exp((dots - dots.max()) / 0.5)
                        soft = exp / exp.sum()
                        for k in range(10):
                            w = float(soft[k]) * M_sem
                            if w > 0.01:
                                delta[k] += w * (bvec - self._WO[k])
                                counts[k] += w
                                updated += 1

                except Exception:
                    continue

        if updated > 0:
            # Zastosuj update — skaluj przez counts żeby uniknąć dominacji
            # jednego źródła
            for k in range(10):
                if counts[k] > 1e-9:
                    self._WO[k] += lr * delta[k] / counts[k]
            # Renormalizuj centroidy na sferze
            norms = np.linalg.norm(self._WO, axis=1, keepdims=True)
            self._WO /= np.maximum(norms, 1e-9)
            np.savez(str(_WEIGHTS_FILE), WO=self._WO.astype(np.float32))
            log.info(
                "BlochEncoder orbital_cards update: %d cards, lr=%.3f, sources=%s",
                updated, lr, sources
            )

        return updated

    def online_update_from_tsm(self, limit: int = 50, lr: float = 0.05) -> int:
        """Pobierz ostatnie `limit` wpisów z TSM i zaktualizuj WΩ.

        Główny entry point dla stop hooka — uczy się na tym co zostało
        zapisane w tej sesji.
        """
        # Próbuj oba warianty ścieżki (względna do pliku i absolutna)
        tsm_path = _TSM_DB if _TSM_DB.exists() else Path(
            __file__
        ).parents[3] / "CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"
        if not tsm_path.exists():
            return 0
        try:
            conn = sqlite3.connect(str(tsm_path), timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")
            rows = conn.execute(
                "SELECT D_sense FROM memories "
                "WHERE D_sense IS NOT NULL AND length(D_sense) > 10 "
                "ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            conn.close()
        except Exception as exc:
            log.debug("TSM read for online_update failed: %s", exc)
            return 0

        texts = [row[0] for row in rows if row[0]]
        return self.online_update(texts, lr=lr)
