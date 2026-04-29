# Relational Seed–Orbit Solver v0

## Status
Canonical working derivation for the first solver that maps repository objects into:

`file -> seed vector -> semantic mass -> local time -> orbit -> winding`

This document is intentionally placed in `docs/science/` because it is a derivation-level bridge between the orbital indexing work and the future runtime solver layer.

---

## 1. Goal

For each repository object `f`, define a solver that computes:

\[
 f \to \vec{\sigma}_f \to (M_{EC}, M_{ZS}) \to M_{sem} \to A_n^{eff} \to T_f \to r_f \to \tau_f \to \Delta\phi_f \to w_f
\]

where:

- `\vec{\sigma}_f` = seed vector,
- `M_{EC}` = Euler–Collatz attractor contribution,
- `M_{ZS}` = Zeta–Schrodinger attractor contribution,
- `M_{sem}` = semantic mass,
- `A_n^{eff}` = effective attractor weight of sphere/sector `S_n`,
- `T_f` = effective orbital period,
- `r_f` = orbital radius,
- `\tau_f` = local proper-time scale,
- `\Delta\phi_f` = phase step,
- `w_f` = winding number.

---

## 2. Input state of an object

For each file/object `f`, define the minimal input record:

\[
E_f = (s_f, d_f, p_f, e_f, t_f, \rho_f, \phi_f)
\]

with:

- `s_f` — base seed,
- `d_f` — dependency profile,
- `p_f` — provenance / canonicality,
- `e_f` — execution criticality,
- `t_f` — type / layer,
- `\rho_f` — informational density,
- `\phi_f` — base phase.

---

## 3. Seed vector

Instead of a scalar-only seed, define a seed vector:

\[
\vec{\sigma}_f = (\sigma_f^{loc}, \sigma_f^{dep}, \sigma_f^{prov}, \sigma_f^{exec}, \sigma_f^{type}, \sigma_f^{phase})
\]

with:

\[
\sigma_f^{loc} = H(path, size, content)
\]
\[
\sigma_f^{dep} = C_{dep}(f)
\]
\[
\sigma_f^{prov} = C_{prov}(f)
\]
\[
\sigma_f^{exec} = C_{exec}(f)
\]
\[
\sigma_f^{type} = W_{type}(f)
\]
\[
\sigma_f^{phase} = \phi_f
\]

Then define the scalar seed norm:

\[
S_f = \lVert \vec{\sigma}_f \rVert_Q
\]

with weighted metric:

\[
Q = \mathrm{diag}(q_1, \dots, q_6)
\]

so that:

\[
S_f = \sqrt{q_1 (\sigma_f^{loc})^2 + q_2 (\sigma_f^{dep})^2 + q_3 (\sigma_f^{prov})^2 + q_4 (\sigma_f^{exec})^2 + q_5 (\sigma_f^{type})^2 + q_6 (\sigma_f^{phase})^2}
\]

---

## 4. Two-attractor split

### 4.1 Euler–Collatz contribution

\[
M_{EC}(f) = u_1 \Pi_{disc}(S_f) + u_2 \Pi_{closure}(f) + u_3 \Pi_{rhythm}(f)
\]

with first canonical choices:

\[
\Pi_{disc}(S_f) = \operatorname{frac}(S_f)
\]
\[
\Pi_{closure}(f) = \frac{1}{1 + R_H(f)}
\]
\[
\Pi_{rhythm}(f) = \frac{1}{1 + \mathrm{var}(\deg_{nbr}(f))}
\]

### 4.2 Zeta–Schrodinger contribution

\[
M_{ZS}(f) = v_1 \Pi_{spec}(f) + v_2 \Pi_{res}(f) + v_3 \Pi_{meta}(f)
\]

with first canonical choices:

\[
\Pi_{spec}(f) = \text{eigenvector-centrality}(f)
\]
\[
\Pi_{res}(f) = \frac{1}{Z_f} \sum_j |W_{fj}|\cos(\phi_f - \phi_j)
\]
\[
\Pi_{meta}(f) = \frac{1}{1 + \mathrm{drift}_f}
\]

---

## 5. Semantic mass

\[
M_{sem}(f) = \alpha M_{EC}(f) + \beta M_{ZS}(f) + \chi C_{dep}(f) + \delta C_{prov}(f) + \epsilon C_{exec}(f)
\]

Normalize over all objects:

\[
\widetilde{M}_{sem}(f) = \frac{M_{sem}(f)}{\sum_g M_{sem}(g)}
\]

and define the amplitude:

\[
a_f = \sqrt{\widetilde{M}_{sem}(f)}
\]

