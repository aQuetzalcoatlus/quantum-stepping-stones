from __future__ import annotations

import numpy as np


def bsc_flip_mask(
    n: int, p: float, size: int | None = None, rng: np.random.Generator | None = None
) -> np.ndarray:
    """
    Bernoulli flip mask(s) for a Binary Symmetric Channel with prob p.
    - If size is None: returns (n,) mask.
    - If size is k: returns (k, n) masks.
    """
    rng = rng or np.random.default_rng()
    if size is None:
        return (rng.random(n) < p).astype(int)
    return (rng.random((size, n)) < p).astype(int)
