from __future__ import annotations
from pathlib import Path
import csv
ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'registries'
rows = [
    {'symbol':'tau_i','meaning':'topological eigenvalue / cycle label','source_type':'contract+pdf','source_name':'Contract, Sigma.pdf, Derivation of tau_i.pdf','status':'confirmed','category':'state','equation_or_note':'tau={0.263,0.353,0.489} in relational contract seed; tau_i used across Metatime PDFs'},
    {'symbol':'gamma_i','meaning':'Berry phase on cycle','source_type':'contract+pdf','source_name':'Contract, Metatime PDFs','status':'confirmed','category':'phase','equation_or_note':'gamma_i = integral of connection over cycle'},
    {'symbol':'Delta_H','meaning':'holonomy defect sum','source_type':'contract','source_name':'Contract _Sapiens-AI.txt','status':'confirmed','category':'constraint','equation_or_note':'Delta_H = sum_k exp(i gamma_k)'},
    {'symbol':'R_H','meaning':'coherence/decoherence scalar from holonomy defect','source_type':'contract','source_name':'Contract _Sapiens-AI.txt','status':'confirmed','category':'constraint','equation_or_note':'R_H = |Delta_H|^2'},
    {'symbol':'V_rel','meaning':'relational potential','source_type':'contract','source_name':'Contract _Sapiens-AI.txt','status':'confirmed','category':'potential','equation_or_note':'V_rel = kappa_H R_H + V_I + V_D'},
    {'symbol':'L_rel','meaning':'relational lagrangian','source_type':'contract','source_name':'Contract _Sapiens-AI.txt','status':'confirmed','category':'lagrangian','equation_or_note':'L_truth + L_coh + L_clarity - L_distortion'},
    {'symbol':'Sigma_i','meaning':'local fingerprint state','source_type':'pdf','source_name':'Sigma.pdf','status':'confirmed','category':'state','equation_or_note':'Sigma_i = (tau_i, gamma_i, F_i)'},
    {'symbol':'W_ij','meaning':'white-thread holonomy between cycles','source_type':'pdf','source_name':'Sigma.pdf, Metatime PDFs','status':'confirmed','category':'holonomy','equation_or_note':'pairwise transporter'},
    {'symbol':'F_i','meaning':'single-state topological correction','source_type':'pdf','source_name':'Sigma.pdf','status':'confirmed','category':'correction','equation_or_note':'local correction in fingerprint'},
    {'symbol':'F_ij','meaning':'pairwise correction factor','source_type':'pdf','source_name':'Sigma.pdf, interpretation.md','status':'confirmed','category':'correction','equation_or_note':'pairwise factor from Wij and phase structure'},
    {'symbol':'Lambda_0(x)','meaning':'micro-macro regulator','source_type':'pdf','source_name':'Lambda_meta.pdf, Metatime_with_Euler_extension (8).pdf','status':'confirmed','category':'potential','equation_or_note':'tensor-scalar/coupling regulator'},
    {'symbol':'epsilon','meaning':'micro coupling / defect amplitude','source_type':'pdf','source_name':'Lambda_meta.pdf, Metatime_with_Euler_extension (8).pdf','status':'confirmed','category':'coupling','equation_or_note':'epsilon approx 1.5e-3 candidate from current PDFs'},
    {'symbol':'D_f','meaning':'fractal dimension candidate','source_type':'pdf+user','source_name':'Lambda_meta.pdf + user correction','status':'unresolved','category':'dimension','equation_or_note':'old pdf candidate 2.7; user indicates newer docs approx 2.5; do not freeze'},
]
REG.mkdir(exist_ok=True)
with open(REG/'formal_symbols.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
with open(REG/'phase_couplings.csv','w',newline='',encoding='utf-8') as f:
    fieldnames=['object','role','depends_on','feeds_into','status','note']
    w=csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader(); w.writerows([
        {'object':'tau_i','role':'cycle label / eigenvalue','depends_on':'seed / generator','feeds_into':'Sigma_i, F_ij, runtime state tables','status':'confirmed','note':'from contract+pdf layer'},
        {'object':'gamma_i','role':'Berry phase','depends_on':'cycle on sphere + connection','feeds_into':'Delta_H, Sigma_i, W_ij','status':'confirmed','note':'phase coupling primitive'},
        {'object':'Delta_H','role':'closure defect','depends_on':'gamma_i','feeds_into':'R_H, reduction conditions, phase diagnostics','status':'confirmed','note':'Euler-Berry mechanism'},
        {'object':'R_H','role':'coherence scalar','depends_on':'Delta_H','feeds_into':'V_rel, monitoring','status':'confirmed','note':'contract layer'},
        {'object':'Sigma_i','role':'local fingerprint','depends_on':'tau_i, gamma_i, F_i','feeds_into':'pairwise mapping and runtime symbolism','status':'confirmed','note':'do not confuse with possible Sigma_global'},
        {'object':'W_ij','role':'pairwise holonomy','depends_on':'path, phases, connection','feeds_into':'F_ij, relation/orchestration','status':'confirmed','note':'white-thread'},
        {'object':'F_ij','role':'pairwise correction','depends_on':'W_ij, tau_i, tau_j','feeds_into':'splitting / relation strength / hadron candidates','status':'confirmed','note':'not final SoT values'},
    ])
with open(REG/'symbol_to_runtime_map.csv','w',newline='',encoding='utf-8') as f:
    fieldnames=['symbol','runtime_path','runtime_object','mapping_type','confidence','note']
    w=csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader(); w.writerows([
        {'symbol':'Delta_H','runtime_path':'ciel_omega/constraints/euler_constraint.py','runtime_object':'module','mapping_type':'direct-name/constraint','confidence':'high','note':'explicit canonical runtime target'},
        {'symbol':'gamma_i','runtime_path':'ciel_omega/fields/intention_field.py','runtime_object':'module','mapping_type':'phase-field candidate','confidence':'medium','note':'phase semantics likely distributed'},
        {'symbol':'Sigma_i','runtime_path':'ciel_omega/fields/sigma_series.py','runtime_object':'module','mapping_type':'name-level candidate','confidence':'medium','note':'name match only; inspect later'},
        {'symbol':'R_H','runtime_path':'ciel_omega/memory/holonomy.py','runtime_object':'module','mapping_type':'holonomy/coherence candidate','confidence':'medium','note':'needs manual confirmation'},
        {'symbol':'tau_i','runtime_path':'ciel_omega/time','runtime_object':'package-candidate','mapping_type':'conceptual','confidence':'low','note':'package may not exist yet; derive from runtime mapping later'},
        {'symbol':'W_ij','runtime_path':'ciel_omega/orbital/global_pass.py','runtime_object':'module','mapping_type':'orbital/holonomy candidate','confidence':'low','note':'manual confirmation required'},
    ])
print('seeded registries')
