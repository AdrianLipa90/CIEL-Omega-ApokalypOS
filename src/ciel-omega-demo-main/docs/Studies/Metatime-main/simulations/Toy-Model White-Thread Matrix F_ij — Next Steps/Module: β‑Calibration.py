import numpy as np

# Input: θ_i, I0 (original)
theta = np.array([...])  # 12 fermionów
I0 = 0.009

# Experimental target F_i from PDG (example)
F_exp = np.array([1.0, 0.995, 0.998, ...])  # 12 wartości F_i

# Define function to compute directional F_ij with beta
def compute_F(beta, theta):
    N = len(theta)
    F = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            F[i,j] = np.exp(beta * (theta[j] - theta[i]))
    return F

# Loss function: difference between column sums or row averages and F_exp
def loss(beta, theta, F_exp):
    F = compute_F(beta, theta)
    F_col_avg = F.mean(axis=0)  # column-wise average
    return np.sum((F_col_avg - F_exp)**2)

# Optimize beta
from scipy.optimize import minimize
res = minimize(lambda b: loss(b, theta, F_exp), x0=[I0])
beta_opt = res.x[0]
print("Optimal beta:", beta_opt)

