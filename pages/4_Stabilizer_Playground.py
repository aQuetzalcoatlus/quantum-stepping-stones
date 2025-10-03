import streamlit as st

from qec.stabilizers import PauliLengthError, pauli_commutes, syndrome_from_pauli

st.header("Stabilizer Playground")

with st.expander("Context — commute/anticommute → syndrome signs", expanded=True):
    st.markdown(r"""
For an error $E$ and generator $g$, the measured sign flips to **−1** iff $E$ and $g$ **anticommute**.
The syndrome is the vector of these signs across generators.
""")

preset = st.radio("Generator set", ["Bit-flip (ZZI, IZZ)", "Phase-flip (XXI, IXX)"])
gens = ["ZZI", "IZZ"] if preset.startswith("Bit") else ["XXI", "IXX"]


# --- NEW: normalize and align input ---
def normalize_pauli(s: str) -> str:
    # strip spaces and non-Pauli chars, uppercase
    return "".join(ch for ch in s.upper() if ch in "IXYZ")


raw_P = st.text_input("Error Pauli string (len must match generators)", value="XII")
P = normalize_pauli(raw_P)

# all gens should be same length; compute target length
target_len = len(gens[0])
if any(len(g) != target_len for g in gens):
    st.error("Generator set is inconsistent (different lengths). Fix the preset.")
else:
    # If user input length mismatches, auto-fix with padding/truncation and tell the user.
    if len(P) < target_len:
        st.info(f"Input shorter than {target_len}. Padding with I’s on the right.")
        P = P + "I" * (target_len - len(P))
    elif len(P) > target_len:
        st.info(
            f"Input longer than {target_len}. Truncating to first {target_len} characters."
        )
        P = P[:target_len]

    st.write("Generators:", ", ".join(gens))
    try:
        comm = [pauli_commutes(P, g) for g in gens]
        syn = syndrome_from_pauli(P, gens)
        st.json(
            {
                "Input P": P,
                "commutes?": {g: c for g, c in zip(gens, comm)},
                "syndrome (0→+1, 1→−1)": {g: s for g, s in zip(gens, syn)},
            }
        )
    except PauliLengthError as e:
        # Fallback if something still slipped through
        st.error(str(e))

st.info(
    "Mini-exercise: find an operator that commutes with both ZZI and IZZ but isn’t a stabilizer (hint: ZZZ)."
)
