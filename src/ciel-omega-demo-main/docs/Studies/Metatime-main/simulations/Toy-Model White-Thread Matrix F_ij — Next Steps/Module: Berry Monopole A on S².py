# For toy S²: spherical coordinates (θ, φ)
def berry_connection(theta_i, phi_i):
    # Dirac monopole, minimal coupling:
    # A_phi = g*(1 - cos θ), g = monopole charge (set 1 for simplicity)
    g = 1.0
    A_phi = g * (1 - np.cos(theta_i))
    return A_phi

# Compute holonomy between two cycles (θ_i, φ_i) -> (θ_j, φ_j)
def compute_W(theta_i, phi_i, theta_j, phi_j):
    # Approximate path integral along great circle
    A_i = berry_connection(theta_i, phi_i)
    delta_phi = phi_j - phi_i
    return np.exp(1j * A_i * delta_phi)

