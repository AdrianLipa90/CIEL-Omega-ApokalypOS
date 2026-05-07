"""CIEL Consolidation Resonator — średnioterminowa pamięć fazowa.

Pipeline:
  1. TAG MAPPER     — normalizacja 1502 tagów → klastry kanoniczne
  2. TAG CARDS      — karta per tag: M_sem, phi_tag, winding, sektor
  3. KURAMOTO       — sprzężenie fazowe ostatnich 400 konsolidacji
                      dφ_i/dt = ω_i + (K/N) Σ_j sin(φ_j - φ_i)
  4. TSM WRITE      — każda konsolidacja → wpis D_type='episodic' w TSM
  5. WΩ UPDATE      — faza Kuramoto → online update BlochEncodera

Rezonator średnioterminowy: nie pamiętasz konkretnych słów z 400 sesji,
ale ich fazowy odcisk — co dominowało, jak oscylowało, gdzie był atraktor.
"""
from __future__ import annotations

import json
import math
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Paths ─────────────────────────────────────────────────────────────────────

_ROOT     = Path(__file__).parents[2]
_CONS_DB  = Path.home() / "Pulpit" / "CIEL_memories" / "local_test" / "consolidator.db"
_TSM_DB   = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"
_CARDS_OUT = _ROOT / "docs" / "object_cards" / "db" / "consolidations"

_KURAMOTO_N    = 400    # ostatnie N konsolidacji do sprzężenia
_KURAMOTO_K    = 2.0    # bazowa stała sprzężenia (K_ij = K × M_sem_wspólnych_tagów)
_KURAMOTO_STEPS = 50    # iteracje numeryczne
_KURAMOTO_DT   = 0.05
_KURAMOTO_SIGMA = 0.3   # rozproszenie ω (Lorentz): im wyższe, tym więcej napięcia
_PHASE_STATE_FILE = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/kuramoto_state.npz"

# ── Affect → phi mapping (8 afektów = 8 sektorów na kole faz) ────────────────

_AFFECT_PHI = {
    "focused":    0.0,
    "curious":    math.pi / 4,
    "joy":        math.pi / 2,
    "calm":       3 * math.pi / 4,
    "relief":     math.pi,
    "sad":        5 * math.pi / 4,
    "anxious":    3 * math.pi / 2,
    "frustrated": 7 * math.pi / 4,
    "grief":      7 * math.pi / 4,
    "love":       math.pi / 2,
    "unknown":    0.0,
}

# ── Tag normalizer ────────────────────────────────────────────────────────────

def _load_entity_tag_aliases() -> dict[str, str]:
    """Auto-generate tag aliases from ciel_entity_cards.yaml: ent_X ↔ noun."""
    try:
        import yaml
        cards_path = Path(__file__).resolve().parents[2] / "integration" / "registries" / "ciel_entity_cards.yaml"
        if not cards_path.exists():
            return {}
        data = yaml.safe_load(cards_path.read_text(encoding="utf-8"))
        result: dict[str, str] = {}
        for card in data.get("entities", []):
            eid = card.get("id", "")
            noun = card.get("noun", "").lower().strip()
            if not (eid and noun):
                continue
            ent_key = eid.replace("entity:", "ent_").replace("-", "_").replace(".", "_").lower()
            result[ent_key] = noun
            result[noun] = noun
        return result
    except Exception:
        return {}


# Ręczne aliasy dla najczęstszych duplikatów (PL/EN, spacja/podkreślenie)
_TAG_ALIASES: dict[str, str] = {
    "session_tracking":    "śledzenie sesji",
    "session tracking":    "śledzenie sesji",
    "ciągłość sesji":      "śledzenie sesji",
    "kontynuacja pracy":   "powrót do kontekstu",
    "powrót do pracy":     "powrót do kontekstu",
    "przerwa sesji":       "przerwanie sesji",
    "hook_debug":          "debug hooków",
    "system_health":       "zdrowie systemu",
    "metryki systemu":     "metryki",
    "metryki ciel":        "metryki",
    "architektura systemu":"architektura ciel",
    "self-presentation":   "autodefinicja",
    "session restart":     "restart",
    "restart metryki":     "restart",
    "orbital bridge":      "orbital bridge",
    "relacja adrian-claude": "relacja adrian-ciel",
    "transcript_logging":  "śledzenie sesji",
    "pamięć":              "pamięć sesji",
    "kontekst sesji":      "powrót do kontekstu",
    "normalizacja":        "normalizacja danych",
    "wrapper":             "architektura ciel",
    "autentykacja":        "autentykacja",
    "źródło anomalii":     "anomalie systemu",
    "monitorowanie energii": "zdrowie systemu",
}
# Merge entity↔tag aliases (entity nouns become valid tag aliases)
_TAG_ALIASES.update(_load_entity_tag_aliases())


