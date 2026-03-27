from src.ciel_sot_agent.sapiens_panel.controller import run_sapiens_panel


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Run the Sapiens panel foundation shell.')
    parser.add_argument('text', nargs='?', default='Hello, model.', help='Initial user text for packet-aware panel state.')
    parser.add_argument('--sapiens-id', default='sapiens', help='Sapiens/client identity label.')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    result = run_sapiens_panel(root, user_text=args.text, sapiens_id=args.sapiens_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
