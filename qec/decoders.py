from __future__ import annotations

import numpy as np

from .codes import ThreeQubitBitFlip

# Lookup: syndrome -> correction vector
_BITFLIP_LUT = {
    (0, 0): np.array([0, 0, 0], dtype=int),  # +1,+1 (no error)
    (1, 0): np.array([1, 0, 0], dtype=int),  # -1,+1 -> flip qubit 1
    (1, 1): np.array([0, 1, 0], dtype=int),  # -1,-1 -> flip qubit 2
    (0, 1): np.array([0, 0, 1], dtype=int),  # +1,-1 -> flip qubit 3
}


def lookup_decoder_3q(
    code: ThreeQubitBitFlip, e_bits: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (syndrome, correction_bits). correction_bits indicates which X (or Z in H-basis) to apply.
    """
    syn = tuple(code.syndrome(e_bits).tolist())
    corr = _BITFLIP_LUT[syn]
    return np.array(syn, dtype=int), corr
