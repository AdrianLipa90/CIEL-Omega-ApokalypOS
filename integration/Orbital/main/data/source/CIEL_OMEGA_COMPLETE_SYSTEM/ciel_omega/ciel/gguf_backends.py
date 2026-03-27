from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from .language_backend import AuxiliaryBackend, LanguageBackend
from .memory_prompt_context import summarize_sector_retrieval


_LLAMA_CACHE: Dict[Tuple[str, int, int, int], Any] = {}


def _coerce_role(role: str) -> str:
    key = (role or "").strip().lower()
    if key in {"system", "user", "assistant"}:
        return key
    return "user"


def _format_dialogue(dialogue: List[Dict[str, str]]) -> str:
    lines: List[str] = []
    for message in dialogue:
        role = _coerce_role(str(message.get("role", "user"))).capitalize()
        content = str(message.get("content", ""))
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


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


class GGUFPrimaryBackend(LanguageBackend):
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
        self.name = os.path.basename(model_path) if model_path else "gguf"
        self._llama: Any | None = None

    def _lazy_init(self) -> None:
        if self._llama is not None:
            return
        key = (self.model_path, self.n_ctx, self.n_threads, self.n_gpu_layers)
        cached = _LLAMA_CACHE.get(key)
        if cached is not None:
            self._llama = cached
            return

        from llama_cpp import Llama

        llama = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_threads=self.n_threads,
            n_gpu_layers=self.n_gpu_layers,
            verbose=False,
        )
        _LLAMA_CACHE[key] = llama
        self._llama = llama

    def generate_reply(self, dialogue: List[Dict[str, str]], ciel_state: Dict[str, Any]) -> str:
        self._lazy_init()
        state_json = _summarize_state(ciel_state)

        system = self.system_prompt.strip()
        if system:
            system = system + "\n\n"
        system += f"State: {state_json}"

        llama = self._llama
        if llama is None:
            return ""

        if hasattr(llama, "create_chat_completion"):
            messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
            for msg in dialogue:
                messages.append(
                    {
                        "role": _coerce_role(str(msg.get("role", "user"))),
                        "content": str(msg.get("content", "")),
                    }
                )
            out = llama.create_chat_completion(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_new_tokens,
            )
            return _extract_text(out).strip()

        prompt_parts = [system, _format_dialogue(dialogue), "Assistant:"]
        prompt = "\n".join(part for part in prompt_parts if part)
        out = llama(
            prompt,
            temperature=self.temperature,
            max_tokens=self.max_new_tokens,
            stop=["User:", "System:", "Assistant:"],
        )
        return _extract_text(out).strip()


class GGUFAuxBackend(AuxiliaryBackend):
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
        self.name = os.path.basename(model_path) if model_path else "gguf-aux"
        self._llama: Any | None = None

    def _lazy_init(self) -> None:
        if self._llama is not None:
            return
        key = (self.model_path, self.n_ctx, self.n_threads, self.n_gpu_layers)
        cached = _LLAMA_CACHE.get(key)
        if cached is not None:
            self._llama = cached
            return

        from llama_cpp import Llama

        llama = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_threads=self.n_threads,
            n_gpu_layers=self.n_gpu_layers,
            verbose=False,
        )
        _LLAMA_CACHE[key] = llama
        self._llama = llama

    def analyse_state(self, ciel_state: Dict[str, Any], candidate_reply: str) -> Dict[str, Any]:
        self._lazy_init()
        state_json = _summarize_state(ciel_state)

        prompt_parts = [
            self.system_prompt.strip(),
            "Evaluate the following reply for coherence and helpfulness given the state.",
            "Return JSON with keys coherence, helpfulness, keywords, emotion.",
            f"State: {state_json}",
            f"Reply: {candidate_reply}",
        ]
        prompt = "\n".join(part for part in prompt_parts if part)

        llama = self._llama
        if llama is None:
            return {"raw": ""}

        out = llama(
            prompt,
            temperature=self.temperature,
            max_tokens=self.max_new_tokens,
            stop=["User:", "System:", "Assistant:"],
        )
        text = _extract_text(out)
        return _parse_json_object(text)


__all__ = ["GGUFPrimaryBackend", "GGUFAuxBackend"]