---

## 6. Effective attractor weight of a sphere / sector

For sector or sphere `S_n`:

\[
A_n^{eff} = \sum_{f \in S_n} \omega_f M_{sem}(f) + \lambda \mathcal{C}_n - \mu \mathcal{D}_n
\]

where:

- `\omega_f` = canonicality weight,
- `\mathcal{C}_n` = coherence of the sphere,
- `\mathcal{D}_n` = defect of the sphere.

First operational forms:

\[
\mathcal{C}_n = \frac{1}{|S_n|^2} \left| \sum_{f,g \in S_n} W_{fg} \right|
\]
\[
\mathcal{D}_n = \frac{1}{|S_n|} \sum_{f \in S_n} R_H(f)
\]

---

## 7. Local proper time

Define local proper-time scale as:

\[
\Delta \tau_f = \Delta t \cdot \frac{1 + \xi_M \widetilde{M}_{sem}(f) + \xi_D \mathcal{D}_f}{1 + \xi_C \mathcal{C}_f + \xi_R / r_f}
\]

Interpretation:

- larger semantic mass and defect slow local time,
- larger coherence and closer orbit accelerate local dynamics.

---

## 8. Orbit solver

Use an effective Kepler-like law:

\[
T_f^2 \propto \frac{a_f^3}{A_n^{eff}}
\]

Define first operational period model:

\[
T_f = T_0 \cdot \frac{1 + \zeta_M \widetilde{M}_{sem}(f) + \zeta_P C_{prov}(f)}{1 + \zeta_E C_{exec}(f) + \zeta_C \mathcal{C}_f}
\]

Then:

\[
r_f = \left( \kappa_T T_f^2 A_n^{eff} \right)^{1/3}
\]

and discrete orbit index:

\[
\operatorname{orbit}(f) = \left\lfloor \frac{r_f - r_{min}}{\Delta r} \right\rfloor
\]

---

## 9. Phase evolution solver

Take the phase dynamics in discrete form:

\[
\phi_f(k+1) = \phi_f(k) + \Delta t\, \omega_f(k)
\]
\[
\omega_f(k+1) = \omega_f(k) + \Delta t \left( -\partial_{\phi_f} V_{tot} - \eta_\phi \omega_f(k) + J_f(k) \right)
\]

with coupling current:

\[
J_f(k) = \sum_j |W_{fj}| \sin(\phi_j(k) - \phi_f(k))
\]

---

## 10. Winding number

The winding number must follow process topology rather than decoration:

\[
w_f(N) = \frac{1}{2\pi} \sum_{k=1}^{N} \Delta\phi_f(k) \frac{\Delta t}{\Delta\tau_f(k)}
\]

with decomposition:

\[
w_f = w_f^{EC} + w_f^{ZS} + w_f^{rel}
\]

---

## 11. Full solver chain

### Input

\[
f \mapsto (path, content, deps, prov, exec, type, \phi_0)
\]

### Step 1

\[
\vec{\sigma}_f \to S_f
\]

### Step 2

\[
S_f \to (M_{EC}(f), M_{ZS}(f))
\]

### Step 3

\[
(M_{EC}, M_{ZS}, C_{dep}, C_{prov}, C_{exec}) \to M_{sem}(f)
\]

### Step 4

\[
(M_{sem}, \mathcal{C}_n, \mathcal{D}_n) \to A_n^{eff}
\]

### Step 5

\[
(M_{sem}, A_n^{eff}, C_{prov}, C_{exec}, \mathcal{C}_f) \to T_f \to r_f \to \operatorname{orbit}(f)
\]

### Step 6

\[
(r_f, M_{sem}, \mathcal{C}_f, \mathcal{D}_f) \to \Delta\tau_f(k)
\]

### Step 7

\[
(\phi_f, \omega_f, W_{fj}, V_{tot}) \to \Delta\phi_f(k)
\]

### Step 8

\[
(\Delta\phi_f(k), \Delta\tau_f(k)) \to w_f
\]

---

## 12. What remains open

This solver closes the missing structural layer, but still requires calibration of:

- `\alpha, \beta, \chi, \delta, \epsilon`
- `u_i, v_i`
- `\xi_i, \zeta_i`
- the final form of `V_tot`
- the exact coupling between EC and ZS channels
- the non-diagonal metric `Q`, if later needed.

That is now a calibration problem, not a missing-solver problem.

---

## 13. Placement rationale

This document belongs in `docs/science/` because it is:

- not only implementation,
- not only theory,
- but an explicit derivation bridge between orbital indexing and executable runtime dynamics.
