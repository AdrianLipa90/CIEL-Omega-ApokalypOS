from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from integration.Orbital.main.global_pass import run_global_pass


if __name__ == '__main__':
    result = run_global_pass()
    import json
    print(json.dumps(result, indent=2))
