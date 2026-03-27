from __future__ import annotations
from typing import Any

STABILIZATION_MESSAGES = [
    {"role": "user", "content": "Reply with exactly: READY-1"},
    {"role": "user", "content": "Reply with exactly: READY-2"},
]

def extract_text(response: dict[str, Any]) -> str:
    try:
        return response["choices"][0]["message"]["content"]
    except Exception:
        return "<unparsed>"


def run_three_prompt_session(runner, model: str, final_prompt: str, temperature: float = 0.0) -> dict[str, Any]:
    transcript: list[dict[str, str]] = [
        {
            "role": "system",
            "content": "You are a local GGUF test model. Follow the requested reply format exactly when possible.",
        }
    ]
    steps: list[dict[str, Any]] = []
    for msg in STABILIZATION_MESSAGES:
        transcript.append(msg)
        resp = runner.chat(model=model, messages=transcript, temperature=temperature, max_tokens=24)
        text = extract_text(resp)
        transcript.append({"role": "assistant", "content": text})
        steps.append({"prompt": msg["content"], "response": text, "raw": resp})
    final_msg = {"role": "user", "content": final_prompt}
    transcript.append(final_msg)
    final_resp = runner.chat(model=model, messages=transcript, temperature=temperature, max_tokens=96)
    final_text = extract_text(final_resp)
    transcript.append({"role": "assistant", "content": final_text})
    steps.append({"prompt": final_prompt, "response": final_text, "raw": final_resp})
    return {"transcript": transcript, "steps": steps, "final_text": final_text}


from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT / "systems" / "CIEL_OMEGA_COMPLETE_SYSTEM") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "systems" / "CIEL_OMEGA_COMPLETE_SYSTEM"))
from ciel_omega.orbital.global_pass import run_global_pass  # type: ignore

def orbital_precheck() -> dict:
    return run_global_pass().get("final", {})

def orbital_postcheck() -> dict:
    return run_global_pass().get("final", {})

def run_orbital_wrapped_chat(backend, model: str, messages: list[dict], temperature: float = 0.0, max_tokens: int = 128) -> dict:
    pre = orbital_precheck()
    response = backend.chat(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    post = orbital_postcheck()
    return {"pre": pre, "response": response, "post": post}
