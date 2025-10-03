import numpy as np
import streamlit as st

from qec.analytics import phaseflip_mc_error
from qec.challenges import Challenge, check_threshold
from qec.codes import ThreeQubitBitFlip
from qec.decoders import lookup_decoder_3q
from qec.error_models import bsc_flip_mask

st.header("Phase-Flip via Hadamard Sandwich")

with st.expander("Learn the concept", expanded=True):
    st.markdown(r"""
### 🌱 What about phase errors?
So far, we've learned how to protect against **bit-flip errors**: when a qubit jumps from `|0⟩` to `|1⟩` or vice versa.  
But in quantum systems, there's another type of error: the **phase flip**.  

A phase flip changes the relative sign:

$$ \ket{+} \longrightarrow \ket{-} $$

while leaving `|0⟩` and `|1⟩` untouched.
This error is invisible in the computational basis, but it scrambles superpositions.

---

### 💡 The trick: switch bases
We can turn a phase flip into a bit flip by moving to the **Hadamard basis**.  
- Apply $H$ before the error → phase flips look like bit flips.  
- Apply $H$ again afterwards → we return to the original basis.

This "H-sandwich" lets us reuse the **3-qubit bit-flip code** to correct phase errors!

---

### 🔍 Encoding the phase-flip code
The logical states are:
$$ \ket{0_L} = \ket{+\,+\,+}, \qquad \ket{1_L} = \ket{-\, -\, -} $$
so each logical qubit is protected against a single phase flip.

The stabilizers we measure are now in the $X$ basis:
- $X_1 X_2$  
- $X_2 X_3$

---

### 🧩 Example
- If qubit 1 suffers a $Z$ error, the syndrome pattern matches uniquely.  
- The decoder applies $Z$ on that qubit to fix it.  

Just like the bit-flip code — but rotated into the Hadamard basis.

---

### 📊 What you can do below
1. Pick a qubit to flip its **phase** (apply $Z$), or let random errors occur with probability $p$.  
2. See the stabilizer outcomes and the correction applied.  
3. Run many trials and estimate the **logical error rate**.  

---

### 🚦 Challenge
Experiment with different $p$:  
- At small $p$, does the logical error become much smaller than $p$?  
- At larger $p$, does the coding help, or can it make things worse?  

This mirrors the same trade-off as before — now with **phase errors instead of bit flips**.
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
