#!/usr/bin/env python3
from pathlib import Path
import csv
from ciel_relational_mechanism.sim import PairKernel, RelationalPhaseToySim
OUT = Path(__file__).resolve().parents[1] / 'registries' / 'toy_sim_history.csv'
labels = ['S','C','Q','T']
initial = {k: 0.0 for k in labels}
kernel = PairKernel.zero(labels)
kernel.set_symmetric('S','C',1.0)
kernel.set_symmetric('C','Q',0.8)
kernel.set_symmetric('Q','T',1.2)
kernel.set_symmetric('S','T',0.5)
sim = RelationalPhaseToySim(labels=labels, initial_gamma=initial, kernel=kernel, dt=0.01, learning_rate=0.05, reduction_threshold=1.0)
rows = sim.run(steps=25)
with open(OUT,'w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['step','delta_H_real','delta_H_imag','R_H','reduction_ready'] + [f'gamma_{k}' for k in labels])
    for r in rows:
        w.writerow([r.step,r.delta_H_real,r.delta_H_imag,r.R_H,r.reduction_ready] + [r.gamma[k] for k in labels])
print(OUT)
