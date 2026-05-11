from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / 'src' / 'CIEL_OMEGA_COMPLETE_SYSTEM'
if str(PKG) not in sys.path:
    sys.path.insert(0, str(PKG))

from ciel_omega.ciel.memory_prompt_context import build_semantic_speech_context
from ciel_omega.ciel.gguf_backends import _summarize_state as gguf_summarize_state
from ciel_omega.ciel.llama_server_backends import _summarize_state as llama_summarize_state


FAKE_STATE = {
    "sector_memory": {
        "governed_retrieval": {
            "ranked": [
                {
                    "channel": "m3",
                    "text": "semantic retrieval prefers repeated meaning",
                    "holonomy_quality": 0.88,
                    "phase_alignment": 0.91,
                },
                {
                    "channel": "m8",
                    "text": "audit trail keeps the history intact",
                    "holonomy_quality": 0.81,
                    "phase_alignment": 0.73,
                },
            ],
            "by_channel": {
                "m3": [
                    {"text": "semantic retrieval prefers repeated meaning"},
                ]
            },
        }
    },
    "semantic_labels": ["memory", "retrieval", "speech"],
    "memory_score": 0.73,
    "nonlocal_runtime": {"semantic_key": "memory bridge", "coherent_fraction": 0.84},
    "euler_bridge": {"memory_semantic_key": "memory bridge"},
    "runtime_policy": {"response_strategy": "truth-aligned-user-intent", "durable_write_allowed": True},
    "lingo_frame": {
        "summary": "CIELingo|concepts=bridge, memory|operators=through|deictic=Now:relative_anchor|unresolved=Now|factual=no|noema_conf=0.710",
        "concept_tokens": ["bridge", "memory"],
        "operator_tokens": ["through"],
        "unresolved": ["Now"],
        "deictic_frame": {
            "anchors": [],
            "relative_anchors": [
                {"operator": "Now", "surface": "now", "resolution_state": "relative_anchor"}
            ],
        },
        "noema_route": {"confidence": 0.71, "factual_validation_required": False},
        "phase_projection": {"target_phase": 0.0, "target_phase_shift": 0.0, "phase_confidence": 0.66},
        "tau_bridge": {
            "tau_gradient_mean": 0.12,
            "imaginal_drive": 0.44,
            "tau_curvature_rms": 0.08,
        },
    },
    "intention_vector": [0.1, 0.2, 0.3],
    "simulation": {"coherence": [0.8, 0.9]},
    "cognition": {"phase": 0.2},
    "affect": {"tone": "calm"},
}


def test_build_semantic_speech_context_exposes_memory_as_text():
    ctx = build_semantic_speech_context(FAKE_STATE, max_items_per_channel=2)
    assert "semantic retrieval prefers repeated meaning" in ctx["text"]
    assert "audit trail keeps the history intact" in ctx["text"]
    assert "Semantic labels: memory, retrieval, speech" in ctx["text"]
    assert "Memory score: 0.730" in ctx["text"]
    assert "CIELingo summary:" in ctx["text"]
    assert "CIELingo concepts: bridge, memory" in ctx["text"]
    assert "CIELingo deictics: Now:relative_anchor" in ctx["text"]
    assert "CIELingo phase target:" in ctx["text"]
    assert "CIELingo tau gradient:" in ctx["text"]
    assert "CIELingo imaginal drive:" in ctx["text"]
    assert "Runtime policy: truth-aligned-user-intent" in ctx["text"]
    assert ctx["retrieval"]["ranked"]


def test_backends_summaries_embed_semantic_speech_bridge():
    gguf_state = json.loads(gguf_summarize_state(FAKE_STATE))
    assert "semantic_speech" in gguf_state
    assert "Retrieved semantic memory:" in gguf_state["semantic_speech"]["text"]

    llama_state = json.loads(llama_summarize_state(FAKE_STATE))
    assert "semantic_speech" in llama_state
    assert "memory bridge" in llama_state["semantic_speech"]["text"]
