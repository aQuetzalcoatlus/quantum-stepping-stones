from hypothesis import given
from hypothesis import strategies as st

from qec.stabilizers import pauli_commutes


@st.composite
def pauli_strings(draw, n=3):
    alphabet = ["I", "X", "Y", "Z"]
    return "".join(draw(st.sampled_from(alphabet)) for _ in range(n))


@given(P=pauli_strings(), Q=pauli_strings())
def test_commutation_symmetry(P, Q):
    assert pauli_commutes(P, Q) == pauli_commutes(Q, P)


def test_commutation_reflexive():
    assert pauli_commutes("XYZ", "XYZ") is True
