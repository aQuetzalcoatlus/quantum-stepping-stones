# QEC Mini-Lab
# Pages: Home, Repetition, 3-Qubit Bit-Flip, Phase-Flip (H-sandwich), Stabilizer Playground

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# plt.style.use("ggplot")
# plt.style.use("thesis_main.mplstyle")
# plt.rcParams["text.usetex"] = True

# ----------------------------
# Global page setup
# ----------------------------
st.set_page_config(page_title="🧮 QEC Mini-Lab", page_icon="🧮", layout="wide")


def card(title: str, body: str) -> None:
    st.markdown(f"### {title}")
    st.write(body)


# ----------------------------
# Utilities
# ----------------------------
def simulate_repetition_once(n: int, p: float) -> int:
    """
    Send logical 0 as 0...0 through a BSC(p) n times, decode via majority vote.

    Returns 1 if logical error, else 0.
    """
    flips = (np.random.rand(n) < p).astype(int)
    ones = flips.sum()
    decoded = 1 if ones > n / 2 else 0
    return decoded  # error if decoded==1


def simulate_repetition(n: int = 3, p: float = 0.1, trials: int = 10000) -> float:
    errs = 0
    # vectorized batches for speed
    batch = min(trials, 10000)
    remaining = trials
    while remaining > 0:
        b = min(batch, remaining)
        flips = (np.random.rand(b, n) < p).astype(int)
        ones = flips.sum(axis=1)
        decoded = (ones > n / 2).astype(int)
        errs += decoded.sum()
        remaining -= b
    return errs / trials


# Parity-check matrix for 3-qubit bit-flip code (Z1Z2, Z2Z3)
S = np.array([[1, 1, 0], [0, 1, 1]], dtype=int)

# Lookup table: syndrome -> correction vector (which X to apply)
BITFLIP_LUT = {
    (0, 0): np.array([0, 0, 0], dtype=int),  # +1,+1 (no error)
    (1, 0): np.array([1, 0, 0], dtype=int),  # -1,+1 -> flip qubit 1
    (1, 1): np.array([0, 1, 0], dtype=int),  # -1,-1 -> flip qubit 2
    (0, 1): np.array([0, 0, 1], dtype=int),  # +1,-1 -> flip qubit 3
}


def syndrome_from_error(e: np.ndarray) -> np.ndarray:
    """Compute 2-bit syndrome (0=+1, 1=-1) as S * e (mod 2)."""
    return (S @ e) % 2


def decode_bitflip_once(p: float = 0.1, forced_error=None):
    """One trial of the 3-qubit bit-flip code.
    If forced_error is a length-3 binary array, use it instead of sampling.
    Returns a dict with everything for UI."""
    if forced_error is None:
        e = (np.random.rand(3) < p).astype(int)
    else:
        e = np.array(forced_error, dtype=int)
    syn = syndrome_from_error(e)
    corr = BITFLIP_LUT[tuple(syn.tolist())]
    e_post = (e + corr) % 2

    # Encode logical |0_L> as 000, decode by majority vote; error if decode -> 1
    decoded_bit = 1 if e_post.sum() > 1 else 0
    logical_error = decoded_bit == 1

    # Human-friendly ±1 outcomes
    pm = ["-1" if b == 1 else "+1" for b in syn]

    return {
        "e": e,
        "syn": syn,
        "pm": pm,
        "corr": corr,
        "e_post": e_post,
        "decoded_bit": decoded_bit,
        "logical_error": logical_error,
    }


def monte_carlo_bitflip(p: float, trials: int) -> float:
    """Monte-Carlo logical error rate for 3-qubit bit-flip with ideal syndrome readout."""
    errs = 0
    for _ in range(trials):
        out = decode_bitflip_once(p)
        errs += int(out["logical_error"])
    return errs / trials


# Phase-flip (H-sandwich) demo:
# We treat Z-errors with the same parity structure; correction LUT is identical in structure,
# but conceptually "apply Z on the indicated qubit". For counting a logical Z error, the
# majority of Z errors after correction ≥ 2 implies a logical phase flip on |+_L>.
def decode_phaseflip_once(p: float = 0.1, forced_error=None):
    # eZ marks Z errors on each physical qubit
    if forced_error is None:
        eZ = (np.random.rand(3) < p).astype(int)
    else:
        eZ = np.array(forced_error, dtype=int)

    syn = (S @ eZ) % 2
    corr = BITFLIP_LUT[tuple(syn.tolist())]  # but think "apply Z"
    e_post = (eZ + corr) % 2

    # Logical phase error if two or more Z remain (majority) when encoding |+_L> ~ |+ + +>
    logical_phase_error = e_post.sum() > 1
    pm = ["-1" if b == 1 else "+1" for b in syn]
    return {
        "eZ": eZ,
        "syn": syn,
        "pm": pm,
        "corrZ": corr,
        "eZ_post": e_post,
        "logical_phase_error": logical_phase_error,
    }


