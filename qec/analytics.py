from __future__ import annotations

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import Statevector

from .circuits import phase_demo_circuit
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


try:
    from qiskit_aer import Aer

    _AER_OK = True
except Exception:
    _AER_OK = False


def _counts_from_statevector(qc) -> dict[str, float]:
    """Return exact P(0), P(1) for a 1-qubit measured circuit (measurement already included)."""
    # remove final measurements to inspect amplitudes pre-meas
    base = qc.remove_final_measurements(inplace=False)
    sv = Statevector.from_instruction(base)
    # Because we incorporated the basis rotation (H) into the circuit already,
    # just read amplitude of |0> and |1> directly.
    p0 = float(np.abs(sv.data[0]) ** 2)
    return {"0": p0, "1": 1.0 - p0}


def _sample_counts(probs: dict[str, float], shots: int) -> dict[str, int]:
    if shots <= 0:
        return {"0": 0, "1": 0}
    outcomes = np.random.choice(["0", "1"], size=shots, p=[probs["0"], probs["1"]])
    return {"0": int((outcomes == "0").sum()), "1": int((outcomes == "1").sum())}


def phaseflip_mixed_counts(
    p: float, shots: int, *, measure_x_basis: bool
) -> tuple[dict[str, int], object, object]:
    """
    Emulate a Z error with probability p on |+>, measured either in Z or X basis.
    Returns (combined_counts, qc_I, qc_Z).
    """
    shots_z = int(round(p * shots))
    shots_i = shots - shots_z

    qc_I = phase_demo_circuit(apply_z=False, measure_x_basis=measure_x_basis)
    qc_Z = phase_demo_circuit(apply_z=True, measure_x_basis=measure_x_basis)

    if _AER_OK:
        backend = Aer.get_backend("aer_simulator")
        tqc_I = transpile(qc_I, backend)
        tqc_Z = transpile(qc_Z, backend)
        cI = backend.run(tqc_I, shots=shots_i).result().get_counts()
        cZ = backend.run(tqc_Z, shots=shots_z).result().get_counts()
    else:
        probs_I = _counts_from_statevector(qc_I)
        probs_Z = _counts_from_statevector(qc_Z)
        cI = _sample_counts(probs_I, shots_i)
        cZ = _sample_counts(probs_Z, shots_z)

    counts = {
        "0": cI.get("0", 0) + cZ.get("0", 0),
        "1": cI.get("1", 0) + cZ.get("1", 0),
    }
    return counts, qc_I, qc_Z
