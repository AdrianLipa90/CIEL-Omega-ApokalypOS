from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CatalogModel:
    key: str
    display_name: str
    gguf_filename_hint: str
    recommended_ram_gb: float
    recommended_vram_gb: Optional[float]
    notes: str
    url_hint: str


MODEL_CATALOG: list[CatalogModel] = [
    CatalogModel(
        key='llama3_8b_q4',
        display_name='Llama 3 8B (Q4) — balanced',
        gguf_filename_hint='llama3-8b-q4.gguf',
        recommended_ram_gb=8.0,
        recommended_vram_gb=6.0,
        notes='Dobry start dla CPU, lepiej działa z GPU layers. Zwiększ n_ctx jeśli masz RAM.',
        url_hint='(wklej link do pliku .gguf z wybranego źródła)',
    ),
    CatalogModel(
        key='mistral7b_q4',
        display_name='Mistral 7B (Q4) — fast',
        gguf_filename_hint='mistral-7b-q4.gguf',
        recommended_ram_gb=8.0,
        recommended_vram_gb=6.0,
        notes='Szybki model do demo; często bardzo dobry stosunek jakości do prędkości.',
        url_hint='(wklej link do pliku .gguf z wybranego źródła)',
    ),
    CatalogModel(
        key='tiny_3b_q4',
        display_name='Small 3B (Q4) — low-spec demo',
        gguf_filename_hint='small-3b-q4.gguf',
        recommended_ram_gb=4.0,
        recommended_vram_gb=3.0,
        notes='Dla słabszych maszyn. Mniejsza jakość, ale łatwe uruchomienie.',
        url_hint='(wklej link do pliku .gguf z wybranego źródła)',
    ),
]
