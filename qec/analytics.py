from __future__ import annotations

import numpy as np

from .codes import ThreeQubitBitFlip
from .decoders import lookup_decoder_3q
from .error_models import bsc_flip_mask


def repetition_mc_error(
    n: int, p: float, trials: int = 10_000, rng: np.random.Generator | None = None
) -> float:
    rng = rng or np.random.default_rng()
    flips = (rng.random((trials, n)) < p).astype(int)
    decoded = (flips.sum(axis=1) > n / 2).astype(int)
    return float(decoded.mean())


def bitflip_mc_error(
    p: float, trials: int = 10_000, rng: np.random.Generator | None = None
) -> float:
    rng = rng or np.random.default_rng()
    code = ThreeQubitBitFlip()
    errs = 0
    for _ in range(trials):
        e = bsc_flip_mask(3, p, rng=rng)
        syn, corr = lookup_decoder_3q(code, e)
        post = (e + corr) % 2
        errs += int(code.decode_majority(post) == 1)
    return errs / trials


def phaseflip_mc_error(
    p: float, trials: int = 10_000, rng: np.random.Generator | None = None
) -> float:
    """
    Same parity logic but treating Z-errors (H-basis argument).
    Logical phase error if majority(Z) after correction.
    """
    rng = rng or np.random.default_rng()
    code = ThreeQubitBitFlip()
    errs = 0
    for _ in range(trials):
        eZ = bsc_flip_mask(3, p, rng=rng)  # which qubits suffered Z
        syn, corrZ = lookup_decoder_3q(code, eZ)
        post = (eZ + corrZ) % 2
        errs += int(post.sum() > 1)
    return errs / trials
