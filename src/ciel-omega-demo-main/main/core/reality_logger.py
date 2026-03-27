from __future__ import annotations

import json
import os
import time
from typing import Any, Dict


class RealityLogger:
    def __init__(self, path: str = 'logs/reality.jsonl'):
        self.path = path
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

    def record(self, step: int, metrics: Dict[str, Any]) -> None:
        rec = dict(step=step, t=time.time(), **metrics)
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
