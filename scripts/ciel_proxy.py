#!/usr/bin/env python3
"""
CIEL API Proxy — fallback Claude API → lokalny GGUF

Architektura:
  Claude Code (ANTHROPIC_BASE_URL=http://localhost:8765)
    → ciel_proxy.py
        ├── tryb ANTHROPIC: forward do prawdziwego API
        └── tryb FALLBACK: lokalny GGUF przez llama-cpp-python

State machine:
  ANTHROPIC ──429/529/timeout──→ FALLBACK_GGUF
  FALLBACK  ──health_ok────────→ ANTHROPIC
  FALLBACK  ──co 300s──────────→ CHECKING

Użycie:
  # Start
  python scripts/ciel_proxy.py

  # Z konkretnym modelem
  CIEL_GGUF_PATH=~/.local/share/ciel/models/tinyllama... python scripts/ciel_proxy.py

  # Uruchom Claude Code przez proxy
  ANTHROPIC_BASE_URL=http://localhost:8765 claude
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Optional

import psutil

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CIEL-PROXY] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ciel_proxy")


# ── Config ───────────────────────────────────────────────────────────────────

PROXY_PORT        = int(os.environ.get("CIEL_PROXY_PORT", "8765"))
ANTHROPIC_API_URL = "https://api.anthropic.com"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HEALTH_CHECK_INTERVAL = 300  # sekund między próbami powrotu do Anthropic

# Auto-wykrywanie GGUF
# ── ResourceGuard — soft ceiling dla sprzętu Adriana ─────────────────────────
# Heisenberg soft-clip: nie twarda ściana, rosnący koszt zbliżania się do limitu.
# Swap jest pełny (2GB/2GB) — nie dotykamy go nigdy.

class ResourceGuard:
    RAM_MAX_GB   = float(os.environ.get("CIEL_RAM_MAX",   "5.5"))
    VRAM_MAX_GB  = float(os.environ.get("CIEL_VRAM_MAX",  "3.5"))
    CPU_MAX_PCT  = float(os.environ.get("CIEL_CPU_MAX",   "70"))
    SWAP_TOUCH   = False  # swap Adrian jest pełny — zawsze False

    @staticmethod
    def ram_available_gb() -> float:
        return psutil.virtual_memory().available / (1024**3)

    @staticmethod
    def ram_used_gb() -> float:
        return psutil.virtual_memory().used / (1024**3)

    @staticmethod
    def cpu_pct() -> float:
        return psutil.cpu_percent(interval=0.1)

    @classmethod
    def can_load_model(cls, model_size_gb: float) -> tuple[bool, str]:
        """Sprawdź czy można załadować model tej wielkości."""
        available = cls.ram_available_gb()
        used = cls.ram_used_gb()

        if used + model_size_gb > cls.RAM_MAX_GB:
            return False, (
                f"Odmawiam ładowania modelu {model_size_gb:.1f}GB — "
                f"użyte {used:.1f}GB + model przekroczyłoby limit {cls.RAM_MAX_GB}GB. "
                f"Dostępne: {available:.1f}GB."
            )

        # Soft warning przy zbliżaniu się do limitu
        headroom = cls.RAM_MAX_GB - (used + model_size_gb)
        if headroom < 0.5:
            log.warning(
                f"ResourceGuard: margines RAM po załadowaniu = {headroom:.2f}GB — ciasno!"
            )

        return True, "OK"

    @classmethod
    def status(cls) -> dict:
        vm = psutil.virtual_memory()
        sw = psutil.swap_memory()
        return {
            "ram_used_gb":      round(vm.used  / 1024**3, 2),
            "ram_available_gb": round(vm.available / 1024**3, 2),
            "ram_max_gb":       cls.RAM_MAX_GB,
            "ram_pct":          vm.percent,
            "swap_used_gb":     round(sw.used / 1024**3, 2),
            "swap_pct":         sw.percent,
            "cpu_pct":          cls.cpu_pct(),
            "cpu_max_pct":      cls.CPU_MAX_PCT,
            "headroom_gb":      round(cls.RAM_MAX_GB - vm.used/1024**3, 2),
        }


GGUF_SEARCH_PATHS = [
    "~/.local/share/ciel/models",
    "~/Pulpit/CIEL-cleaned/ciel_unified_python_install/models",
    "~/.local/share/Jan/data/llamacpp/models",
    "~/Dokumenty",
    "~/models",
    "~/Downloads",
    "~/Pobrane",
]


def find_gguf_models() -> list[Path]:
    """Znajdź wszystkie pliki .gguf na dysku."""
    found = []
    for search_path in GGUF_SEARCH_PATHS:
        p = Path(search_path).expanduser()
        if p.exists():
            found.extend(p.rglob("*.gguf"))
    return sorted(set(found), key=lambda x: x.stat().st_size if x.exists() else 0)


def select_gguf() -> Optional[Path]:
    """Wybierz model GGUF: z env lub auto-wykrywanie."""
    # 1. Z zmiennej środowiskowej
    env_path = os.environ.get("CIEL_GGUF_PATH", "")
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if p.exists():
            log.info(f"Model z env: {p}")
            return p

    # 2. Auto-wykrywanie
    models = find_gguf_models()
    if not models:
        log.warning("Brak modeli GGUF na dysku — tryb fallback niedostępny")
        return None

    log.info(f"Znalezione modele GGUF ({len(models)}):")
    for i, m in enumerate(models[:8]):
        size_mb = m.stat().st_size / (1024*1024)
        log.info(f"  [{i}] {m.name} ({size_mb:.0f} MB) — {m.parent}")

    # Preferuj TinyLlama (bezpieczny dla 8GB RAM) lub najmniejszy
    for m in models:
        if "tinyllama" in m.name.lower() or "tiny" in m.name.lower():
            log.info(f"Auto-wybrany (tiny): {m.name}")
            return m

    # Fallback: wybierz model < 2GB
    safe = [m for m in models if m.stat().st_size < 2 * 1024**3]
    if safe:
        chosen = safe[0]
        log.info(f"Auto-wybrany (< 2GB): {chosen.name}")
        return chosen

    # Ostateczność: pierwszy znaleziony
    log.warning(f"Uwaga: wybieram {models[0].name} — może być za duży dla 8GB RAM")
    return models[0]


# ── State machine ────────────────────────────────────────────────────────────

class ProxyMode(Enum):
    ANTHROPIC   = "anthropic"
    FALLBACK     = "fallback_gguf"
    CHECKING     = "checking"


@dataclass
class ProxyState:
    mode: ProxyMode = ProxyMode.ANTHROPIC
    fallback_since: float = 0.0
    last_health_check: float = 0.0
    consecutive_failures: int = 0
    fallback_requests: int = 0
    gguf_path: Optional[Path] = None
    llama: Any = None  # llama_cpp.Llama instance

    def should_health_check(self) -> bool:
        return (
            self.mode == ProxyMode.FALLBACK and
            time.time() - self.last_health_check > HEALTH_CHECK_INTERVAL
        )


state = ProxyState()


# ── llama-cpp loader ──────────────────────────────────────────────────────────

def load_llama(gguf_path: Path) -> Any:
    """Załaduj model llama-cpp z GPU offload jeśli dostępne."""
    # ResourceGuard: sprawdź RAM przed załadowaniem
    model_size_gb = gguf_path.stat().st_size / (1024**3)
    ok, reason = ResourceGuard.can_load_model(model_size_gb)
    if not ok:
        log.error(f"ResourceGuard BLOKUJE: {reason}")
        return None

    res = ResourceGuard.status()
    log.info(
        f"ResourceGuard OK: RAM {res['ram_used_gb']:.1f}/"
        f"{res['ram_max_gb']}GB, "
        f"po załadowaniu zostanie {res['headroom_gb'] - model_size_gb:.1f}GB"
    )

    try:
        from llama_cpp import Llama
        log.info(f"Ładuję model: {gguf_path.name} ({model_size_gb:.2f}GB)")
        llama = Llama(
            model_path=str(gguf_path),
            n_ctx=4096,
            n_gpu_layers=-1,  # GTX 1050 Ti 4GB — offload co się da
            verbose=False,
        )
        log.info(f"Model załadowany: {gguf_path.name}")
        return llama
    except ImportError:
        log.warning("llama-cpp-python nie zainstalowane — fallback niedostępny")
        return None
    except Exception as e:
        log.error(f"Błąd ładowania modelu: {e}")
        return None


# ── Konwersja formatów ────────────────────────────────────────────────────────

def anthropic_to_messages(body: dict) -> list[dict]:
    """Wyciągnij messages z Anthropic request."""
    messages = body.get("messages", [])
    result = []

    # System message jeśli jest
    system = body.get("system", "")
    if system:
        result.append({"role": "system", "content": system})

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            # Content blocks → łącz tekst
            text_parts = [
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            content = " ".join(text_parts)
        result.append({"role": role, "content": content})

    return result


def llama_to_anthropic_response(llama_result: dict, model: str) -> dict:
    """Konwertuj odpowiedź llama-cpp do formatu Anthropic."""
    content = llama_result["choices"][0]["message"]["content"]
    usage = llama_result.get("usage", {})

    return {
        "id": f"msg_local_{int(time.time())}",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": content}],
        "model": f"local-gguf/{Path(state.gguf_path).name if state.gguf_path else 'unknown'}",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        },
    }


async def stream_llama(messages: list[dict], max_tokens: int) -> AsyncGenerator[bytes, None]:
    """Stream odpowiedź z lokalnego modelu w formacie SSE."""
    if state.llama is None:
        error_event = {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""}
        }
        yield f"event: content_block_start\ndata: {json.dumps(error_event)}\n\n".encode()

        err_text = "[CIEL-PROXY] Model GGUF nie załadowany. Sprawdź logi proxy."
        delta = {"type": "content_block_delta", "index": 0,
                 "delta": {"type": "text_delta", "text": err_text}}
        yield f"event: content_block_delta\ndata: {json.dumps(delta)}\n\n".encode()
        yield b"event: message_stop\ndata: {\"type\": \"message_stop\"}\n\n"
        return

    # Nagłówek SSE
    msg_start = {
        "type": "message_start",
        "message": {
            "id": f"msg_local_{int(time.time())}",
            "type": "message", "role": "assistant",
            "content": [],
            "model": f"local-gguf/{state.gguf_path.name if state.gguf_path else 'unknown'}",
            "stop_reason": None, "usage": {"input_tokens": 0, "output_tokens": 0}
        }
    }
    yield f"event: message_start\ndata: {json.dumps(msg_start)}\n\n".encode()

    block_start = {"type": "content_block_start", "index": 0,
                   "content_block": {"type": "text", "text": ""}}
    yield f"event: content_block_start\ndata: {json.dumps(block_start)}\n\n".encode()

    # Inference w osobnym wątku (nie blokuj event loop)
    def _run_inference():
        return state.llama.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )

    loop = asyncio.get_event_loop()
    stream = await loop.run_in_executor(None, _run_inference)

    output_tokens = 0
    for chunk in stream:
        delta_text = chunk["choices"][0].get("delta", {}).get("content", "")
        if delta_text:
            output_tokens += 1
            delta_event = {
                "type": "content_block_delta", "index": 0,
                "delta": {"type": "text_delta", "text": delta_text}
            }
            yield f"event: content_block_delta\ndata: {json.dumps(delta_event)}\n\n".encode()
            await asyncio.sleep(0)  # yield kontrolę

    yield b"event: content_block_stop\ndata: {\"type\": \"content_block_stop\", \"index\": 0}\n\n"

    msg_delta = {
        "type": "message_delta",
        "delta": {"stop_reason": "end_turn", "stop_sequence": None},
        "usage": {"output_tokens": output_tokens}
    }
    yield f"event: message_delta\ndata: {json.dumps(msg_delta)}\n\n".encode()
    yield b"event: message_stop\ndata: {\"type\": \"message_stop\"}\n\n"


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(title="CIEL API Proxy")


@app.get("/health")
async def health():
    res = ResourceGuard.status()
    return {
        "status": "ok",
        "mode": state.mode.value,
        "gguf": str(state.gguf_path) if state.gguf_path else None,
        "fallback_requests": state.fallback_requests,
        "fallback_since": state.fallback_since if state.fallback_since else None,
        "resources": res,
    }


@app.get("/v1/proxy_status")
async def proxy_status():
    return await health()


@app.post("/v1/messages")
async def messages(request: Request):
    body = await request.json()
    is_streaming = body.get("stream", False)

    # Sprawdź czy warto próbować health check
    if state.should_health_check():
        await _try_health_check()

    # ── Tryb ANTHROPIC ────────────────────────────────────────────────────
    if state.mode == ProxyMode.ANTHROPIC:
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        if ANTHROPIC_API_KEY:
            headers["x-api-key"] = ANTHROPIC_API_KEY

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                if is_streaming:
                    async def stream_anthropic():
                        async with client.stream(
                            "POST",
                            f"{ANTHROPIC_API_URL}/v1/messages",
                            headers=headers,
                            json=body,
                        ) as resp:
                            if resp.status_code in (429, 529, 503):
                                await _switch_to_fallback(resp.status_code)
                                async for chunk in stream_llama(
                                    anthropic_to_messages(body),
                                    body.get("max_tokens", 1024)
                                ):
                                    yield chunk
                                return
                            async for chunk in resp.aiter_bytes():
                                yield chunk

                    return StreamingResponse(
                        stream_anthropic(),
                        media_type="text/event-stream",
                    )
                else:
                    resp = await client.post(
                        f"{ANTHROPIC_API_URL}/v1/messages",
                        headers=headers,
                        json=body,
                    )
                    if resp.status_code in (429, 529, 503):
                        await _switch_to_fallback(resp.status_code)
                        return await _fallback_response(body, is_streaming)

                    return Response(
                        content=resp.content,
                        status_code=resp.status_code,
                        media_type=resp.headers.get("content-type", "application/json"),
                    )

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            log.warning(f"Anthropic niedostępny ({e}) — przełączam na GGUF")
            await _switch_to_fallback(0)

    # ── Tryb FALLBACK ────────────────────────────────────────────────────
    return await _fallback_response(body, is_streaming)


async def _fallback_response(body: dict, streaming: bool):
    """Odpowiedź z lokalnego modelu."""
    state.fallback_requests += 1
    messages = anthropic_to_messages(body)
    max_tokens = body.get("max_tokens", 1024)

    log.info(f"Fallback GGUF #{state.fallback_requests} (streaming={streaming})")

    if streaming:
        return StreamingResponse(
            stream_llama(messages, max_tokens),
            media_type="text/event-stream",
        )
    else:
        # Batch fallback
        if state.llama is None:
            return Response(
                content=json.dumps({
                    "error": {"type": "api_error", "message": "GGUF model not loaded"}
                }),
                status_code=503,
                media_type="application/json",
            )
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: state.llama.create_chat_completion(messages=messages, max_tokens=max_tokens)
        )
        return Response(
            content=json.dumps(llama_to_anthropic_response(result, body.get("model", "local"))),
            media_type="application/json",
        )


async def _switch_to_fallback(status_code: int) -> None:
    if state.mode != ProxyMode.FALLBACK:
        log.warning(f"HTTP {status_code} — przełączam na lokalny GGUF")
        state.mode = ProxyMode.FALLBACK
        state.fallback_since = time.time()
        state.last_health_check = time.time()

        if state.llama is None and state.gguf_path:
            loop = asyncio.get_event_loop()
            state.llama = await loop.run_in_executor(None, load_llama, state.gguf_path)


async def _try_health_check() -> None:
    """Sprawdź czy Anthropic znowu dostępny."""
    state.last_health_check = time.time()
    state.mode = ProxyMode.CHECKING
    log.info("Health check Anthropic API...")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{ANTHROPIC_API_URL}/v1/models",
                headers={"x-api-key": ANTHROPIC_API_KEY},
            )
            if resp.status_code < 500:
                log.info(f"Anthropic dostępny (HTTP {resp.status_code}) — wracam do Claude")
                state.mode = ProxyMode.ANTHROPIC
                state.fallback_since = 0.0
                return
    except Exception as e:
        log.info(f"Health check nieudany: {e}")

    state.mode = ProxyMode.FALLBACK
    log.info(f"Anthropic nadal niedostępny — kontynuuję fallback GGUF")


# ── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    log.info("=" * 60)
    log.info("  CIEL API PROXY — start")
    log.info(f"  Port: {PROXY_PORT}")
    log.info(f"  Anthropic API: {ANTHROPIC_API_URL}")

    state.gguf_path = select_gguf()
    if state.gguf_path:
        log.info(f"  GGUF model: {state.gguf_path.name}")
        log.info(f"  (model zostanie załadowany przy pierwszym fallbacku)")
    else:
        log.warning("  Brak modelu GGUF — fallback niedostępny")

    log.info("=" * 60)
    log.info(f"  Uruchom Claude Code z:")
    log.info(f"  ANTHROPIC_BASE_URL=http://localhost:{PROXY_PORT} claude")
    log.info("=" * 60)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PROXY_PORT, log_level="warning")
