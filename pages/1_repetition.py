import numpy as np
import pandas as pd
import streamlit as st

from qec.analytics import repetition_mc_error
from qec.challenges import Challenge, check_smallest_n_below, check_threshold

st.header("Classical Repetition Code")

with st.expander("Context (what’s going on) — click to read", expanded=True):
    st.markdown(r"""
**Idea.** Send one bit through $n$ independent noisy channels (flip prob $p$), then decode by **majority vote**.  
A logical error occurs if more than half the bits flipped.

**Key expression.**

$$ P_\text{logical}(n,p)=\sum_{k=\lfloor n/2\rfloor+1}^{n} \binom{n}{k} p^k(1-p)^{n-k}. $$
                
For $p<0.5$, increasing $n$ initially reduces error; for $p>0.5$, coding hurts.
""")

st.subheader("Interactive demo")
left, right = st.columns([1, 2], vertical_alignment="top")

with left:
    p = st.slider("Flip probability p", 0.0, 0.5, 0.10, 0.01)
    n = st.select_slider("Code length n", options=[1, 3, 5, 7, 9], value=3)
    trials = st.slider("Monte-Carlo trials", 100, 100_000, 10_000, 100)
    if st.button("Estimate error rate"):
        rate = repetition_mc_error(n, p, trials)
        st.session_state["repetition_rate"] = rate
        st.metric("Estimated logical error", f"{rate:.4f}")

with right:
    if st.button("Quick sweep over n"):
        ns = np.array([1, 3, 5, 7, 9])
        rates = [repetition_mc_error(int(ni), p, max(2000, trials // 5)) for ni in ns]
        curve_df = pd.DataFrame({"n": ns, "logical_error": rates})
        st.session_state["repetition_curve"] = list(zip(ns.tolist(), rates))
        st.session_state["n"] = n
        st.line_chart(curve_df, x="n", y="logical_error", use_container_width=True)
    elif "repetition_curve" in st.session_state:
        # display last sweep if available
        ns, rs = zip(*st.session_state["repetition_curve"])
        st.line_chart(
            pd.DataFrame({"n": ns, "logical_error": rs}),
            x="n",
            y="logical_error",
            use_container_width=True,
        )

st.subheader("Challenge")
target = st.number_input(
    "Target logical error ≤",
    min_value=0.0,
    max_value=1.0,
    value=0.05,
    step=0.005,
    format="%.3f",
)
challenge = st.radio(
    "Pick a challenge",
    ["Hit the target now", "Find the smallest n achieving target (use sweep)"],
)

if challenge == "Hit the target now":
    ch = Challenge(
        prompt=f"Using your current sliders, achieve error ≤ {target:.3f}.",
        check=check_threshold(target, key_rate="repetition_rate"),
        hint="Increase n or reduce p; then click 'Estimate error rate'.",
    )
else:
    ch = Challenge(
        prompt=f"Find the **smallest** n that achieves error ≤ {target:.3f} at current p. (Run 'Quick sweep' and then set n.)",
        check=check_smallest_n_below(target, key_curve="repetition_curve"),
        hint="Run the sweep; set n to the minimal one that dips below target.",
    )

st.write(f"**Challenge:** {ch.prompt}")
if st.button("Check my answer"):
    ok, msg = ch.check(
        {
            "repetition_rate": st.session_state.get("repetition_rate"),
            "repetition_curve": st.session_state.get("repetition_curve"),
            "n": n,
        }
    )
    if ok:
        st.success(msg)
        st.balloons()
    else:
        st.warning(msg)
