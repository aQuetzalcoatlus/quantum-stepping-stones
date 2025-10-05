import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from qec.analytics import phaseflip_mc_error, phaseflip_mixed_counts
from qec.challenges import Challenge, check_threshold
from qec.circuits import draw_circuit
from qec.codes import ThreeQubitBitFlip
from qec.decoders import lookup_decoder_3q
from qec.error_models import bsc_flip_mask

st.header("Phase-Flip via Hadamard Sandwich")

with st.expander("Learn the concept", expanded=False):
    st.markdown(r"""
### 🌱 What about phase errors?
Up to now, we've only worried about **bit flips**, which are errors that swap $\ket{0}$ and $\ket{1}$.  
But quantum systems also suffer **phase flips**, described by the Pauli-$Z$ operator:

$$ Z\ket{0} = \ket{0}, \qquad Z\ket{1} = -\ket{1}. $$

For the pure state $\ket{1}$, that minus sign is just a **global phase** (invisible on its own).  
But for a **superposition**, like

$$ \ket{+} = \tfrac{1}{\sqrt{2}}\big(\ket{0}+\ket{1}\big), $$
a $Z$ error turns it into

$$ \ket{-} = \tfrac{1}{\sqrt{2}}\big(\ket{0}-\ket{1}\big). $$

Now the relative phase between components has changed - and this is physically observable if you measure in the right basis.

---

### The trick: switch bases
If we want to treat phase flips just like bit flips, we can **rotate the basis** using Hadamards:
- Apply $H$ before the noise: $Z$ errors become $X$-like.
- Apply $H$ after the noise: rotate back.

This “H-sandwich” lets us reuse the same 3-qubit bit-flip code to also protect against phase errors.

---

### Encoding the phase-flip code
The logical states are:

$$ \ket{0_L} = \ket{+ + +}, \qquad \ket{1_L} = \ket{- - -}. $$

The stabilizers we measure are $X$-type:
- $X_1 X_2$
- $X_2 X_3$

If a single $Z$ error occurs, the syndrome identifies which qubit flipped in phase.

---

### Example
- If qubit 1 suffers a $Z$ error, the $X_1X_2$ stabilizer anticommutes and signals it.  
- If qubit 2 suffers a $Z$ error, both checks flip.  
- If qubit 3 suffers a $Z$ error, only $X_2X_3$ detects it.  

The decoder then applies $Z$ on the identified qubit to restore the logical state.

---

### Activity
To really *see* what a phase flip does, let's look at a single qubit in the lab:

1. Prepare the state $\ket{+}$.  
2. With probability $p$, apply a $Z$ error.  
3. Measure either in the **Z basis** or the **X basis**.  

- In the Z basis, the counts don't change, the phase error is invisible here.  
- In the X basis, the error flips $\ket{+}\mapsto\ket{-}$, and you'll see outcome “1” appear with probability $\approx p$.  

This small experiment shows why the H-sandwich works: it rotates phase errors into a basis where they become **measurable bit flips**.

---

### What you can do below
1. Use the sliders to set the error probability $p$ and number of shots.  
2. Run the simulation in Z basis and then X basis.  
3. Compare the bar charts and circuits to see when the phase error shows up.  

---

### Challenge
Try $p=0.3$ with 5000 shots.  
- In the Z basis: the counts barely move from 50/50.  
- In the X basis: you should see roughly 70% “0” and 30% “1”, revealing the phase flips directly.  

This activity bridges the intuition from abstract stabilizers to something you can **observe and play with**.
""")


st.subheader("Activity: Make a phase flip visible")

col_demo, col_notes = st.columns([1, 1], vertical_alignment="top")

with col_demo:
    p = st.slider(r"Phase-flip probability $p$ ($Z$ error)", 0.0, 1.0, 0.20, 0.01)
    shots = st.slider("Shots", 100, 20000, 5000, 100)

    st.markdown(r"**Measure in $Z$ basis** (computational basis)")
    if st.button(r"Run ($Z$ basis)"):
        counts, qcI, qcZ = phaseflip_mixed_counts(p, shots, measure_x_basis=False)
        dfz = pd.DataFrame.from_dict(counts, orient="index", columns=["counts"])
        st.bar_chart(dfz, use_container_width=True)
        st.caption(
            r"$Z$ basis: relative phase is hidden; counts barely reflect $Z$ errors."
        )
        st.pyplot(draw_circuit(qcI), use_container_width=True)
        st.pyplot(draw_circuit(qcZ), use_container_width=True)

    st.markdown(r"**Measure in $X$ basis** (apply $H$ then measure)")
    if st.button(r"Run ($X$ basis)"):
        counts, qcI, qcZ = phaseflip_mixed_counts(p, shots, measure_x_basis=True)
        dfx = pd.DataFrame.from_dict(counts, orient="index", columns=["counts"])
        st.bar_chart(dfx, use_container_width=True)
        st.caption(
            r"$X$ basis: $Z$ errors flip $\ket{+} \mapsto \ket{-}$, so outcome `1` appears with probability $\approx p$."
        )
        st.pyplot(draw_circuit(qcI), use_container_width=True)
        st.pyplot(draw_circuit(qcZ), use_container_width=True)

with col_notes:
    st.markdown("**What to notice**")
    st.markdown(
        r"""
        - In the **$Z$ basis**, a $Z$ error doesn't change measurement probabilities for $\ket{+}$.
        - In the **$X$ basis**, the phase becomes visible as a flip between $\ket{+}$ and $\ket{-}$.
        - This is exactly why the $H$-sandwich detects phase flips.
    """
    )
