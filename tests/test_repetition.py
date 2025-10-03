import numpy as np

from qec.analytics import repetition_mc_error


def test_repetition_bounds():
    assert 0.0 <= repetition_mc_error(3, 0.1, 1000) <= 1.0


def test_repetition_p_zero_is_zero():
    # With p=0, no flips -> zero logical error
    assert repetition_mc_error(5, 0.0, 2000) == 0.0
