#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    state_path = repo_root / 'integration' / 'imports' / 'audio_orbital_stack' / 'state' / 'audio_orbital_stack_state.json'
    if not state_path.exists():
        print(json.dumps({"ready": False, "reason": "bootstrap not yet run"}, indent=2))
        return 1
    state = json.loads(state_path.read_text(encoding='utf-8'))
    ready = {
        "vad": state["archives"].get("silero_vad", {}).get("extracted", False),
        "stt_primary": state["archives"].get("whisper_cpp", {}).get("extracted", False),
        "tts": state["archives"].get("piper", {}).get("extracted", False),
        "stt_alt": state["archives"].get("faster_whisper", {}).get("extracted", False),
        "whisper_model": state["models"].get("whisper_model", {}).get("present", False),
        "piper_voice_model": state["models"].get("piper_voice_model", {}).get("present", False),
        "piper_voice_config": state["models"].get("piper_voice_config", {}).get("present", False),
    }
    summary = {
        "schema": "ciel/audio-orbital-probe/v0.1",
        "ready": all([ready["vad"], ready["stt_primary"], ready["tts"]]),
        "components": ready,
        "advice": {
            "minimum": "silero_vad + whisper_cpp + piper extracted",
            "full_voice": "add whisper_model + piper_voice_model + piper_voice_config"
        }
    }
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
