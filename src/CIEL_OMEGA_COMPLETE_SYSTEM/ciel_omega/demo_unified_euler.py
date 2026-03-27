#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ciel_omega.unified_system import UnifiedSystem


def main() -> None:
    system = UnifiedSystem.create(identity_phase=0.25)
    out = system.run_text_cycle('Euler-constraint integration test.', metadata={'salience': 0.8, 'confidence': 0.76, 'novelty': 0.61})
    print(json.dumps(out['euler_metrics'], indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
