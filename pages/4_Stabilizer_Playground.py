import streamlit as st

from qec.stabilizers import pauli_commutes, syndrome_from_pauli

st.header("Stabilizer Playground")

with st.expander("Context — commute/anticommute → syndrome signs", expanded=True):
    st.markdown(r"""
For an error $E$ and generator $g$, the measured sign flips to **−1** iff $E$ and $g$ **anticommute**.
The syndrome is the vector of these signs across generators.

Try different Pauli strings and see which checks flip.
""")

preset = st.radio("Generator set", ["Bit-flip (ZZI, IZZ)", "Phase-flip (XXI, IXX)"])
gens = ["ZZI", "IZZ"] if preset.startswith("Bit") else ["XXI", "IXX"]

P = (
    st.text_input("Error Pauli string (len=3 over I/X/Y/Z)", value="XII")
    .strip()
    .upper()
)
valid = (len(P) == 3) and all(c in {"I", "X", "Y", "Z"} for c in P)

if not valid:
    st.error("Enter 3 chars from {I,X,Y,Z}.")
else:
    st.write("Generators:", ", ".join(gens))
    comm = [pauli_commutes(P, g) for g in gens]
    syn = syndrome_from_pauli(P, gens)
    st.json(
        {
            "commutes?": {g: c for g, c in zip(gens, comm)},
            "syndrome (0→+1, 1→-1)": {g: s for g, s in zip(gens, syn)},
        }
    )
st.info(
    "Mini-exercise: find an operator that commutes with both ZZI and IZZ but isn’t a stabilizer (hint: ZZZ)."
)
