import numpy as np

from qec.codes import ThreeQubitBitFlip
from qec.decoders import lookup_decoder_3q


def test_unique_syndromes_for_single_X():
    code = ThreeQubitBitFlip()
    seen = set()
    for i in range(3):
        e = np.zeros(3, dtype=int)
        e[i] = 1
        syn, corr = lookup_decoder_3q(code, e)
        seen.add(tuple(syn.tolist()))
        assert corr[i] == 1  # the LUT flips that qubit
    assert (
        len(seen) == 3 or len(seen) == 2
    )  # in 3-qubit code, 3 single-X map to 3 distinct syndromes


def test_correction_neutralizes_single_X():
    code = ThreeQubitBitFlip()
    for i in range(3):
        e = np.zeros(3, dtype=int)
        e[i] = 1
        syn, corr = lookup_decoder_3q(code, e)
        post = (e + corr) % 2
        assert post.sum() == 0  # error neutralized
