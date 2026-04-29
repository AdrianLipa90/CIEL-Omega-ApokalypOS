#!/usr/bin/env python3
"""CIEL Retrieval Benchmark — 4 warianty, tylko wewnętrzny pipeline.

Porównuje:
  CIEL-FULL       — holonomic_weight (faza + CP² + Poincaré + Hebbian spreading)
  CIEL-PHASE-ONLY — ranking po odległości fazowej |φ_berry − φ_query|
  CIEL-COSINE     — cosine similarity embeddingów (odpowiednik vector DB)
  CIEL-RANDOM     — null hypothesis

Ground truth: proxy relevance z tagów hunches + słów kluczowych ciel_entries.
Metryki: Precision@k (k=1,3,5), MRR, phase_resonance@k, mean_closure, latency.

Usage:
    python3 scripts/ciel_benchmark_retrieval.py [--dry-run] [--k 5] [--top-n 50]
"""
from __future__ import annotations

import argparse
import importlib.util as ilu
import json
import math
import random
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"
_MEM_DIR = Path.home() / "Pulpit/CIEL_memories"
_DB = _SRC / "CIEL_MEMORY_SYSTEM" / "TSM" / "ledger" / "memory_ledger.db"
_REPORTS = _ROOT / "integration" / "reports"

# ── Loader helpers ────────────────────────────────────────────────────────────

def _load(name: str, rel: str):
    path = _SRC / "ciel_omega" / "memory" / rel
    if name in sys.modules:
        return sys.modules[name]
    spec = ilu.spec_from_file_location(name, path)
    mod = ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Ground truth construction ─────────────────────────────────────────────────

def _keywords_from_tags(tags: list[str]) -> set[str]:
    """Expand tag list to a set of lowercase search terms."""
    kw = set()
    for t in tags:
        kw.add(t.lower())
        # split snake_case and hyphenated
        for part in t.replace("-", "_").split("_"):
            if len(part) > 2:
                kw.add(part.lower())
    return kw


def _text_relevant(d_sense: str, keywords: set[str]) -> bool:
    """True if d_sense contains at least one keyword."""
    if not d_sense or not keywords:
        return False
    lower = d_sense.lower()
    return any(kw in lower for kw in keywords)


def _build_query_set(enc, conn: sqlite3.Connection, top_n: int) -> list[dict]:
    """Build query set from hunches + ciel_entries with proxy relevance labels.

    Each query:
        text         str   — the query text
        phi_query    float — encoded phase
        embedding    ndarray(384,) — encoded embedding
        keywords     set[str] — relevance signal
        relevant_ids set[str] — TSM memorise_ids deemed relevant
        source       str   — "hunch" | "ciel_entry"
    """
    queries = []

    # ── Hunches ───────────────────────────────────────────────────────────────
    hunch_file = _MEM_DIR / "hunches.jsonl"
    if hunch_file.exists():
        for line in hunch_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                h = json.loads(line)
            except Exception:
                continue
            text = h.get("hunch", "").strip()
            tags = h.get("tags", [])
            if len(text) < 20 or not tags:
                continue
            queries.append({"text": text, "keywords": _keywords_from_tags(tags),
                            "source": "hunch"})

    # ── CIEL entries ──────────────────────────────────────────────────────────
    entry_file = _MEM_DIR / "ciel_entries.jsonl"
    if entry_file.exists():
        for line in entry_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            text = e.get("text", "").strip()
            if len(text) < 30:
                continue
            # Extract keywords from first 100 chars — nouns & technical terms
            kw_raw = set(w.strip(".,;:()[]") for w in text.split()
                         if len(w) > 4 and w[0].isupper() or "_" in w or
                         any(c.isdigit() for c in w))
            kw = {k.lower() for k in kw_raw if len(k) > 3}
            if not kw:
                continue
            queries.append({"text": text[:400], "keywords": kw, "source": "ciel_entry"})

    # Limit + shuffle for reproducibility
    rng = random.Random(42)
    rng.shuffle(queries)
    queries = queries[:top_n]

    # ── Fetch all corpus entries with phi_berry ────────────────────────────────
    rows = conn.execute(
        "SELECT memorise_id, D_sense, phi_berry, closure_score, winding_n "
        "FROM memories WHERE phi_berry IS NOT NULL AND D_sense IS NOT NULL"
    ).fetchall()

    corpus = [{"memorise_id": r[0], "D_sense": (r[1] or "")[:300],
               "phi_berry": float(r[2] or 0.0),
               "closure_score": float(r[3] or 0.0),
               "winding_n": int(r[4] or 0)} for r in rows]

    # ── Batch-encode queries (pure semantic, no HTRI/nonlocal blending) ────────
    # Use _embed + _phase_projection directly to avoid expensive nonlocal lookups
    query_texts = [q["text"] for q in queries]
    print(f"  Batch-encoding {len(query_texts)} queries…")
    t0 = time.time()
    import numpy as np
    embeddings = enc._embed_batch(query_texts)
    print(f"  Encoded in {time.time()-t0:.1f}s")

    enriched = []
    for q, emb in zip(queries, embeddings):
        phi_q = enc._phase_projection(emb, None)
        kw = q["keywords"]
        rel_ids = {c["memorise_id"] for c in corpus
                   if _text_relevant(c["D_sense"], kw)}
        if not rel_ids:
            continue
        enriched.append({
            "text":         q["text"],
            "phi_query":    phi_q,
            "embedding":    np.asarray(emb),
            "keywords":     kw,
            "relevant_ids": rel_ids,
            "source":       q["source"],
        })

    return enriched, corpus


