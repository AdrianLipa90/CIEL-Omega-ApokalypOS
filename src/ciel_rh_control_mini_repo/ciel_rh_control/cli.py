import argparse, json
from .controller import RHController
from .models import ThresholdProfile

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--rh", type=float, required=True)
    p.add_argument("--sector", type=str, default="generic")
    p.add_argument("--r1", type=float, default=0.30)
    p.add_argument("--r2", type=float, default=0.70)
    a = p.parse_args()
    d = RHController(ThresholdProfile(r1=a.r1, r2=a.r2)).evaluate(a.rh, sector=a.sector)
    print(json.dumps({
        "rh": d.rh, "sector": d.sector, "mode": d.mode, "severity": d.severity,
        "allowed_actions": d.allowed_actions,
        "discouraged_actions": d.discouraged_actions,
        "actions": d.actions,
        "sector_overrides": d.sector_overrides,
        "notes": d.notes,
    }, indent=2))

if __name__ == "__main__":
    main()
