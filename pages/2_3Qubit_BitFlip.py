import numpy as np
import pandas as pd
import streamlit as st

from qec.analytics import bitflip_mc_error
from qec.challenges import Challenge, check_threshold
from qec.codes import ThreeQubitBitFlip
from qec.decoders import lookup_decoder_3q
from qec.error_models import bsc_flip_mask

st.header("3-Qubit Bit-Flip Code")

with st.expander("Context — stabilizers, syndrome, decoder", expanded=True):
    st.markdown(r"""
**Code.** $\lvert 0_L\rangle=\lvert 000\rangle,\ \lvert 1_L\rangle=\lvert 111\rangle$.
**Stabilizers.** $Z_1Z_2,\ Z_2Z_3$ define the code space (**+1** eigenvalues).  
A single-qubit $X_i$ anticommutes with the checks that involve qubit $i$, flipping their sign to **−1**.
The pair of signs (**syndrome**) identifies which $X_i$ occurred.

**Decoder.** Lookup mapping syndrome → correction ($X_1$, $X_2$, or $X_3$).  
**Distance.** $d=3$; corrects any one $X$; two $X$ can mimic the third and cause a logical flip.
""")

st.subheader("Interactive demo")
code = ThreeQubitBitFlip()

left, right = st.columns([1, 2], vertical_alignment="top")

with left:
    mode = st.radio("Error mode", ["Manual (pick a qubit)", "Random (probability p)"])
    p = st.slider("Physical X error prob p", 0.0, 0.5, 0.10, 0.01)
    trials = st.slider("Monte-Carlo trials", 100, 100_000, 10_000, 100)

    forced = np.array([0, 0, 0], dtype=int)
    if mode.startswith("Manual"):
        q = st.radio("Inject X on:", ["none", "1", "2", "3"], horizontal=True)
        if q != "none":
            forced[int(q) - 1] = 1
            e = forced
        else:
            e = bsc_flip_mask(3, p)
    else:
        e = bsc_flip_mask(3, p)

    if st.button("Run one shot"):
        syn, corr = lookup_decoder_3q(code, e)
        post = (e + corr) % 2
        decoded_bit = code.decode_majority(post)
        st.session_state["bitflip_last"] = dict(
            e=e, syn=syn, corr=corr, post=post, decoded_bit=decoded_bit
        )
        st.metric("Decoded logical bit", f"{decoded_bit}")
        # show a tidy table
        df = pd.DataFrame(
            {
                "Injected X": e,
                "Syndrome bit (0=+1)": syn,
                "Correction": corr,
                "Post-error": post,
            },
            index=["q1", "q2", "q3"],
        )
        st.dataframe(df, use_container_width=True)

    if st.button("Estimate logical error rate"):
        rate = bitflip_mc_error(p, trials)
        st.session_state["bitflip_rate"] = rate
        st.metric("Estimated logical error", f"{rate:.4f}")

with right:
    st.caption(
        "Tip: Manual single-X gives a unique syndrome; try X on q2 and watch both checks flip."
    )
    # small “what happened” panel
    last = st.session_state.get("bitflip_last")
    if last:
        st.write("Last run details:")
        st.json(
            {
                "syndrome (±1)": ["-1" if b == 1 else "+1" for b in last["syn"]],
                "correction": last["corr"].tolist(),
                "post-error": last["post"].tolist(),
            }
        )

st.subheader("Challenge")
target = st.number_input("Target logical error ≤", 0.0, 1.0, 0.05, 0.005, format="%.3f")
ch = Challenge(
    prompt=f"Achieve logical error ≤ {target:.3f} at your chosen p by tuning p/trials and verifying.",
    check=check_threshold(target, key_rate="bitflip_rate"),
    hint="Lower p or just measure more accurately; then press 'Estimate'.",
)

st.write(f"**Challenge:** {ch.prompt}")
if st.button("Check my answer"):
    ok, msg = ch.check({"bitflip_rate": st.session_state.get("bitflip_rate")})
    if ok:
        st.success(msg)
        st.balloons()
    else:
        st.warning(msg)
