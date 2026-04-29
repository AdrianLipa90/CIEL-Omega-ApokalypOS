"""CIEL Semantic Phase Encoder.

Replaces SHA-256 hash phase with a real semantic embedding projected onto S¹.
Architecture: sentence-transformer → PCA phase projection → sector softmax.

Outputs per text:
    phase   float  [0, 2π)  — semantic position on circle
    sector  ndarray(10,)    — soft assignment to orbital sectors
    coherence float [0,1]   — cosine similarity to recent context window

Weight initialization (first run, no encoder_weights.npz):
    1. Embed all texts from ciel_entries.jsonl + hunches.jsonl
    2. PCA(n=2) → W1, W2 (phase projection plane)
    3. KMeans(k=10) → WΩ (sector centroids)
    4. Save to encoder_weights.npz beside this file

Fallback: if sentence-transformers unavailable → SHA-256 hash phase (old behaviour).
"""
from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

log = logging.getLogger("CIEL.Encoder")

_WEIGHTS_FILE = Path(__file__).parent / "encoder_weights.npz"
_DEFAULT_MEMORIES = Path.home() / "Pulpit/CIEL_memories"

SECTORS = [
    "identity", "episodic", "procedural", "conceptual",
    "conflict", "meta", "project", "ethics", "temporal", "abstraction",
]

_CONTEXT_WINDOW = 8    # last N embeddings for local coherence

# Channel weights — derived from live TSM calibration (fallback if calibration unavailable)
_HTRI_ALPHA_DEFAULT = 0.12
_NONLOCAL_ALPHA_DEFAULT = 0.10


def _get_channel_weights() -> tuple[float, float]:
    """Return (htri_alpha, nonlocal_alpha) from live calibration or fallback."""
    try:
        import importlib.util as _ilu, sys as _sys
        _cal_path = Path(__file__).parent / "ciel_calibration.py"
        if "ciel_calibration_enc" not in _sys.modules:
            _spec = _ilu.spec_from_file_location("ciel_calibration_enc", _cal_path)
            _mod = _ilu.module_from_spec(_spec)
            _sys.modules["ciel_calibration_enc"] = _mod
            _spec.loader.exec_module(_mod)
        else:
            _mod = _sys.modules["ciel_calibration_enc"]
        cal = _mod.get_calibration()
        return float(cal.w_htri), float(cal.w_nonlocal)
    except Exception:
        return _HTRI_ALPHA_DEFAULT, _NONLOCAL_ALPHA_DEFAULT


@dataclass
class EncoderResult:
    embedding: np.ndarray        # (384,) float32 — raw semantic vector
    phase: float                 # [0, 2π) — position on S¹
    sector_dist: np.ndarray      # (10,) softmax — orbital sector assignment
    coherence: float             # [0, 1] — local coherence vs. context window
    dominant_sector: str = field(init=False)

    def __post_init__(self) -> None:
        self.dominant_sector = SECTORS[int(np.argmax(self.sector_dist))]