def monte_carlo_phaseflip(p: float, trials: int) -> float:
    errs = 0
    for _ in range(trials):
        out = decode_phaseflip_once(p)
        errs += int(out["logical_phase_error"])
    return errs / trials


# ----------------------------
# Stabilizer playground helpers
# ----------------------------
PAULI_SET = {"I", "X", "Y", "Z"}


def pauli_commutes(P: str, Q: str) -> bool:
    """Return True if P and Q commute, given equal-length Pauli strings."""
    assert len(P) == len(Q), "Pauli strings must be same length"
    anti = 0
    for a, b in zip(P, Q):
        if a == "I" or b == "I" or a == b:
            continue
        # anticommute pairs on the same qubit:
        if {a, b} in [
            {"X", "Z"},
            {"Z", "X"},
            {"X", "Y"},
            {"Y", "X"},
            {"Y", "Z"},
            {"Z", "Y"},
        ]:
            anti += 1
    return (anti % 2) == 0


def pretty_syndrome_for_error_pauli(error: str, generators: list[str]) -> list[int]:
    """Given an error Pauli string and stabilizer generators (as Pauli strings),
    predict the ±1 measurement outcomes encoded as 0(+1)/1(-1):
    outcome = -1 iff error anticommutes with the generator."""
    syn_bits = []
    for G in generators:
        syn_bits.append(0 if pauli_commutes(error, G) else 1)
    return syn_bits


# Predefined generator sets
GENS_BITFLIP = ["ZZI", "IZZ"]  # Z1Z2, Z2Z3
GENS_PHASEFLIP = ["XXI", "IXX"]  # X1X2, X2X3 (for conceptual contrast)

# ----------------------------
# Sidebar Navigation
# ----------------------------
st.sidebar.title("QEC Mini-Lab")
page = st.sidebar.radio(
    "Go to",
    [
        "Home",
        "Repetition",
        "3-Qubit Bit-Flip",
        "Phase-Flip (H-sandwich)",
        "Stabilizer Playground",
    ],
)

# ----------------------------
# Pages
# ----------------------------
if page == "Home":
    st.title("Quantum Error Correction — Simple Demonstrators")
    card(
        "What this is",
        "Interactive, minimal-math demos to build intuition for QEC: repetition, 3-qubit bit-flip, "
        "phase-flip via Hadamard sandwich, and a small stabilizer playground.",
    )
    st.markdown("""
- **Repetition:** classical majority-vote intuition.  
- **3-Qubit Bit-Flip:** stabilizers, syndromes, and lookup decoding.  
- **Phase-Flip:** treat Z errors via H-basis (conceptual H-sandwich).  
- **Stabilizer Playground:** check commutation and predict syndromes.
    """)
    st.info(
        "Tip: Use the sidebar to hop between modules. Click buttons for instant feedback."
    )

