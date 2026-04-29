# Bundled local LLM assets

Bundled in this workspace:

- adapter: `adapters/llama_cpp/bin/llama-server`

External by design (not bundled into the lightweight core):

- GGUF model file, supplied by the operator via environment path or CLI flag

Recommended environment variables:

- `CIEL_GGUF_MODEL_PATH`
- `CIEL_GGUF_LITE_MODEL_PATH`
- `CIEL_GGUF_STANDARD_MODEL_PATH`
- `CIEL_GGUF_SCIENCE_MODEL_PATH`
- `CIEL_GGUF_MODELS_DIR`
