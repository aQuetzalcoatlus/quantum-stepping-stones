import streamlit as st

st.set_page_config(page_title="QEC Mini-Lab", layout="wide", page_icon="🧮")
# st.title("Quantum Error Correction Mini-Lab")


def render_home():
    st.title("Quantum Error Correction — Mini-Lab")
    st.markdown("Welcome! Use the nav to open modules.")


home = st.Page(render_home, title="Home", icon=":material/home:")
repetition = st.Page(
    "pages/1_Repetition.py", title="Repetition", icon=":material/insights:"
)
bitflip = st.Page(
    "pages/2_3Qubit_BitFlip.py",
    title="3-Qubit Bit-Flip",
    icon=":material/flip_camera_android:",
)
phase = st.Page(
    "pages/3_PhaseFlip_H_Sandwich.py",
    title="Phase-Flip (H-sandwich)",
    icon=":material/gradient:",
)
stab = st.Page(
    "pages/4_Stabilizer_Playground.py",
    title="Stabilizer Playground",
    icon=":material/category:",
)

pg = st.navigation([home, repetition, bitflip, phase, stab], position="sidebar")

pg.run()