elif page == "Repetition":
    st.title("Classical Repetition Code")
    with st.sidebar:
        p = st.slider("Flip probability p", 0.0, 0.5, 0.1, 0.01)
        n = st.select_slider("Code length n", options=[1, 3, 5, 7, 9], value=3)
        trials = st.slider("Trials (Monte-Carlo)", 100, 50000, 5000, 100)

    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Simulate once"):
            err = simulate_repetition_once(n, p)
            st.metric(
                "Single trial decoded bit", "1 (error)" if err == 1 else "0 (correct)"
            )

        if st.button("Estimate error rate"):
            rate = simulate_repetition(n, p, trials)
            st.metric("Estimated logical error rate", f"{rate:.4f}")

    with c2:
        st.subheader("Error rate vs. code length (quick sweep)")
        ns = np.array([1, 3, 5, 7, 9])
        rates = [simulate_repetition(int(ni), p, max(1000, trials // 5)) for ni in ns]
        data = pd.DataFrame({"n": ns, "logical_error_rate": rates})
        st.line_chart(data, x="n", y="logical_error_rate", use_container_width=True)
        # fig = plt.figure()
        # # Override only tick label fonts
        # plt.plot(ns, rates, marker="o")
        # plt.xlabel("n (repetition length)")
        # plt.ylabel("logical error rate")
        # plt.title(rf"Repetition code at $p={p:.2f}$")
        # st.pyplot(fig, clear_figure=True)

    st.markdown(
        r"**Why it works:** majority vote corrects any $ \leq \lfloor (n-1)/2 \rfloor $ bit flips; beyond that, errors win."
    )

elif page == "3-Qubit Bit-Flip":
    st.title("3-Qubit Bit-Flip Code")
    with st.sidebar:
        mode = st.radio(
            "Error mode", ["Manual (pick a qubit)", "Random (probability p)"]
        )
        p = st.slider("Physical X error prob p", 0.0, 0.5, 0.1, 0.01)
        trials = st.slider("Trials (Monte-Carlo)", 100, 50000, 5000, 100)

    st.markdown(
        "**Stabilizers:** $Z_1Z_2$ and $Z_2Z_3$. Syndrome bits are 0→(+1), 1→(-1)."
    )

    # Manual or random one-shot
    forced = None
    if mode.startswith("Manual"):
        q = st.radio(
            "Inject X on which qubit?", ["none", "1", "2", "3"], horizontal=True
        )
        if q != "none":
            e = np.array([0, 0, 0], dtype=int)
            e[int(q) - 1] = 1
            forced = e

    if st.button("Run one shot"):
        out = decode_bitflip_once(p, forced_error=forced)
        colA, colB, colC = st.columns(3)
        with colA:
            st.write("**Injected X errors (e)**:", out["e"])
            st.write("**Syndrome (±1)**:", out["pm"])
        with colB:
            st.write("**Correction applied**:", out["corr"])
            st.write("**Post-error e'**:", out["e_post"])
        with colC:
            st.metric("Decoded logical bit", f"{out['decoded_bit']}")
            st.metric("Logical error?", "Yes" if out["logical_error"] else "No")

        st.caption("Lookup: (-1,+1)→flip q1, (-1,-1)→q2, (+1,-1)→q3.")

    if st.button("Estimate logical error rate (Monte-Carlo)"):
        rate = monte_carlo_bitflip(p, trials)
        st.metric("Estimated logical error rate", f"{rate:.4f}")

    st.markdown(
        "**Why it works:** any single X creates a unique parity pattern across $Z_1Z_2$ and $Z_2Z_3$, so a lookup decoder reverses it. Two X’s mimic the third and lead to a logical flip after correction."
    )

elif page == "Phase-Flip (H-sandwich)":
    st.title("Phase-Flip via Hadamard Sandwich")
    st.markdown(
        "Hadamard maps $Z \\leftrightarrow X$, so phase errors become bit flips in the H-basis. We reuse the same parity checks."
    )
    with st.sidebar:
        mode = st.radio(
            "Z-error mode",
            ["Manual (pick a qubit)", "Random (probability p)"],
            key="phase_mode",
        )
        pz = st.slider("Physical Z error prob p", 0.0, 0.5, 0.1, 0.01, key="phase_p")
        trials = st.slider(
            "Trials (Monte-Carlo)", 100, 50000, 5000, 100, key="phase_trials"
        )

    forcedZ = None
    if mode.startswith("Manual"):
        qz = st.radio(
            "Inject Z on which qubit?",
            ["none", "1", "2", "3"],
            horizontal=True,
            key="phase_q",
        )
        if qz != "none":
            eZ = np.array([0, 0, 0], dtype=int)
            eZ[int(qz) - 1] = 1
            forcedZ = eZ

    if st.button("Run one shot (phase)"):
        out = decode_phaseflip_once(pz, forced_error=forcedZ)
        colA, colB, colC = st.columns(3)
        with colA:
            st.write("**Injected Z errors (eZ)**:", out["eZ"])
            st.write("**Syndrome (±1)**:", out["pm"])
        with colB:
            st.write("**Z-correction applied**:", out["corrZ"])
            st.write("**Post-phase eZ'**:", out["eZ_post"])
        with colC:
            st.metric(
                "Logical phase error?", "Yes" if out["logical_phase_error"] else "No"
            )

    if st.button("Estimate logical phase error rate (Monte-Carlo)"):
        rate = monte_carlo_phaseflip(pz, trials)
        st.metric("Estimated logical Z error rate", f"{rate:.4f}")

    st.markdown(
        "**Why it works:** $H Z H = X$. Measuring Z-type stabilizers after H detects phase flips just like X flips in the bit-flip code."
    )

elif page == "Stabilizer Playground":
    st.title("Stabilizer Playground")
    st.markdown(
        "Enter a Pauli string (e.g., `XIZ`) and check commutation and predicted syndrome with chosen generators."
    )
    col1, col2 = st.columns(2)

    with col1:
        gens_choice = st.radio(
            "Generator set", ["Bit-flip (Z1Z2, Z2Z3)", "Phase-flip (X1X2, X2X3)"]
        )
        gens = GENS_BITFLIP if gens_choice.startswith("Bit") else GENS_PHASEFLIP
        st.write("**Generators:**", ", ".join(gens))
        P = (
            st.text_input("Error Pauli string (length 3, chars I/X/Y/Z):", value="XII")
            .strip()
            .upper()
        )

        valid = (len(P) == 3) and all(ch in PAULI_SET for ch in P)
        if not valid:
            st.error("Please enter a 3-character string over {I, X, Y, Z}.")
        else:
            results = []
            for G in gens:
                results.append(
                    {"G": G, "Commutes?": "✔️" if pauli_commutes(P, G) else "❌"}
                )
            st.table(results)

    with col2:
        if valid:
            syn = pretty_syndrome_for_error_pauli(P, gens)
            pm = ["-1" if b == 1 else "+1" for b in syn]
            st.write("**Predicted syndrome (±1):**", pm)
            st.caption("Outcome is -1 if the error anticommutes with the generator.")
    st.info(
        "Challenge: find a nontrivial operator that commutes with all generators but changes the logical state (a logical operator)."
    )
