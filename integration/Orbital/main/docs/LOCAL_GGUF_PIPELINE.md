# Local GGUF pipeline (external model + bundled llama-server)

## Asset split

This workspace keeps the llama adapter bundled, but the GGUF model is external so the core repository stays lightweight.

- bundled adapter: `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/llm/adapters/llama_cpp/bin/llama-server`
- external model: provide your own `.gguf` path

## Resolution order

`build_default_bundle(backend="gguf")` resolves the model from:

1. `CIEL_GGUF_LITE_MODEL_PATH`, `CIEL_GGUF_STANDARD_MODEL_PATH`, `CIEL_GGUF_SCIENCE_MODEL_PATH`
2. `CIEL_GGUF_MODEL_PATH` or `CIEL_GGUF_MODEL`
3. `CIEL_GGUF_MODELS_DIR`
4. local `llm/models/` directories if the operator puts a model there

## Example run

```bash
python data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/scripts/run_local_gguf_pipeline.py \
  --model-path /absolute/path/to/model.gguf \
  "Describe your current coherence state in one short paragraph." \
  --profile lite --threads 4 --ctx 1024
```

## Notes

- the fallback launches a local HTTP server on `127.0.0.1` using an ephemeral port
- server processes are cached per `(model, ctx, threads, gpu layers)` tuple and stopped at interpreter exit
- if no external model path is supplied, the GGUF backend degrades to an explicit stub instead of failing silently