# ── Variant runners ───────────────────────────────────────────────────────────

def _cyclic_dist(a: float, b: float) -> float:
    diff = (a - b + math.pi) % (2 * math.pi) - math.pi
    return abs(diff)


def _cosine(a, b) -> float:
    import numpy as np
    n = float(np.dot(a, b))
    d = float(np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return n / d


def _rank_ciel_full(hm, phi_query: float, k: int, delta: float | None) -> list[dict]:
    return hm.retrieve_resonant(phi_query, delta=delta, top_k=k, hebbian=False)


def _rank_phase_only(corpus: list[dict], phi_query: float, k: int) -> list[dict]:
    ranked = sorted(corpus, key=lambda c: _cyclic_dist(c["phi_berry"], phi_query))
    return ranked[:k]


def _rank_cosine(corpus_emb: list[tuple], emb_query, k: int) -> list[dict]:
    scored = [(c, _cosine(emb_query, emb)) for c, emb in corpus_emb]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in scored[:k]]


def _rank_random(corpus: list[dict], k: int, rng: random.Random) -> list[dict]:
    return rng.sample(corpus, min(k, len(corpus)))


# ── Metrics ───────────────────────────────────────────────────────────────────

def _precision_at_k(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    if not retrieved_ids:
        return 0.0
    hits = sum(1 for rid in retrieved_ids if rid in relevant_ids)
    return hits / len(retrieved_ids)


def _reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    for i, rid in enumerate(retrieved_ids, 1):
        if rid in relevant_ids:
            return 1.0 / i
    return 0.0


def _phase_resonance(retrieved: list[dict], phi_query: float, delta: float) -> float:
    if not retrieved:
        return 0.0
    in_window = sum(1 for r in retrieved
                    if _cyclic_dist(r.get("phi_berry", 0.0), phi_query) <= delta)
    return in_window / len(retrieved)


def _mean_closure(retrieved: list[dict]) -> float:
    vals = [float(r.get("closure_score") or 0.0) for r in retrieved]
    return sum(vals) / max(len(vals), 1)


# ── Main benchmark loop ───────────────────────────────────────────────────────

def _run_benchmark(queries: list[dict], corpus: list[dict],
                   corpus_emb: list[tuple], hm, cal,
                   k: int, dry_run: bool) -> dict:
    delta_natural = float(cal.delta_natural)
    rng = random.Random(0)
    variants = ["CIEL-FULL", "CIEL-PHASE-ONLY", "CIEL-COSINE", "CIEL-RANDOM"]
    results = {v: {"p1": [], "p3": [], "p5": [], "mrr": [],
                   "resonance": [], "closure": [], "latency_ms": []}
               for v in variants}

    for i, q in enumerate(queries):
        phi_q = q["phi_query"]
        emb_q = q["embedding"]
        rel   = q["relevant_ids"]

        if dry_run:
            print(f"  [{i+1}/{len(queries)}] query={q['text'][:50]!r} "
                  f"φ={phi_q:.3f} rel={len(rel)}")
            continue

        for variant in variants:
            t0 = time.perf_counter()

            if variant == "CIEL-FULL":
                ret = _rank_ciel_full(hm, phi_q, k=max(k, 5), delta=None)
            elif variant == "CIEL-PHASE-ONLY":
                ret = _rank_phase_only(corpus, phi_q, k=max(k, 5))
            elif variant == "CIEL-COSINE":
                ret = _rank_cosine(corpus_emb, emb_q, k=max(k, 5))
            else:
                ret = _rank_random(corpus, k=max(k, 5), rng=rng)

            elapsed_ms = (time.perf_counter() - t0) * 1000
            ret_ids = [r.get("memorise_id", "") for r in ret]

            results[variant]["p1"].append(_precision_at_k(ret_ids[:1], rel))
            results[variant]["p3"].append(_precision_at_k(ret_ids[:3], rel))
            results[variant]["p5"].append(_precision_at_k(ret_ids[:5], rel))
            results[variant]["mrr"].append(_reciprocal_rank(ret_ids, rel))
            results[variant]["resonance"].append(
                _phase_resonance(ret, phi_q, delta_natural))
            results[variant]["closure"].append(_mean_closure(ret))
            results[variant]["latency_ms"].append(elapsed_ms)

    if dry_run:
        return {}

    import numpy as np
    summary = {}
    for variant in variants:
        d = results[variant]
        lats = sorted(d["latency_ms"])
        n = len(lats)
        summary[variant] = {
            "precision_at_1":  round(float(np.mean(d["p1"])), 4),
            "precision_at_3":  round(float(np.mean(d["p3"])), 4),
            "precision_at_5":  round(float(np.mean(d["p5"])), 4),
            "mrr":             round(float(np.mean(d["mrr"])), 4),
            "phase_resonance": round(float(np.mean(d["resonance"])), 4),
            "mean_closure":    round(float(np.mean(d["closure"])), 4),
            "latency_p50_ms":  round(lats[n // 2], 2) if n else 0,
            "latency_p95_ms":  round(lats[int(n * 0.95)], 2) if n else 0,
            "n_queries":       n,
        }
    return summary


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--top-n", type=int, default=60,
                    help="Max queries to evaluate")
    args = ap.parse_args()

    import warnings
    warnings.filterwarnings("ignore")

    print("Loading CIEL modules…")
    enc_mod = _load("ciel_encoder_bench", "ciel_encoder.py")
    enc = enc_mod.get_encoder()
    print(f"  Encoder: {enc.model_name}")

    cal_mod = _load("ciel_calibration_bench", "ciel_calibration.py")
    cal = cal_mod.get_calibration()
    print(f"  Calibration: n={cal.n_entries} δ_nat={cal.delta_natural:.4f} "
          f"w_s={cal.w_semantic:.3f}")

    hm_mod = _load("holonomic_memory_bench", "holonomic_memory.py")
    hm = hm_mod.HolonomicMemory()

    conn = sqlite3.connect(str(_DB))

    print("Building query set…")
    queries, corpus = _build_query_set(enc, conn, top_n=args.top_n)
    print(f"  Queries with ground truth: {len(queries)}")
    print(f"  Corpus entries: {len(corpus)}")

    if args.dry_run:
        print("\n── DRY RUN — queries ──")
        _run_benchmark(queries, corpus, [], hm, cal, k=args.k, dry_run=True)
        conn.close()
        return

    # Pre-embed corpus for cosine variant (single batch pass, pure semantic)
    print("Pre-embedding corpus for CIEL-COSINE…")
    import numpy as np
    corpus_texts = [c["D_sense"] for c in corpus]
    t0 = time.time()
    corpus_vecs = enc._embed_batch(corpus_texts)
    print(f"  Embedded {len(corpus_texts)} entries in {time.time()-t0:.1f}s")
    corpus_emb = list(zip(corpus, [np.asarray(v) for v in corpus_vecs]))

    print(f"\nRunning benchmark ({len(queries)} queries, k={args.k})…")
    summary = _run_benchmark(queries, corpus, corpus_emb, hm, cal,
                             k=args.k, dry_run=False)

    # ── Print table ──────────────────────────────────────────────────────────
    print("\n── RESULTS ─────────────────────────────────────────────────────")
    header = f"{'Variant':<20} {'P@1':>6} {'P@3':>6} {'P@5':>6} {'MRR':>6} {'Resonance':>10} {'Closure':>8} {'p50ms':>7} {'p95ms':>7}"
    print(header)
    print("─" * len(header))
    for variant in ["CIEL-FULL", "CIEL-PHASE-ONLY", "CIEL-COSINE", "CIEL-RANDOM"]:
        d = summary[variant]
        print(f"{variant:<20} {d['precision_at_1']:>6.3f} {d['precision_at_3']:>6.3f} "
              f"{d['precision_at_5']:>6.3f} {d['mrr']:>6.3f} "
              f"{d['phase_resonance']:>10.3f} {d['mean_closure']:>8.3f} "
              f"{d['latency_p50_ms']:>7.1f} {d['latency_p95_ms']:>7.1f}")

    # ── Save JSON report ─────────────────────────────────────────────────────
    _REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    report_path = _REPORTS / f"ciel_benchmark_retrieval_{ts}.json"
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_queries": len(queries),
        "n_corpus": len(corpus),
        "k": args.k,
        "variants": summary,
        "calibration": cal.to_dict(),
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport saved → {report_path}")

    conn.close()


if __name__ == "__main__":
    main()
