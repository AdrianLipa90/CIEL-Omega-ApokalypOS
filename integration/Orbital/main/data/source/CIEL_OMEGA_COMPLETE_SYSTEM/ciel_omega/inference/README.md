# inference

Local GGUF inference integration layer.

Current purpose:
- start or attach to a local `llama-server`
- expose a minimal OpenAI-compatible client
- support orbital pre/post diagnostics around inference
- run a 3-prompt stabilization conversation before the main prompt
