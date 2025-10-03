from __future__ import annotations

from typing import List

# simple per-site anticommute table
_ANTI = {
    frozenset({"X", "Z"}),
    frozenset({"Z", "X"}),
    frozenset({"X", "Y"}),
    frozenset({"Y", "X"}),
    frozenset({"Y", "Z"}),
    frozenset({"Z", "Y"}),
}


class PauliLengthError(ValueError):
    """Raised when Pauli strings have different lengths."""


def pauli_commutes(P: str, Q: str) -> bool:
    """Return True if equal-length Pauli strings commute."""

    if len(P) != len(Q):
        raise PauliLengthError(
            f"Pauli strings must have equal length (got {len(P)} vs {len(Q)})"
        )

    anti = 0
    for a, b in zip(P, Q):
        if a == "I" or b == "I" or a == b:
            continue
        if frozenset({a, b}) in _ANTI:
            anti += 1
    return (anti % 2) == 0


def syndrome_from_pauli(error: str, generators: List[str]) -> list[int]:
    """
    Predict 0(+1)/1(-1) for each generator: 1 iff error anticommutes with generator.
    """
    return [0 if pauli_commutes(error, g) else 1 for g in generators]
