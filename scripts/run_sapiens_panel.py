from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.ciel_sot_agent.sapiens_panel.controller import run_sapiens_panel
from src.ciel_sot_agent.satellite_authority import require_interaction_surface, project_authority_summary


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Run the Sapiens panel foundation shell.')
    parser.add_argument('text', nargs='?', default='Hello, model.', help='Initial user text for packet-aware panel state.')
    parser.add_argument('--sapiens-id', default='sapiens', help='Sapiens/client identity label.')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    authority = project_authority_summary(require_interaction_surface(root, 'SAT-SAPIENS-0001'))
    result = run_sapiens_panel(root, user_text=args.text, sapiens_id=args.sapiens_id)
    result['satellite_authority'] = authority
    print(json.dumps(result, ensure_ascii=False, indent=2))
