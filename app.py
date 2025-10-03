import streamlit as st

st.set_page_config(page_title="QEC Mini-Lab", layout="wide")
st.title("Quantum Error Correction Mini-Lab")

st.markdown("""
Welcome! Use the sidebar to open modules.  
Each page includes: **Context**, **Interactive Demo**, and **Challenge** tied to the sliders/buttons.
""")

st.divider()
st.markdown("""
**Modules**
- Repetition (classical)
- 3-Qubit Bit-Flip
- Phase-Flip (H-sandwich)
- Stabilizer Playground
""")
st.info("Tip: Solve the challenge by manipulating the controls.")
