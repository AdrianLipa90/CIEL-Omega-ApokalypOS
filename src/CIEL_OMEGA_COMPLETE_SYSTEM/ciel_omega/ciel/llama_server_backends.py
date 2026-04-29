from __future__ import annotations

import atexit
import json
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .language_backend import AuxiliaryBackend, LanguageBackend
from .memory_prompt_context import summarize_sector_retrieval

_SERVER_CACHE: Dict[Tuple[str, str, int, int, int], "_ServerHandle"] = {}


def _coerce_role(role: str) -> str:
    key = (role or "").strip().lower()
    if key in {"system", "user", "assistant"}:
        return key
    return "user"


def _mean_or_none(values: Any) -> Optional[float]:
    if not isinstance(values, list) or not values:
        return None
    nums = [float(v) for v in values if isinstance(v, (int, float))]
    if not nums:
        return None
    return sum(nums) / len(nums)


def _summarize_state(ciel_state: Dict[str, Any]) -> str:
    simulation = ciel_state.get("simulation") if isinstance(ciel_state.get("simulation"), dict) else {}
    orbital = ciel_state.get("orbital") if isinstance(ciel_state.get("orbital"), dict) else {}
    control = orbital.get("control") if isinstance(orbital.get("control"), dict) else {}
    runtime_policy = ciel_state.get("runtime_policy") if isinstance(ciel_state.get("runtime_policy"), dict) else {}
    tmp_outcome = ciel_state.get("tmp_outcome") if isinstance(ciel_state.get("tmp_outcome"), dict) else {}

    summary = {
        "intention_preview": list(ciel_state.get("intention_vector", [])[:4]) if isinstance(ciel_state.get("intention_vector"), list) else None,
        "simulation_coherence_mean": _mean_or_none(simulation.get("coherence")),
        "dominant_emotion": ciel_state.get("dominant_emotion"),
        "mood": ciel_state.get("mood"),
        "soul_invariant": ciel_state.get("soul_invariant"),
        "ethical_score": ciel_state.get("ethical_score"),
        "orbital_mode": control.get("mode"),
        "orbital_severity": control.get("severity"),
        "orbital_R_H": orbital.get("R_H"),
        "orbital_T_glob": orbital.get("T_glob"),
        "runtime_strategy": runtime_policy.get("response_strategy"),
        "durable_write_allowed": runtime_policy.get("durable_write_allowed"),
        "tmp_gate": tmp_outcome.get("bifurcation"),
        "memorised": ciel_state.get("memorised"),
        "memory_governor": ciel_state.get("memory_governor"),
        "sector_memory_retrieval": summarize_sector_retrieval(ciel_state),
    }
    return json.dumps(summary, ensure_ascii=False)



def _extract_text(output: Any) -> str:
    if isinstance(output, dict):
        choices = output.get("choices") or []
        if choices:
            choice0 = choices[0] or {}
            message = choice0.get("message") or {}
            if isinstance(message, dict) and message.get("content") is not None:
                return str(message.get("content"))
            if choice0.get("text") is not None:
                return str(choice0.get("text"))
        if output.get("text") is not None:
            return str(output.get("text"))
    return str(output)


def _parse_json_object(text: str) -> Dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            return {"raw": text.strip()}
    return {"raw": text.strip()}


def _candidate_server_paths() -> List[Path]:
    candidates: List[Path] = []
    env = os.getenv("CIEL_LLAMA_SERVER_PATH")
    if env:
        candidates.append(Path(env))
    here = Path(__file__).resolve().parent.parent
    candidates.extend([
        here / "llm" / "adapters" / "llama_cpp" / "bin" / "llama-server",
        Path.cwd() / "llama-server",
        Path.cwd() / "build" / "bin" / "llama-server",
    ])
    out: List[Path] = []
    seen: set[str] = set()
    for path in candidates:
        if not path.is_file():
            continue
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def resolve_llama_server_path() -> Optional[str]:
    for path in _candidate_server_paths():
        return str(path)
    return None


def _pick_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _http_json(url: str, payload: Optional[Dict[str, Any]] = None, timeout: float = 30.0) -> Dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    if not body.strip():
        return {}
    return json.loads(body)


@dataclass
class _ServerHandle:
    process: subprocess.Popen[str]
    base_url: str
    model_path: str
    server_path: str
    port: int

    def stop(self) -> None:
        proc = self.process
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


def _stop_all_servers() -> None:
    for handle in list(_SERVER_CACHE.values()):
        try:
            handle.stop()
        except Exception:
            pass


atexit.register(_stop_all_servers)


