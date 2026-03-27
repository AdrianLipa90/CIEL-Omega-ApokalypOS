from integration.Orbital.main.global_pass import run_global_pass


if __name__ == '__main__':
    result = run_global_pass()
    import json
    print(json.dumps(result, indent=2))
