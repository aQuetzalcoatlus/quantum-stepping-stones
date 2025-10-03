"""QEC Mini-Lab core package."""

from .analytics import bitflip_mc_error, phaseflip_mc_error, repetition_mc_error
from .challenges import Challenge, check_smallest_n_below, check_threshold
from .codes import ParityCheck, ThreeQubitBitFlip
from .decoders import lookup_decoder_3q
from .error_models import bsc_flip_mask
from .stabilizers import PauliLengthError, pauli_commutes, syndrome_from_pauli
