import numpy as np
import streamlit as st

from qec.analytics import phaseflip_mc_error
from qec.challenges import Challenge, check_threshold
from qec.codes import ThreeQubitBitFlip
from qec.decoders import lookup_decoder_3q
from qec.error_models import bsc_flip_mask

st.header("Phase-Flip via Hadamard Sandwich")

with st.expander("Context — why Z looks like X in the H basis", expanded=True):
    st.markdown(r"""
**Hadamard identities.** $H Z H = X,\quad H X H = Z$.

Treat logical $\lvert +_L\rangle=\lvert +++\rangle$: a physical $Z_i$ behaves like an $X_i$ in the H-basis,
so the **same parity checks** can diagnose and correct single $Z$ errors.  
We declare a **logical phase error** if ≥2 Z remain after correction (majority logic in H-basis).
""")

st.subheader("Interactive demo")
code = ThreeQubitBitFlip()

p = st.slider("Physical Z error prob p", 0.0, 0.5, 0.10, 0.01)
trials = st.slider("Monte-Carlo trials", 100, 100_000, 10_000, 100)
mode = st.radio("Z-error mode", ["Manual (pick a qubit)", "Random"])

forcedZ = np.array([0, 0, 0], dtype=int)
if mode.startswith("Manual"):
    qz = st.radio("Inject Z on:", ["none", "1", "2", "3"], horizontal=True)
    if qz != "none":
        forcedZ[int(qz) - 1] = 1
        eZ = forcedZ
    else:
        eZ = bsc_flip_mask(3, p)
else:
    eZ = bsc_flip_mask(3, p)

if st.button("Run one shot (phase)"):
    syn, corrZ = lookup_decoder_3q(
        code, eZ
    )  # correction corresponds to Zs conceptually
    post = (eZ + corrZ) % 2
    logical_phase_error = int(post.sum() > 1)
    st.json(
        {
            "Z injected": eZ.tolist(),
            "syndrome (±1)": ["-1" if b == 1 else "+1" for b in syn],
            "Z-correction": corrZ.tolist(),
            "post-Z": post.tolist(),
            "logical phase error?": bool(logical_phase_error),
        }
    )

if st.button("Estimate logical Z error rate"):
    rate = phaseflip_mc_error(p, trials)
    st.session_state["phase_rate"] = rate
    st.metric("Estimated logical Z error", f"{rate:.4f}")

st.subheader("Challenge")
target = st.number_input(
    "Target logical phase error ≤", 0.0, 1.0, 0.05, 0.005, format="%.3f"
)
ch = Challenge(
    prompt=f"At your chosen p, make the logical Z error ≤ {target:.3f}.",
    check=check_threshold(target, key_rate="phase_rate"),
    hint="Reduce p or understand when single Z is corrected vs. double Z causing failure.",
)
st.write(f"**Challenge:** {ch.prompt}")
if st.button("Check my answer"):
    ok, msg = ch.check({"phase_rate": st.session_state.get("phase_rate")})
    if ok:
        st.success(msg)
        st.balloons()
    else:
        st.warning(msg)
