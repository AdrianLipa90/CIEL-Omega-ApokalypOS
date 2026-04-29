# Audio Orbital Stack

This import sector assembles the local speech skeleton around **Omega** and **Orbital** without forcing large vendor payloads into the canonical tree.

## Active path
`audio -> VAD -> STT -> normalization -> sapiens packet -> omega/orbital -> response -> TTS`

## What is placed here
- `vendor/whisper.cpp` — primary local STT engine
- `vendor/silero-vad` — speech gate / turn detector
- `vendor/piper` — primary local TTS engine
- `vendor/faster-whisper` — optional Python STT alternative
- `models/` — optional downloaded model assets
- `state/audio_orbital_stack_state.json` — last assembled local state
- `active_pipeline_semantics.json|csv` — semantic values for active files
- `assets_audio_stack.json` — source/drop manifest with auto-download fallback

## Entrypoints
- `scripts/bootstrap_audio_orbital_stack.py`
- `scripts/run_audio_orbital_probe.py`
- `scripts/snapshot_audio_orbital_stack.sh`

## Auto-download sources / citations
The bootstrap script first checks local drop locations, then uses the configured upstream archive URL when a local archive is missing.

### Code archives fetched automatically when missing
- `whisper.cpp`  
  Source citation: <https://github.com/ggml-org/whisper.cpp/archive/refs/heads/master.zip>
- `faster-whisper`  
  Source citation: <https://github.com/SYSTRAN/faster-whisper/archive/refs/heads/master.zip>
- `silero-vad`  
  Source citation: <https://github.com/snakers4/silero-vad/archive/refs/heads/master.zip>
- `piper`  
  Source citation: <https://github.com/rhasspy/piper/archive/refs/heads/master.zip>
- `piper-samples` *(optional; not extracted by default)*  
  Source citation: <https://github.com/rhasspy/piper-samples/archive/refs/heads/master.zip>

### Optional model payloads
The manifest reserves optional model slots, but they are **not** auto-downloaded until a concrete `source_url` is written into `assets_audio_stack.json`.
- `models/whisper/ggml-base.bin` — whisper.cpp model slot
- `models/piper/en_US-lessac-medium.onnx` — Piper voice model slot
- `models/piper/en_US-lessac-medium.onnx.json` — Piper voice config slot

## Nonlocal / hyperspace intent
This stack is catalogued as an Orbital import so Omega is no longer isolated from immediate audio binding. The import is kept auditable and optional:
- code archives may be auto-fetched when missing
- heavy model files remain external until explicitly configured
- semantic roles are explicit, not implicit