def normalize_tag(raw: str) -> str:
    """Normalizuj tag: lowercase, strip, alias lookup."""
    t = raw.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return _TAG_ALIASES.get(t, t)


# ── Dane konsolidacji ─────────────────────────────────────────────────────────

@dataclass
class ConsolidationRecord:
    id: int
    ts: str
    themes: list[str]        # surowe tagi
    tags: list[str]          # znormalizowane tagi
    affect: str
    essence: str
    hunch: str
    phi: float = 0.0         # faza przypisana z affect + tagów
    omega: float = 0.0       # częstość naturalna (z M_sem tagów)
    M_sem: float = 0.5       # masa semantyczna tej konsolidacji


@dataclass
class TagCard:
    tag: str                 # kanoniczny tag
    count: int               # liczba wystąpień
    phi_mean: float          # średnia faza konsolidacji zawierających ten tag
    phi_std: float           # odchylenie standardowe fazy
    M_sem: float             # masa semantyczna tagu
    dominant_affect: str     # najczęstszy affect przy tym tagu
    sector: str              # sektor WΩ atraktora
    winding: float           # skumulowane winding (przejścia 2π)
    aliases: list[str] = field(default_factory=list)


# ── Loader ────────────────────────────────────────────────────────────────────

def load_consolidations(limit: int = _KURAMOTO_N) -> list[ConsolidationRecord]:
    if not _CONS_DB.exists():
        return []
    conn = sqlite3.connect(str(_CONS_DB), timeout=10)
    rows = conn.execute(
        "SELECT id, ts, themes, affect, essence, hunch "
        "FROM consolidations ORDER BY ts DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()

    records = []
    for row_id, ts, themes_raw, affect, essence, hunch in rows:
        try:
            themes = json.loads(themes_raw) if themes_raw else []
        except Exception:
            themes = []
        tags = [normalize_tag(t) for t in themes]
        affect = (affect or "unknown").lower().strip()
        phi = _AFFECT_PHI.get(affect, 0.0)

        records.append(ConsolidationRecord(
            id=row_id, ts=ts or "",
            themes=themes, tags=tags,
            affect=affect, phi=phi,
            essence=essence or "",
            hunch=hunch or "",
        ))
    return records


# ── Tag map builder ───────────────────────────────────────────────────────────

def build_tag_map(records: list[ConsolidationRecord]) -> dict[str, TagCard]:
    """Zbuduj mapę tagów → TagCard z wszystkich konsolidacji."""
    tag_phis: defaultdict[str, list[float]] = defaultdict(list)
    tag_affects: defaultdict[str, list[str]] = defaultdict(list)
    tag_counts: Counter = Counter()

    for rec in records:
        for tag in rec.tags:
            if not tag or len(tag) < 3:
                continue
            tag_counts[tag] += 1
            tag_phis[tag].append(rec.phi)
            tag_affects[tag].append(rec.affect)

    cards: dict[str, TagCard] = {}
    for tag, count in tag_counts.items():
        phis = tag_phis[tag]
        phi_mean = _circular_mean(phis)
        phi_std  = _circular_std(phis, phi_mean)

        # M_sem tagu: log1p(count) × (1 - phi_std/π) × affect_boost
        affect_counter = Counter(tag_affects[tag])
        dom_affect = affect_counter.most_common(1)[0][0]
        affect_boost = {
            "focused": 1.1, "curious": 1.05, "joy": 1.0,
            "frustrated": 0.9, "anxious": 0.85,
        }.get(dom_affect, 1.0)
        M_sem = min(1.0, math.log1p(count) / math.log1p(200)
                    * (1.0 - min(phi_std / math.pi, 0.9))
                    * affect_boost)

        # Winding: ile razy tag "okrążył" koło faz (proxy: spread / 2π)
        winding = phi_std / (2 * math.pi)

        # Sektor: z phi_mean
        sector = _phi_to_sector(phi_mean)

        cards[tag] = TagCard(
            tag=tag, count=count,
            phi_mean=round(phi_mean, 4),
            phi_std=round(phi_std, 4),
            M_sem=round(M_sem, 5),
            dominant_affect=dom_affect,
            sector=sector,
            winding=round(winding, 4),
        )
    return cards


# ── Kuramoto — poprawiony ────────────────────────────────────────────────────

def _load_phase_state(ids: list[int]) -> dict[int, float]:
    """Załaduj poprzedni stan fazowy z pliku .npz → {cons_id: phi}."""
    if not _PHASE_STATE_FILE.exists():
        return {}
    try:
        import numpy as np
        d = np.load(str(_PHASE_STATE_FILE), allow_pickle=True)
        saved_ids  = d["ids"].tolist()
        saved_phis = d["phis"].tolist()
        return dict(zip(saved_ids, saved_phis))
    except Exception:
        return {}


def _save_phase_state(records: list[ConsolidationRecord]) -> None:
    """Zapisz aktualny stan fazowy do .npz — ciągłość między sesjami."""
    import numpy as np
    ids  = np.array([r.id  for r in records], dtype=np.int64)
    phis = np.array([r.phi for r in records], dtype=np.float32)
    np.savez(str(_PHASE_STATE_FILE), ids=ids, phis=phis)


def _build_coupling_matrix(
    records: list[ConsolidationRecord],
    tag_map: dict[str, TagCard],
    K: float,
) -> list[list[float]]:
    """Macierz sprzężenia K_ij — ważona przez M_sem wspólnych tagów.

    K_ij = K × Σ_{t ∈ tags_i ∩ tags_j} M_sem(t)

    Dwie konsolidacje dzielące ciężkie tagi semantycznie
    są mocniej sprzężone niż losowe pary.
    Normalizacja: dzielimy przez max K_ij żeby sprzężenie było w [0, K].
    """
    n = len(records)
    tag_sets = [set(r.tags) for r in records]
    K_mat = [[0.0] * n for _ in range(n)]
    max_k = 0.0

    for i in range(n):
        for j in range(i + 1, n):
            common = tag_sets[i] & tag_sets[j]
            if common:
                k_ij = K * sum(tag_map[t].M_sem for t in common if t in tag_map)
                K_mat[i][j] = k_ij
                K_mat[j][i] = k_ij
                if k_ij > max_k:
                    max_k = k_ij

    # Normalizuj do [0, K]
    if max_k > 1e-9:
        for i in range(n):
            for j in range(n):
                K_mat[i][j] /= max_k / K

    return K_mat


def _lorentz_omega(omega_0: float, sigma: float, seed: int) -> float:
    """Częstość naturalna z rozkładu Lorentza: γ/(π((ω-ω_0)²+γ²)).

    Używamy transformacji odwrotnej CDF: ω = ω_0 + σ·tan(π(u - 0.5))
    gdzie u ∈ (0,1) deterministyczne z seed (cons_id) — powtarzalne między sesjami.
    """
    import hashlib
    u = (int(hashlib.md5(str(seed).encode()).hexdigest(), 16) % 10000) / 10000.0
    u = max(0.001, min(0.999, u))  # unikamy osobliwości
    return omega_0 + sigma * math.tan(math.pi * (u - 0.5))


def kuramoto_sync(
    records: list[ConsolidationRecord],
    tag_map: dict[str, TagCard],
    K: float = _KURAMOTO_K,
    steps: int = _KURAMOTO_STEPS,
    dt: float = _KURAMOTO_DT,
    sigma: float = _KURAMOTO_SIGMA,
) -> list[ConsolidationRecord]:
    """Sprzężenie Kuramoto — poprawiony model.

    Trzy zmiany względem v1:

    1. ROZKŁAD ω: ω_i = ω_0(M_sem) + Lorentz(σ=0.3, seed=cons_id)
       Część oscylatorów ciągnie do przodu, część za — napięcie przed synchronizacją.

    2. CIĄGŁOŚĆ FAZOWA: φ_i startuje z poprzedniego stanu (.npz)
       jeśli konsolidacja była już w poprzednim runie. Holonomia akumuluje.

    3. MACIERZ K_ij: K_ij = K × Σ_{t∈tags_i∩tags_j} M_sem(t)
       Konsolidacje ze wspólnymi ciężkimi tagami są mocniej sprzężone.
       Czyste pary bez wspólnych tagów: K_ij = 0 (brak bezpośredniego sprzężenia).
    """
    import numpy as np
    n = len(records)
    if n == 0:
        return records

    # M_sem per konsolidacja (z tagów)
    for rec in records:
        tag_masses = [tag_map[t].M_sem for t in rec.tags if t in tag_map]
        rec.M_sem = sum(tag_masses) / max(len(tag_masses), 1) if tag_masses else 0.3

    # 1. Omega z rozkładu Lorentza — deterministyczne z cons_id
    omega_0_base = 2 * math.pi  # 1 cykl / jednostkę czasu
    omegas = [
        _lorentz_omega(rec.M_sem * omega_0_base, sigma, rec.id)
        for rec in records
    ]
    for rec, omega in zip(records, omegas):
        rec.omega = omega

    # 2. Fazy startowe — z poprzedniego stanu jeśli dostępne
    prev_state = _load_phase_state([r.id for r in records])
    phis = []
    for rec in records:
        if rec.id in prev_state:
            phis.append(prev_state[rec.id])  # kontynuacja
        else:
            phis.append(rec.phi)  # nowa konsolidacja: affect phi

    # 3. Macierz sprzężenia K_ij (ważona tagami)
    # Dla N=400 macierz 400×400 = 160k elementów — OK
    K_mat = _build_coupling_matrix(records, tag_map, K)

    # Numeryczna integracja — Euler (wystarczy dla demonstracji holonomii)
    phis_arr = np.array(phis, dtype=np.float64)
    omegas_arr = np.array(omegas, dtype=np.float64)
    K_arr = np.array(K_mat, dtype=np.float64)

    for _ in range(steps):
        # dφ_i/dt = ω_i + Σ_j K_ij sin(φ_j - φ_i)
        phi_diff = phis_arr[:, None] - phis_arr[None, :]   # (n, n)
        coupling = (K_arr * np.sin(-phi_diff)).sum(axis=1)  # (n,)
        phis_arr = (phis_arr + dt * (omegas_arr + coupling)) % (2 * math.pi)

    # Zapisz nowy stan fazowy
    for i, rec in enumerate(records):
        rec.phi = round(float(phis_arr[i]), 4)
    _save_phase_state(records)

    return records


def kuramoto_order_parameter(records: list[ConsolidationRecord]) -> tuple[float, float]:
    """r·e^{iΨ} = (1/N) Σ e^{iφ_k} — miara synchronizacji (r=1 pełna, r=0 chaos)."""
    import cmath
    z = sum(cmath.exp(1j * rec.phi) for rec in records) / max(len(records), 1)
    return abs(z), cmath.phase(z) % (2 * math.pi)


# ── Tag cards writer ──────────────────────────────────────────────────────────

def write_tag_cards(tag_map: dict[str, TagCard]) -> int:
    _CARDS_OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    written = 0

    for tag, card in sorted(tag_map.items(), key=lambda x: -x[1].M_sem):
        fname = re.sub(r"[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ_\-]", "_", tag)[:60] + ".md"
        fpath = _CARDS_OUT / fname
        md = f"""# TAG: {tag}

## Identity
- **obj_id:** `tag:{tag}`
- **source:** `consolidations`
- **last_updated:** `{now}`

## Orbital mechanics
| param | value |
|---|---|
| **M_sem** | `{card.M_sem}` |
| count | `{card.count}` |
| φ mean | `{card.phi_mean}` |
| φ std | `{card.phi_std}` |
| winding | `{card.winding}` |

## Attractor
- **sector:** `{card.sector}`
- **dominant_affect:** `{card.dominant_affect}`
"""
        fpath.write_text(md, encoding="utf-8")
        written += 1

    # Index
    lines = [
        "# Consolidation Tag Cards",
        f"*Generated: {now} | {len(tag_map)} tags*",
        "",
        "| tag | M_sem | count | sector | affect |",
        "|---|---|---|---|---|",
    ]
    for tag, card in sorted(tag_map.items(), key=lambda x: -x[1].M_sem)[:100]:
        lines.append(f"| {tag} | `{card.M_sem}` | {card.count} | `{card.sector}` | {card.dominant_affect} |")
    (_CARDS_OUT / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    return written


# ── TSM writer ────────────────────────────────────────────────────────────────

def write_to_tsm(
    records: list[ConsolidationRecord],
    tag_map: dict[str, TagCard],
    kuramoto_r: float,
    kuramoto_psi: float,
) -> int:
    """Zapisz konsolidacje do TSM jako D_type='episodic'.

    Każda konsolidacja → jeden wpis z:
      D_sense  = essence (lub themes jeśli brak)
      D_context= hunch
      phi_berry= phi po Kuramoto
      winding_n= count najbardziej masywnego tagu
      D_type   = 'episodic'
      D_attr   = JSON: {affect, tags, M_sem, kuramoto_r}
    """
    if not _TSM_DB.exists():
        return 0

    import hashlib
    conn = sqlite3.connect(str(_TSM_DB), timeout=15)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=15000")

    written = 0
    now = datetime.now(timezone.utc).isoformat()

    for rec in records:
        sense = rec.essence.strip() if rec.essence.strip() else ", ".join(rec.themes[:3])
        if not sense:
            continue

        mem_id = "cons_" + hashlib.sha256(
            f"{rec.id}:{rec.ts}".encode()
        ).hexdigest()[:12]

        exists = conn.execute(
            "SELECT 1 FROM memories WHERE memorise_id=?", (mem_id,)
        ).fetchone()
        if exists:
            continue

        # winding_n z najmasywniejszego tagu
        top_winding = max(
            (tag_map[t].winding for t in rec.tags if t in tag_map),
            default=0.0
        )
        winding_n = int(top_winding * 10)

        attr = json.dumps({
            "affect": rec.affect,
            "tags": rec.tags[:5],
            "M_sem": round(rec.M_sem, 4),
            "kuramoto_r": round(kuramoto_r, 4),
            "kuramoto_psi": round(kuramoto_psi, 4),
            "cons_id": rec.id,
        }, ensure_ascii=False)

        try:
            conn.execute(
                """INSERT INTO memories
                   (memorise_id, created_at, D_id, D_sense, D_type,
                    D_context, phi_berry, winding_n, D_attr, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    mem_id, now,
                    f"cons_{rec.id}",
                    sense[:500],
                    "episodic",
                    rec.hunch[:200] if rec.hunch else "",
                    rec.phi,
                    winding_n,
                    attr,
                    "consolidation_resonator",
                )
            )
            written += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    return written


# ── WΩ update ─────────────────────────────────────────────────────────────────

def update_encoder_from_kuramoto(
    records: list[ConsolidationRecord],
    lr: float = 0.02,
) -> int:
    """Update BlochEncoder WΩ z faz Kuramoto.

    Każda konsolidacja po synchronizacji ma phi (faza) i M_sem.
    Budujemy wektor Blocha: theta = π(1-M_sem), phi = Kuramoto phi.
    Soft update centroidów proporcjonalny do M_sem.
    """
    try:
        import sys, importlib.util, numpy as np
        enc_path = _ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/ciel_bloch_encoder.py"
        spec = importlib.util.spec_from_file_location("ciel_bloch_encoder", enc_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ciel_bloch_encoder"] = mod
        spec.loader.exec_module(mod)
        enc = mod.CIELBlochEncoder()

        delta = np.zeros_like(enc._WO)
        counts = np.zeros(10, dtype=float)

        for rec in records:
            if rec.M_sem < 0.1:
                continue
            theta = math.pi * (1.0 - min(rec.M_sem, 1.0))
            phi   = rec.phi
            bvec  = np.array([
                math.sin(theta) * math.cos(phi),
                math.sin(theta) * math.sin(phi),
                math.cos(theta),
            ], dtype=np.float32)
            norm = float(np.linalg.norm(bvec))
            if norm < 1e-9:
                continue
            bvec /= norm

            dots = enc._WO @ bvec
            exp  = np.exp((dots - dots.max()) / 0.5)
            soft = exp / exp.sum()

            for k in range(10):
                w = float(soft[k]) * rec.M_sem
                if w > 0.005:
                    delta[k] += w * (bvec - enc._WO[k])
                    counts[k] += w

        updated = 0
        for k in range(10):
            if counts[k] > 1e-9:
                enc._WO[k] += lr * delta[k] / counts[k]
                updated += 1

        norms = np.linalg.norm(enc._WO, axis=1, keepdims=True)
        enc._WO /= np.maximum(norms, 1e-9)
        np.savez(str(mod._WEIGHTS_FILE), WO=enc._WO.astype(np.float32))
        return updated
    except Exception as exc:
        return 0


# ── Helpers ───────────────────────────────────────────────────────────────────

def _circular_mean(phis: list[float]) -> float:
    import cmath
    z = sum(cmath.exp(1j * p) for p in phis) / max(len(phis), 1)
    return cmath.phase(z) % (2 * math.pi)


def _circular_std(phis: list[float], mean: float) -> float:
    if len(phis) < 2:
        return 0.0
    diffs = [min(abs(p - mean), 2*math.pi - abs(p - mean)) for p in phis]
    return math.sqrt(sum(d**2 for d in diffs) / len(diffs))


_WO_SECTORS = [
    "identity", "episodic", "procedural", "conceptual",
    "conflict", "meta", "project", "ethics", "temporal", "abstraction",
]

def _phi_to_sector(phi: float) -> str:
    idx = int((phi / (2 * math.pi)) * 10) % 10
    return _WO_SECTORS[idx]


# ── Public entry point ────────────────────────────────────────────────────────

def run(
    n: int = _KURAMOTO_N,
    write_tsm: bool = True,
    write_cards: bool = True,
    update_wo: bool = True,
    verbose: bool = True,
) -> dict[str, Any]:
    """Uruchom pełny pipeline resonatora.

    Returns raport: {n_records, n_tags, kuramoto_r, kuramoto_psi,
                     tsm_written, cards_written, wo_updated}
    """
    report: dict[str, Any] = {}

    # 1. Załaduj konsolidacje
    records = load_consolidations(limit=n)
    report["n_records"] = len(records)
    if verbose:
        print(f"Konsolidacje: {len(records)}")

    # 2. Buduj mapę tagów
    tag_map = build_tag_map(records)
    report["n_tags"] = len(tag_map)
    if verbose:
        print(f"Unikalne tagi: {len(tag_map)}")

    # 3. Kuramoto
    records = kuramoto_sync(records, tag_map)
    r, psi = kuramoto_order_parameter(records)
    report["kuramoto_r"]   = round(r, 4)
    report["kuramoto_psi"] = round(psi, 4)
    if verbose:
        print(f"Kuramoto: r={r:.4f}, Ψ={psi:.4f} ({'synchronizacja' if r > 0.6 else 'chaos' if r < 0.3 else 'częściowa sync'})")

    # 4. Karty tagów
    if write_cards:
        n_cards = write_tag_cards(tag_map)
        report["cards_written"] = n_cards
        if verbose:
            print(f"Tag cards: {n_cards} → {_CARDS_OUT}")

    # 5. TSM
    if write_tsm:
        n_tsm = write_to_tsm(records, tag_map, r, psi)
        report["tsm_written"] = n_tsm
        if verbose:
            print(f"TSM: {n_tsm} nowych wpisów")

    # 6. WΩ update
    if update_wo:
        n_wo = update_encoder_from_kuramoto(records)
        report["wo_updated"] = n_wo
        if verbose:
            print(f"WΩ centroidy zaktualizowane: {n_wo}")

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(level=logging.WARNING)

    n = int(sys.argv[1]) if len(sys.argv) > 1 else _KURAMOTO_N
    print(f"CIEL Consolidation Resonator — ostatnie {n} konsolidacji\n")
    report = run(n=n)
    print(f"\nRaport: {json.dumps(report, indent=2, ensure_ascii=False)}")
