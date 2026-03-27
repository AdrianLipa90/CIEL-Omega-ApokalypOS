from __future__ import annotations

import numpy as np


_ZETA_2 = float(np.pi**2 / 6.0)
_EPS0 = float(1e-12 * _ZETA_2)


def _heisenberg_soft_clip_complex(x: np.ndarray, clip: float) -> np.ndarray:
    if clip <= 0.0:
        return x
    mag = np.abs(x)
    scale = (float(clip) * np.tanh(mag / float(clip))) / (mag + _EPS0)
    return x * scale


def sanitize_field(a: np.ndarray, *, clip: float = 1e6) -> np.ndarray:
    x = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
    if clip and float(clip) > 0.0:
        x = _heisenberg_soft_clip_complex(x.astype(np.complex128, copy=False), float(clip)).astype(a.dtype, copy=False)
    return x


def normalize_field(psi: np.ndarray, *, eps: float = _EPS0, clip: float = 1e6) -> np.ndarray:
    x = sanitize_field(psi, clip=float(clip))
    nrm = field_norm(x, eps=float(eps))
    return x / float(nrm)


def laplacian2(a: np.ndarray) -> np.ndarray:
    a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
    out = np.zeros_like(a, dtype=a.dtype)
    out[1:-1, 1:-1] = a[2:, 1:-1] + a[:-2, 1:-1] + a[1:-1, 2:] + a[1:-1, :-2] - 4.0 * a[1:-1, 1:-1]
    return out


def field_norm(psi: np.ndarray, eps: float = _EPS0) -> float:
    psi = np.nan_to_num(psi, nan=0.0, posinf=0.0, neginf=0.0)
    e = float(np.mean(np.abs(psi) ** 2))
    return float(np.sqrt(max(e, 0.0)) + float(eps))


def coherence_metric(psi: np.ndarray) -> float:
    psi = np.nan_to_num(psi, nan=0.0, posinf=0.0, neginf=0.0)
    gx = np.zeros_like(psi)
    gy = np.zeros_like(psi)
    gx[:, 1:-1] = psi[:, 2:] - psi[:, :-2]
    gy[1:-1, :] = psi[2:, :] - psi[:-2, :]
    E = np.mean(np.abs(gx) ** 2 + np.abs(gy) ** 2)
    E = float(np.nan_to_num(E, nan=0.0, posinf=0.0, neginf=0.0))
    return float(1.0 / (1.0 + max(E, 0.0)))
