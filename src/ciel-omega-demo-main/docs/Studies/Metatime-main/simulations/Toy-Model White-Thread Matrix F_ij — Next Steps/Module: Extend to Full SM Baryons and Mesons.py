# Example: baryon made of quarks q1, q2, q3
def baryon_F(q_indices, F_quark):
    # Simple geometric mean of pairwise F_ij
    F_baryon = 1.0
    for i in range(len(q_indices)):
        for j in range(i+1, len(q_indices)):
            F_baryon *= F_quark[q_indices[i], q_indices[j]]
    F_baryon = F_baryon ** (2/3)  # normalize to single baryon
    return F_baryon

# Example: meson q1-antiq2
def meson_F(q1, q2, F_quark):
    return F_quark[q1, q2]

