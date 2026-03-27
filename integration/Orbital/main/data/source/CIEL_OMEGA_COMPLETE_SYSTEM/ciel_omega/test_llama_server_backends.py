from __future__ import annotations

from pathlib import Path

from ciel_omega.ciel.llama_server_backends import resolve_llama_server_path
from ciel_omega.ciel.llm_registry import build_gguf_primary_backend


def test_resolve_llama_server_path_finds_bundled_binary() -> None:
    path = resolve_llama_server_path()
    assert path is not None
    assert Path(path).is_file()


def test_build_gguf_primary_backend_uses_real_backend_or_stub_with_clear_reason() -> None:
    model_path = Path(__file__).resolve().parent / 'llm' / 'models' / 'qwen2.5-0.5b-instruct-q2_k.gguf'
    backend = build_gguf_primary_backend(model_path=str(model_path), n_ctx=512, n_threads=2, max_new_tokens=16)
    assert getattr(backend, 'name', '')
    # Either real backend via llama_cpp/server fallback or explicit stub.
    if backend.__class__.__name__.lower().startswith('stub'):
        reply = backend.generate_reply([{'role': 'user', 'content': 'hi'}], {'runtime_policy': {}})
        assert 'llama' in reply.lower() or 'gguf' in reply.lower()
    else:
        assert backend.__class__.__name__ in {'GGUFPrimaryBackend', 'LlamaServerPrimaryBackend'}
