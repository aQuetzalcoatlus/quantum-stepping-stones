from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class ParityCheck:
    """Binary parity-check matrix S (rows = checks, cols = qubits), over GF(2)."""

    S: np.ndarray  # shape (m, n), dtype=int

    def syndrome(self, e_bits: np.ndarray) -> np.ndarray:
        """Compute syndrome s = S e (mod 2)."""
        return (self.S @ e_bits) % 2


@dataclass(frozen=True)
class ThreeQubitBitFlip:
    """
    3-qubit bit-flip code viewed classically.
    Logical 0_L=000, 1_L=111. Checks: Z1Z2, Z2Z3 -> parity on (1,2) and (2,3).
    """

    checks: ParityCheck = ParityCheck(S=np.array([[1, 1, 0], [0, 1, 1]], dtype=int))

    @property
    def distance(self) -> int:
        return 3

    def decode_majority(self, word_bits: np.ndarray) -> int:
        """Return decoded bit after majority vote; 1 indicates logical flip if we sent 0."""
        return int(word_bits.sum() > 1)

    def syndrome(self, e_bits: np.ndarray) -> np.ndarray:
        return self.checks.syndrome(e_bits)
