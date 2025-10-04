import streamlit as st


def render_home():
    st.title("Quantum Error Correction Lab")

    c_left, c_main, c_right = st.columns([1, 2, 1])

    with c_main:
        st.info(
            "⚠️ This lab is a **work in progress**. Content and activities may change as it develops."
        )

        st.markdown(r"""
    ### Welcome to the Quantum Error Correction Lab
    Every time we send or store information there is a chance it will get corrupted.  
    For ordinary computers this means a bit can flip from `0` to `1`.  
    We use simple tricks like parity checks and repetition to catch and fix those flips.

    In the quantum world there is more to worry about.  
    Qubits can flip between $\ket{0}$ and $\ket{1}$.  
    They can also pick up **phase** changes that are invisible if you only look in the computational basis.  
    Measuring a qubit can destroy the very information you want to protect.  
    So the question is simple. How do we keep quantum information safe without looking at it directly?

    This lab is a guided set of small experiments.  
    You will read a short idea, try an interactive activity, and then answer a tiny challenge that you can solve by adjusting the sliders.

    ---

    Think of this as an interactive textbook.
    Enjoy the experiments!
    """)

    st.divider()

    # Optional quick links to pages (works with both classic pages/ and st.Page)
    c_pad, c_links, _ = st.columns([1, 2, 1])
    with c_links:
        st.subheader("Navigation:")
        # Use page_link if on classic multipage structure.
        # Adjust targets to your actual filenames or routes.
        try:
            st.page_link("pages/1_Repetition.py", label="[1] Repetition")
            st.page_link("pages/2_3Qubit_BitFlip.py", label="[2] 3-Qubit Bit-Flip")
            st.page_link(
                "pages/3_PhaseFlip_H_Sandwich.py", label="[3] Phase-Flip (H-sandwich)"
            )
            # Keep Page 4 hidden if you removed it from navigation.
            # st.page_link("pages/4_Stabilizer_Playground.py", label="Stabilizer Playground", icon="🧩")
        except Exception:
            # If using st.Page + st.navigation, you may not need these links.
            st.caption("Use the sidebar to open modules.")


home = st.Page(render_home, title="Home", icon=":material/home:")

repetition = st.Page("pages/1_Repetition.py", title="Repetition", icon="🧱")
bitflip = st.Page("pages/2_3Qubit_BitFlip.py", title="3-Qubit Bit-Flip", icon="🎯")
phase = st.Page(
    "pages/3_PhaseFlip_H_Sandwich.py", title="Phase-Flip (H-sandwich)", icon="🎚️"
)
# stab = st.Page("pages/4_Stabilizer_Playground.py", title="Stabilizer Playground", icon="🧩")

pg = st.navigation([home, repetition, bitflip, phase], position="sidebar")
pg.run()
