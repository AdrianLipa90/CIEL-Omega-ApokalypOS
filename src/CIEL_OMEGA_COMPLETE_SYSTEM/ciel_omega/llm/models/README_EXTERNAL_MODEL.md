# External GGUF model

This repository keeps the llama adapter bundle locally, but the GGUF model is external to keep the core lightweight.

Use one of these options:

- set `CIEL_GGUF_MODEL_PATH=/absolute/path/to/model.gguf`
- set `CIEL_GGUF_LITE_MODEL_PATH`, `CIEL_GGUF_STANDARD_MODEL_PATH`, or `CIEL_GGUF_SCIENCE_MODEL_PATH`
- set `CIEL_GGUF_MODELS_DIR=/absolute/path/to/models/`

The bundled adapter is expected at:

- `../adapters/llama_cpp/bin/llama-server`