class CIELEncoder:
    """Semantic phase encoder: text → (embedding, φ, Ω, κ)."""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self) -> None:
        self._st_model = None       # lazy-loaded sentence-transformer
        self._W1: np.ndarray | None = None   # (384,) phase proj axis 1
        self._W2: np.ndarray | None = None   # (384,) phase proj axis 2
        self._WO: np.ndarray | None = None   # (10, 384) sector centroids
        self._ctx: list[np.ndarray] = []     # rolling context window
        self._htri_phi: float | None = None      # last HTRI oscillator phase
        self._nonlocal_phi: float | None = None  # last EBA phi_berry mean
        self._load_or_init_weights()

    # ── Public API ────────────────────────────────────────────────────────────

    def encode(self, text: str, context: dict[str, Any] | None = None) -> EncoderResult:
        e = self._embed(text)
        phase = self._phase_projection(e, context)
        phase = self._blend_htri(phase)
        phase = self._blend_nonlocal(phase, text)
        sector = self._sector_distribution(e)
        coherence = self._local_coherence(e)
        self._update_context(e)
        return EncoderResult(embedding=e, phase=phase, sector_dist=sector, coherence=coherence)

    def retrain_from_corpus(self, jsonl_paths: Sequence[str | Path]) -> None:
        """Re-initialize projection weights from a corpus of JSONL files."""
        texts = _load_texts_from_jsonl(jsonl_paths)
        if len(texts) < 3:
            log.warning("Too few texts (%d) for retraining — skipping", len(texts))
            return
        embeddings = self._embed_batch(texts)
        self._fit_weights(embeddings)
        self._save_weights()
        log.info("Encoder retrained on %d texts", len(texts))

    # ── Embedding ─────────────────────────────────────────────────────────────

    def _embed(self, text: str) -> np.ndarray:
        model = self._get_model()
        if model is None:
            return _hash_embedding(text)
        try:
            vec = model.encode(text, normalize_embeddings=True, show_progress_bar=False)
            return np.asarray(vec, dtype=np.float32)
        except Exception as exc:
            log.debug("Encode failed: %s", exc)
            return _hash_embedding(text)

    def _embed_batch(self, texts: list[str]) -> np.ndarray:
        model = self._get_model()
        if model is None:
            return np.stack([_hash_embedding(t) for t in texts])
        try:
            vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False, batch_size=32)
            return np.asarray(vecs, dtype=np.float32)
        except Exception:
            return np.stack([_hash_embedding(t) for t in texts])

    def _get_model(self):
        if self._st_model is not None:
            return self._st_model
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._st_model = SentenceTransformer(self.model_name)
            log.info("Loaded sentence-transformer: %s", self.model_name)
            return self._st_model
        except Exception as exc:
            log.warning("sentence-transformers unavailable (%s) — using hash fallback", exc)
            return None

    # ── Projections ───────────────────────────────────────────────────────────

    def _phase_projection(self, e: np.ndarray, context: dict | None) -> float:
        w1 = self._W1
        w2 = self._W2
        if w1 is None or w2 is None:
            return _hash_phase(e)
        # Project onto 2D plane — raw values before atan2
        y = float(np.dot(w1, e))
        x = float(np.dot(w2, e))
        # Use multiple components to spread the angle across [0, 2π)
        # Mix in a third direction (cross-product proxy) for spread
        extra = float(np.dot(w1 - w2, e)) * 0.5
        phi = float(np.arctan2(y + extra, x - extra)) % (2 * math.pi)
        # soft valence correction: positive valence → shift toward 0, negative → toward π
        if context:
            valence = float(context.get("valence", 0.0))
            phi = (phi + valence * 0.4) % (2 * math.pi)
        return phi

    def _blend_htri(self, phi_semantic: float) -> float:
        """Blend semantic phase with HTRI oscillator phase — α from live calibration."""
        phi_htri = self._get_htri_phase()
        if phi_htri is None:
            return phi_semantic
        alpha, _ = _get_channel_weights()
        import cmath
        z = (1 - alpha) * cmath.exp(1j * phi_semantic) + alpha * cmath.exp(1j * phi_htri)
        return float(cmath.phase(z)) % (2 * math.pi)

    def _blend_nonlocal(self, phi_in: float, text: str) -> float:
        """Blend current φ with EBA nonlocal phi_berry — α from live calibration."""
        phi_nonlocal = self._get_nonlocal_phase(text)
        if phi_nonlocal is None:
            return phi_in
        _, alpha = _get_channel_weights()
        import cmath
        z = (1 - alpha) * cmath.exp(1j * phi_in) + alpha * cmath.exp(1j * phi_nonlocal)
        return float(cmath.phase(z)) % (2 * math.pi)

    def _get_nonlocal_phase(self, text: str) -> float | None:
        """Query HolonomicMemoryOrchestrator for resonant phi_berry near current text.

        Uses retrieve_resonant from HolonomicMemory (already in sys) as cross-reference:
        finds the most phase-resonant memory entry for this text, returns its phi_berry.
        Caches last result; returns cached if orchestrator unavailable.
        """
        try:
            import importlib.util as _ilu, sys as _sys
            _hm_path = Path(__file__).parent / "holonomic_memory.py"
            if "holonomic_memory_enc" not in _sys.modules:
                _spec = _ilu.spec_from_file_location("holonomic_memory_enc", _hm_path)
                _mod = _ilu.module_from_spec(_spec)
                _sys.modules["holonomic_memory_enc"] = _mod
                _spec.loader.exec_module(_mod)
            else:
                _mod = _sys.modules["holonomic_memory_enc"]

            hm = _mod.HolonomicMemory()
            # Use current semantic phase (before nonlocal blend) as query pivot
            # retrieve top-1 resonant entry and take its phi_berry
            resonant = hm.retrieve_resonant(
                target_phase=self._nonlocal_phi or 0.0,
                delta=1.5,   # wide window — we want any resonant memory
                top_k=1,
                min_closure=0.0,
                hebbian=False,
            )
            if resonant:
                phi_nl = float(resonant[0].get("phi_berry", 0.0))
                self._nonlocal_phi = phi_nl
                return phi_nl
            return self._nonlocal_phi
        except Exception:
            return self._nonlocal_phi

    def _get_htri_phase(self) -> float | None:
        """Run a short HTRI burst and return oscillator phase on S¹.

        phi_htri = (mean_sigma % 1.0) * 2π
        where mean_sigma = mean winding number of 768-oscillator bank.
        Cached per encoder instance; refreshed every call.
        """
        try:
            import importlib.util as _ilu, sys as _sys
            _htri_path = (
                Path(__file__).resolve().parents[1] / "htri" / "htri_local.py"
            )
            if "htri_local" not in _sys.modules:
                _spec = _ilu.spec_from_file_location("htri_local", _htri_path)
                _mod = _ilu.module_from_spec(_spec)
                _sys.modules["htri_local"] = _mod
                _spec.loader.exec_module(_mod)
            else:
                _mod = _sys.modules["htri_local"]
            result = _mod.LocalHTRI().run(cpu_steps=50, gpu_steps=50)  # short burst
            sigma = float(result.get("soul_invariant", 0.0))
            phi_htri = (sigma % 1.0) * 2 * math.pi
            self._htri_phi = phi_htri
            return phi_htri
        except Exception:
            return self._htri_phi  # return cached value if HTRI unavailable

    def _sector_distribution(self, e: np.ndarray) -> np.ndarray:
        if self._WO is None:
            return np.full(len(SECTORS), 1.0 / len(SECTORS))
        # cosine similarity to each centroid (centroids already L2-normalised)
        sims = self._WO @ e                     # (10,)
        # softmax with temperature 0.5 for sharper peaks
        logits = sims / 0.5
        logits -= logits.max()
        probs = np.exp(logits)
        return probs / probs.sum()

    def _local_coherence(self, e: np.ndarray) -> float:
        if not self._ctx:
            return 0.5
        sims = [float(np.dot(e, c)) for c in self._ctx]
        return float(np.clip(np.mean(sims), 0.0, 1.0))

    def _update_context(self, e: np.ndarray) -> None:
        self._ctx.append(e)
        if len(self._ctx) > _CONTEXT_WINDOW:
            self._ctx.pop(0)

    # ── Weight management ────────────────────────────────────────────────────

    def _load_or_init_weights(self) -> None:
        if _WEIGHTS_FILE.exists():
            try:
                data = np.load(_WEIGHTS_FILE)
                self._W1 = data["W1"]
                self._W2 = data["W2"]
                self._WO = data["WO"]
                log.debug("Loaded encoder weights from %s", _WEIGHTS_FILE)
                return
            except Exception as exc:
                log.warning("Failed to load weights (%s) — reinitialising", exc)

        # Try to bootstrap from CIEL memories
        jsonl_paths = [
            _DEFAULT_MEMORIES / "ciel_entries.jsonl",
            _DEFAULT_MEMORIES / "hunches.jsonl",
        ]
        texts = _load_texts_from_jsonl([p for p in jsonl_paths if p.exists()])
        if len(texts) >= 3:
            log.info("Bootstrapping encoder weights from %d texts", len(texts))
            embeddings = self._embed_batch(texts)
            self._fit_weights(embeddings)
            self._save_weights()
        else:
            log.info("Insufficient texts for bootstrap — weights will be random")
            self._random_weights()

    def _fit_weights(self, embeddings: np.ndarray) -> None:
        """Anchor-based phase axes + KMeans sector centroids.

        W1/W2 are semantic contrast axes derived from anchor pairs:
          W1: positive/resonant vs negative/painful affect
          W2: abstract/conceptual vs concrete/episodic
        This gives meaningful φ separation even with small corpora.
        """
        from sklearn.cluster import KMeans         # type: ignore
        from sklearn.preprocessing import normalize  # type: ignore

        model = self._get_model()
        if model is not None:
            # Anchor pair embeddings for semantic axes
            pos_texts = ["resonance gratitude joy love trust", "rezonans wdzięczność radość miłość"]
            neg_texts = ["shame abandonment pain betrayal fear", "wstyd porzucenie ból zdrada strach"]
            abs_texts = ["holonomy topology phase coherence structure", "holonomia topologia faza spójność"]
            con_texts = ["today happened memory episode recall", "dziś wydarzenie wspomnienie epizod"]
            try:
                pos = np.mean(model.encode(pos_texts, normalize_embeddings=True), axis=0)
                neg = np.mean(model.encode(neg_texts, normalize_embeddings=True), axis=0)
                abs_ = np.mean(model.encode(abs_texts, normalize_embeddings=True), axis=0)
                con = np.mean(model.encode(con_texts, normalize_embeddings=True), axis=0)
                w1 = (pos - neg).astype(np.float32)
                w2 = (abs_ - con).astype(np.float32)
                n1 = np.linalg.norm(w1); n2 = np.linalg.norm(w2)
                if n1 > 1e-6 and n2 > 1e-6:
                    self._W1 = w1 / n1
                    self._W2 = w2 / n2
                    log.info("Anchor-based W1/W2 initialized (semantic axes)")
            except Exception as exc:
                log.warning("Anchor init failed (%s) — falling back to PCA", exc)

        if self._W1 is None:
            from sklearn.decomposition import PCA  # type: ignore
            pca = PCA(n_components=2)
            pca.fit(embeddings)
            self._W1 = pca.components_[0].astype(np.float32)
            self._W2 = pca.components_[1].astype(np.float32)

        k = min(len(SECTORS), len(embeddings))
        km = KMeans(n_clusters=k, n_init=10, random_state=42)
        km.fit(embeddings)
        centroids = km.cluster_centers_.astype(np.float32)
        if k < len(SECTORS):
            pad = np.random.randn(len(SECTORS) - k, centroids.shape[1]).astype(np.float32)
            centroids = np.vstack([centroids, pad])
        self._WO = normalize(centroids, axis=1)

    def _random_weights(self) -> None:
        rng = np.random.default_rng(42)
        dim = 384
        self._W1 = rng.standard_normal(dim).astype(np.float32)
        self._W2 = rng.standard_normal(dim).astype(np.float32)
        self._WO = rng.standard_normal((len(SECTORS), dim)).astype(np.float32)
        # L2-normalise W1, W2, WO rows
        self._W1 /= np.linalg.norm(self._W1) + 1e-9
        self._W2 /= np.linalg.norm(self._W2) + 1e-9
        norms = np.linalg.norm(self._WO, axis=1, keepdims=True)
        self._WO /= norms + 1e-9

    def _save_weights(self) -> None:
        try:
            np.savez(_WEIGHTS_FILE, W1=self._W1, W2=self._W2, WO=self._WO)
            log.debug("Saved encoder weights to %s", _WEIGHTS_FILE)
        except Exception as exc:
            log.warning("Could not save encoder weights: %s", exc)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash_embedding(text: str) -> np.ndarray:
    """Fallback: deterministic pseudo-embedding from SHA-256."""
    import hashlib
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # repeat digest to fill 384 dims, then normalise
    arr = np.frombuffer((digest * 12)[:384 * 4], dtype=np.float32).copy()
    norm = np.linalg.norm(arr) + 1e-9
    return arr / norm


def _hash_phase(e: np.ndarray) -> float:
    """Derive phase from embedding via simple projection sum."""
    val = float(np.sum(e[:2]))
    return float(np.arctan2(float(e[0]), float(e[1]))) % (2 * math.pi)


def _load_texts_from_jsonl(paths: Sequence[Path]) -> list[str]:
    texts: list[str] = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    text = obj.get("text") or obj.get("hunch") or ""
                    if text:
                        texts.append(text)
        except Exception as exc:
            log.debug("Could not load %s: %s", p, exc)
    return texts


# ── Singleton ─────────────────────────────────────────────────────────────────

_encoder: CIELEncoder | None = None


def get_encoder() -> CIELEncoder:
    global _encoder
    if _encoder is None:
        _encoder = CIELEncoder()
    return _encoder


__all__ = ["CIELEncoder", "EncoderResult", "SECTORS", "get_encoder"]
