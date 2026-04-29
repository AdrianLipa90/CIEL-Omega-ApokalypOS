#!/usr/bin/env python3
"""
CIEL LoRA Training Script

Fine-tuning qwen2.5-0.5B z orbitalną inicjalizacją LoRA.

Wymaga:
  pip install torch==2.0.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117
  pip install transformers peft trl accelerate bitsandbytes

Użycie:
  python3 ciel_lora_train.py
  python3 ciel_lora_train.py --epochs 3 --rank 8 --output ./ciel_lora_out
  python3 ciel_lora_train.py --dry-run   # sprawdź konfigurację bez treningu

Architektura:
  - Base model: Qwen2.5-0.5B (qwen2.5-0.5b-instruct-q2_k.gguf → najpierw FP16 HF)
  - LoRA rank: 8 (inicjalizowany z eigenvektorów J_kj)
  - Holonomy constraint: L_total = L_ce + λ·L_holonomy
  - Training: CPU (sm_61 niekompatybilny z torch>=2.1) lub GPU gdy dostępne
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np

PROJECT = Path(__file__).parent.parent
OMEGA_SRC = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM")
for _p in (OMEGA_SRC,):
    if _p not in sys.path:
        sys.path.insert(0, _p)

DATASET_PATH = Path("/tmp/ciel_dataset.jsonl")
LORA_SEED_PATH = Path("/tmp/ciel_lora_seed.npz")
DEFAULT_OUTPUT = Path("/tmp/ciel_lora_out")

# Model HuggingFace (nie GGUF — LoRA wymaga FP16/BF16)
HF_MODEL_ID = "Qwen/Qwen3-1.7B"  # baza Lucy-128k


# ── Holonomy regularizer (PyTorch) ────────────────────────────────────────────

def holonomy_loss_torch(model, target: float = math.pi, weight: float = 0.01):
    """
    L_holonomy = λ · ||∑_k φ_k - π||²

    φ_k = normy wag warstw LoRA → proxy dla faz kanałów pamięci.
    Constraint Eulera: suma faz = π (spin ½ holonomy).
    """
    import torch
    phases = []
    for name, param in model.named_parameters():
        if "lora_A" in name and param.requires_grad:
            # Norma wierszy jako proxy fazy
            row_norms = param.data.norm(dim=1)
            phases.extend(row_norms.tolist())

    if not phases:
        return torch.tensor(0.0)

    phase_tensor = torch.tensor(phases[:8], dtype=torch.float32)  # pierwsze 8 kanałów
    phase_sum = phase_tensor.sum()
    return weight * (phase_sum - target) ** 2


# ── LoRA weight injection from orbital seed ───────────────────────────────────

def inject_orbital_weights(model, seed_path: Path) -> bool:
    """Wstrzyknij orbital seed do macierzy LoRA A przez named_parameters."""
    import torch
    if not seed_path.exists():
        print(f"[LoRA] brak seed: {seed_path} — użyję domyślnej init")
        return False

    seed = np.load(seed_path)
    A_seed = torch.tensor(seed["A"], dtype=torch.float32)  # (rank, hidden)

    injected = 0
    with torch.no_grad():
        for name, param in model.named_parameters():
            if "lora_A" in name and param.requires_grad:
                rank, hidden = param.shape
                padded = torch.zeros(rank, hidden)
                r_s = min(rank, A_seed.shape[0])
                h_s = min(hidden, A_seed.shape[1])
                padded[:r_s, :h_s] = A_seed[:r_s, :h_s]
                param.data.copy_(padded)
                injected += 1

    print(f"[LoRA] orbital seed wstrzyknięty do {injected} macierzy A")
    return injected > 0


# ── Dataset loader ────────────────────────────────────────────────────────────

def load_dataset(path: Path) -> List[Dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def format_for_training(record: Dict, tokenizer) -> str:
    """Formatuj rekord jako tekst treningowy (chat template)."""
    messages = record.get("messages", [])
    if hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=False
            )
        except Exception:
            pass
    # Fallback: prosty format
    parts = []
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"]
        parts.append(f"<|{role}|>\n{content}")
    return "\n".join(parts) + "\n<|END|>"


# ── Training ──────────────────────────────────────────────────────────────────

def train(
    dataset_path: Path = DATASET_PATH,
    output_dir: Path = DEFAULT_OUTPUT,
    rank: int = 8,
    epochs: int = 2,
    batch_size: int = 1,
    learning_rate: float = 2e-4,
    holonomy_weight: float = 0.01,
    dry_run: bool = False,
) -> None:
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
        from peft import LoraConfig, get_peft_model, TaskType
        from trl import SFTTrainer
    except ImportError as e:
        print(f"[błąd] brakuje pakietu: {e}")
        print("Zainstaluj: pip install transformers peft trl accelerate")
        print("Torch sm_61: pip install torch==2.0.1+cu117 "
              "--extra-index-url https://download.pytorch.org/whl/cu117")
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[train] device: {device}")
    print(f"[train] model: {HF_MODEL_ID}")
    print(f"[train] rank: {rank}  epochs: {epochs}  lr: {learning_rate}")
    print(f"[train] holonomy_weight: {holonomy_weight}")

    if dry_run:
        print("[dry-run] konfiguracja OK")
        return

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Model
    model = AutoModelForCausalLM.from_pretrained(
        HF_MODEL_ID,
        torch_dtype=torch.float32 if device == "cpu" else torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    # LoRA config — cele: q_proj, v_proj (uwaga)
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=rank,
        lora_alpha=rank * 2,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
    )
    model = get_peft_model(model, lora_config)

    # Wstrzyknij orbital seed
    inject_orbital_weights(model, LORA_SEED_PATH)
    model.print_trainable_parameters()

    # Dataset
    records = load_dataset(dataset_path)
    texts = [format_for_training(r, tokenizer) for r in records]
    print(f"[train] dataset: {len(texts)} przykładów")

    from datasets import Dataset as HFDataset
    hf_dataset = HFDataset.from_dict({"text": texts})

    # Training args
    output_dir.mkdir(parents=True, exist_ok=True)
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        fp16=False,  # CPU safe
        bf16=False,
        logging_steps=10,
        save_strategy="epoch",
        report_to="none",
        dataloader_num_workers=0,
    )

    # Custom trainer z holonomy regularizer
    class OrbitalTrainer(SFTTrainer):
        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            result = super().compute_loss(model, inputs, return_outputs=return_outputs, **kwargs)
            loss = result[0] if return_outputs else result
            h_loss = holonomy_loss_torch(model, weight=holonomy_weight)
            total = loss + h_loss
            return (total, result[1]) if return_outputs else total

    trainer = OrbitalTrainer(
        model=model,
        args=training_args,
        train_dataset=hf_dataset,
        dataset_text_field="text",
        max_seq_length=512,
        tokenizer=tokenizer,
    )

    print("[train] start...")
    trainer.train()
    model.save_pretrained(str(output_dir / "final"))
    tokenizer.save_pretrained(str(output_dir / "final"))
    print(f"[train] zapisano: {output_dir}/final")
    print("Konwertuj do GGUF: python3 convert_hf_to_gguf.py "
          f"{output_dir}/final --outtype q4_k_m")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIEL Orbital LoRA Training")
    parser.add_argument("--rank", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--holonomy-weight", type=float, default=0.01)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    train(
        dataset_path=args.dataset,
        output_dir=args.output,
        rank=args.rank,
        epochs=args.epochs,
        batch_size=args.batch,
        learning_rate=args.lr,
        holonomy_weight=args.holonomy_weight,
        dry_run=args.dry_run,
    )