def _ensure_server(*, model_path: str, n_ctx: int, n_threads: int, n_gpu_layers: int = 0) -> _ServerHandle:
    server_path = resolve_llama_server_path()
    if not server_path:
        raise FileNotFoundError("llama-server executable not found")
    key = (server_path, str(Path(model_path).resolve()), int(n_ctx), int(n_threads), int(n_gpu_layers))
    cached = _SERVER_CACHE.get(key)
    if cached is not None and cached.process.poll() is None:
        return cached

    port = _pick_port()
    base_url = f"http://127.0.0.1:{port}"
    cmd = [
        server_path,
        "-m", model_path,
        "--host", "127.0.0.1",
        "--port", str(port),
        "-c", str(int(n_ctx)),
        "-t", str(int(n_threads)),
        "--jinja",
    ]
    if int(n_gpu_layers) > 0:
        cmd.extend(["--n-gpu-layers", str(int(n_gpu_layers))])

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    handle = _ServerHandle(
        process=proc,
        base_url=base_url,
        model_path=model_path,
        server_path=server_path,
        port=port,
    )

    deadline = time.time() + 90.0
    last_error: Optional[Exception] = None
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"llama-server exited early with code {proc.returncode}")
        try:
            _http_json(base_url + "/health", timeout=2.0)
            _SERVER_CACHE[key] = handle
            return handle
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1.0)

    handle.stop()
    raise RuntimeError(f"llama-server did not become healthy: {last_error}")


class LlamaServerPrimaryBackend(LanguageBackend):
    def __init__(
        self,
        *,
        model_path: str,
        n_ctx: int = 2048,
        n_threads: int = 4,
        n_gpu_layers: int = 0,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        system_prompt: str = "",
    ) -> None:
        self.model_path = model_path
        self.n_ctx = int(n_ctx)
        self.n_threads = int(n_threads)
        self.n_gpu_layers = int(n_gpu_layers)
        self.max_new_tokens = int(max_new_tokens)
        self.temperature = float(temperature)
        self.system_prompt = system_prompt
        self.name = os.path.basename(model_path) if model_path else "llama-server-gguf"
        self._server: Optional[_ServerHandle] = None

    def _lazy_init(self) -> None:
        if self._server is None:
            self._server = _ensure_server(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
            )

    def generate_reply(self, dialogue: List[Dict[str, str]], ciel_state: Dict[str, Any]) -> str:
        self._lazy_init()
        assert self._server is not None
        state_json = _summarize_state(ciel_state)
        system = self.system_prompt.strip()
        if system:
            system = system + "\n\n"
        system += f"State: {state_json}"
        messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
        for msg in dialogue:
            messages.append({
                "role": _coerce_role(str(msg.get("role", "user"))),
                "content": str(msg.get("content", "")),
            })
        payload = {
            "model": os.path.basename(self.model_path),
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_new_tokens,
        }
        out = _http_json(self._server.base_url + "/v1/chat/completions", payload=payload, timeout=180.0)
        return _extract_text(out).strip()


class LlamaServerAuxBackend(AuxiliaryBackend):
    def __init__(
        self,
        *,
        model_path: str,
        n_ctx: int = 2048,
        n_threads: int = 4,
        n_gpu_layers: int = 0,
        max_new_tokens: int = 128,
        temperature: float = 0.2,
        system_prompt: str = "",
    ) -> None:
        self.model_path = model_path
        self.n_ctx = int(n_ctx)
        self.n_threads = int(n_threads)
        self.n_gpu_layers = int(n_gpu_layers)
        self.max_new_tokens = int(max_new_tokens)
        self.temperature = float(temperature)
        self.system_prompt = system_prompt
        self.name = os.path.basename(model_path) if model_path else "llama-server-gguf-aux"
        self._server: Optional[_ServerHandle] = None

    def _lazy_init(self) -> None:
        if self._server is None:
            self._server = _ensure_server(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=self.n_gpu_layers,
            )

    def analyse_state(self, ciel_state: Dict[str, Any], candidate_reply: str) -> Dict[str, Any]:
        self._lazy_init()
        assert self._server is not None
        state_json = _summarize_state(ciel_state)
        system = self.system_prompt.strip()
        if system:
            system = system + "\n\n"
        system += "Return strict JSON with keys coherence, helpfulness, keywords, emotion."
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"State: {state_json}\nReply: {candidate_reply}"},
        ]
        payload = {
            "model": os.path.basename(self.model_path),
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_new_tokens,
        }
        out = _http_json(self._server.base_url + "/v1/chat/completions", payload=payload, timeout=180.0)
        return _parse_json_object(_extract_text(out))


__all__ = [
    "LlamaServerPrimaryBackend",
    "LlamaServerAuxBackend",
    "resolve_llama_server_path",
]
