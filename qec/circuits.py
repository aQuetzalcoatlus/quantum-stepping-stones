# qec/circuits.py
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit


def bitflip_encode_circuit() -> QuantumCircuit:
    """
    3-qubit repetition (bit-flip) encoding circuit:
    Take |ψ⟩ on q0, fan it out to q1 and q2 using CNOTs.
    """
    qc = QuantumCircuit(3, name="Encode")
    qc.cx(0, 1)
    qc.cx(0, 2)
    return qc


def bitflip_syndrome_circuit() -> QuantumCircuit:
    """
    Syndrome extraction circuit for the bit-flip code:
    Two ancillas (q3,q4) capture parity of (q0,q1) and (q1,q2).
    """
    qc = QuantumCircuit(
        5, 2, name="Syndrome"
    )  # 3 data + 2 ancillas, 2 classical for meas
    # encoding step
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier()
    # ancilla 3 measures parity of (q0,q1)
    qc.cx(0, 3)
    qc.cx(1, 3)
    # ancilla 4 measures parity of (q1,q2)
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.barrier()
    qc.measure(3, 0)
    qc.measure(4, 1)
    return qc


def draw_circuit(circuit: QuantumCircuit, figsize=(6, 3)):
    """
    Render a QuantumCircuit to a matplotlib Figure, suitable for st.image.
    """
    fig, ax = plt.subplots(figsize=figsize)
    circuit.draw(output="mpl", ax=ax)
    fig.tight_layout()
    return fig
