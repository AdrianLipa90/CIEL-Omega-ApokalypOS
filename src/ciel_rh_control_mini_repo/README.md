# ciel_rh_control

Mini repo for **R_H-driven control**.

Purpose:
- accept a coherence-defect scalar `R_H`
- classify system state into operational modes
- return recommended action policy
- stay separate and pluggable into Omega or any other runtime

## Quick use

```python
from ciel_rh_control import RHController, ThresholdProfile

controller = RHController(ThresholdProfile(r1=0.30, r2=0.70))
decision = controller.evaluate(0.82, sector="runtime")
print(decision.mode)
```

## CLI

```bash
python -m ciel_rh_control.cli --rh 0.82 --sector runtime
```
