import numpy as np
import pandas as pd
import streamlit as st

from qec.analytics import bitflip_mc_error
from qec.challenges import Challenge, check_threshold
from qec.circuits import bitflip_encode_circuit, bitflip_syndrome_circuit, draw_circuit
from qec.codes import ThreeQubitBitFlip
from qec.decoders import lookup_decoder_3q
from qec.error_models import bsc_flip_mask

st.header("3-Qubit Bit-Flip Code")

with st.expander("Learn the concept", expanded=False):
    st.markdown(r"""
    ## Why do we need more than repetition?
    In the last activity, we saw that repeating a bit and taking the **majority vote** can protect information
    from random flips.  

    But in quantum mechanics, we don't want to just *measure* all the qubits to take a vote, as measurement would destroy the delicate quantum state.

    We need a way to **detect** which qubit flipped *without directly looking at the logical information*.

    ---

    ## The 3-qubit bit-flip code
    This is the simplest true **quantum error-correcting code**.  
    - Logical states are encoded as:
    $$ \ket{ 0_L} = \ket{000}, \qquad \ket{1_L} = \ket{111} $$           
    (See Figure 1 below for the circuit which encodes the logical qubits.)
    - If a single qubit flips (say the first becomes `1` in `100`), we want to detect it and flip it back.

    ---

    ### How can we detect an error without measuring the logical state?
    We measure **stabilizers**, which are special operators that check **parity** between pairs of qubits:
    - $Z_1 Z_2$ compares qubit 1 with 2  
    - $Z_2 Z_3$ compares qubit 2 with 3  

    If both are equal, the outcome is $+1$.  
    If they differ, the outcome is $-1$.  

    The pair of outcomes (the **syndrome**) tells us exactly *which qubit* flipped.

    ---

    ### Example
    Suppose we have $\ket{000}$
    - If qubit 1 flips (i.e., our state becomes $\ket{100}$), $Z_1Z_2$ gives: 
    
    $$Z_1 Z_2 \ket{100} = -1 \ket{100} $$, 

    $$Z_2Z_3 \ket{100} = +1 \ket{100}$$  
    - If qubit 2 flips, both report $-1$  
    - If qubit 3 flips, $Z_1Z_2$ reports $+1$, $Z_2Z_3$ reports $-1$  

    This lookup gives us a unique signature for each single-qubit error.

    ---

    ## What is the decoder?
    The **decoder** is just a small lookup table:  
    - Syndrome: “apply an $X$ gate on the identified qubit”  

    That correction returns the system to the right logical state.

    """)
    # show encoding circuit
    fig1 = draw_circuit(bitflip_encode_circuit())
    st.pyplot(fig1, width=200)
    st.caption("Figure 1: Encoding circuit for the 3-qubit bit-flip code")

    # show syndrome circuit
    fig2 = draw_circuit(bitflip_syndrome_circuit())
    st.pyplot(fig2, use_container_width=True)
    st.caption("Figure 2: Syndrome extraction circuit")

st.subheader("Interactive demo")

st.markdown("""
### 📊 What you can do below
1. Pick a qubit to inject an error on, or let the simulator flip one randomly with probability $p$.  
2. See the **syndrome** measured, and the correction applied.  
3. Estimate the **logical error rate** by running many trials — now “logical error” means
that *after correction* the decoded logical bit is still wrong.  

---

### 🚦 Challenge
Try different error rates $p$:
- Can you find values of $p$ where the logical error rate is **much smaller** than the physical error rate?  
- Can you also find values of $p$ where coding actually doesn't help (or even makes it worse)?  

This mirrors the trade-off you saw in the Repetition code — but now using the true quantum language of **stabilizers and syndromes**.
""")

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
                "Syndrome bit (0=$+1$)": syn,
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
                "syndrome (±1)": ["-1" if b == 1 else "$+1$" for b in last["syn"]],
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
