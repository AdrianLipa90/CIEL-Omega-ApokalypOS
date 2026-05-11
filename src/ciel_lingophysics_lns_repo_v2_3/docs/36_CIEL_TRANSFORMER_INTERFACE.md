# CIEL-Transformer Interface v1.9

This layer defines the bridge between CIEL-LNS/Ω lingophysics and transformer-style neural language models.

The goal is **not** to replace statistical learning. The goal is to feed a model structural signals that normal token statistics tend to flatten:

- concept vs operator distinction,
- operator class and arity,
- event-frame compatibility,
- case-gauge role reconstruction,
- TAM-E features,
- scope and negation status,
- dynamic deixis anchors,
- ontological aspect such as identity/state and thing/concept,
- synonym phase coherence and antonym Euler phase,
- graph distance between concept/operator cards.

Canonical flow:

```text
Text
→ CIEL parser / card linker
→ CIEL feature tensor
→ Transformer / adapter / attention bias
→ Output
→ CIEL validator loop
→ accept / repair / report
```

This repository does not train a transformer yet. v1.9 defines an interface and deterministic reference functions that can be used as preprocessing, auxiliary supervision, attention-bias generation, or post-generation validation.

## Four integration levels

1. **Feature sidecar**: keep the model unchanged; attach CIEL tensors to examples.
2. **Auxiliary tasks**: predict CIEL labels during training.
3. **Attention bias**: add structural bias to attention logits.
4. **Validator loop**: reject or repair outputs that violate core invariants.

The design principle is simple:

```text
Do not train the model to believe CIEL.
Train or guide it to respect CIEL invariants.
```
