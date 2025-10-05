# pages/1_Repetition.py
import numpy as np
import pandas as pd
import streamlit as st

from qec.analytics import repetition_mc_error
from qec.challenges import Challenge, check_smallest_n_below, check_threshold

st.header("Classical Repetition Code")

# ---------- Context block ----------
with st.expander("Learn the concept", expanded=False):
    st.markdown(r"""
Information is prone to errors. Sending a "bit" of information (say `0`) through a noisy channel
can alter this bit (in this case, "flipping" to `1`), resulting in the receiver getting incorrect information.
If the probability of such a flip is high, this can significantly affect data transmission.

A simple way of tackling this issue is to introduce **redundancy**. This means you send multiple copies of the same bit
so that the receiver can "correct" errors by majority vote.  
If you intend to send `0`, you instead send `000`. If the receiver obtains `001` (or `100` or `010`),
they can still correctly decode it as `0`, because the majority of bits are `0`.  

The `000` in this process is called a **logical bit**, and the length of the code (how many times the bit is repeated) is the **code length**.
This error-correcting method is called a **repetition code**. It fails if more than **half** the bits flip.

### Logical error rate
When we add redundancy, we care about the probability that the **decoded logical bit** is wrong after applying the correction rule.
This probability is the **logical error rate**.  
For code length $n$ and physical flip probability $p$:
$$
P_\text{logical}(n,p) \;=\; \sum_{k=\lfloor n/2 \rfloor + 1}^{n} \binom{n}{k}\, p^k (1-p)^{\,n-k}.
$$

### What the sweep plot shows
Instead of checking one value of $n$, we can **sweep** across several code lengths at a fixed $p$:
- x-axis: the **code length** $n$
- y-axis: the **logical error rate** (from Monte Carlo)

Try sliding $p$:
- For **small $p$** (e.g. 0.1), increasing $n$ lowers the logical error - coding helps.
- For **large $p$** (e.g. 0.4), the curve bends upward - more redundancy can hurt (majority goes the wrong way).
""")
st.text("See the plot:")
st.image(
    "plots/classical_error_rates.png",
    caption="Logical error rate",
    # width="stretch",
    width=700,
)

st.divider()

# ---------- Layout choice ----------
layout = st.radio(
    "Layout for the two activities:",
    ["Side-by-side", "Stacked"],
    horizontal=True,
)


def activity_columns():
    if layout == "Side-by-side":
        return st.columns(2, vertical_alignment="top")
    else:
        # stacked: just yield two containers one after the other
        return st.container(), st.container()


left, right = activity_columns()

# =========================================
# ACTIVITY 1 - Point estimate at chosen (p, n)
# =========================================
with left:
    st.subheader("Activity 1 · Estimate logical error at chosen $p$ and $n$")
    st.caption(
        "Pick noise level $p$ and repetition length $n$, then run a Monte-Carlo estimate."
    )
    with st.form(key="rep_point_form", clear_on_submit=False):
        p1 = st.slider("Flip probability p", 0.0, 0.5, 0.10, 0.01, key="rep_p1")
        n1 = st.select_slider(
            "Code length n", options=[1, 3, 5, 7, 9], value=3, key="rep_n1"
        )
        trials1 = st.slider(
            "Monte-Carlo trials", 100, 100_000, 10_000, 100, key="rep_trials1"
        )
        submitted1 = st.form_submit_button("Estimate error rate")
    if submitted1:
        rate1 = repetition_mc_error(int(n1), float(p1), int(trials1))
        st.session_state["rep_point_rate"] = rate1
        st.metric("Estimated logical error", f"{rate1:.4f}")
        st.caption(
            "This is the probability that the **decoded logical bit** is wrong after majority vote."
        )

    # small challenge tied to Activity 1
    st.markdown("**Challenge A** - Hit a target now")
    targetA = st.number_input(
        r"Target error $\leq$", 0.0, 1.0, 0.05, 0.005, format="%.3f", key="rep_targetA"
    )
    chA = Challenge(
        prompt=rf"Using your current sliders, achieve error $\leq {targetA:.3f}$.",
        check=check_threshold(targetA, key_rate="rep_point_rate"),
        hint="Increase n or reduce p; then press **Estimate error rate**.",
    )
    if st.button("Check my answer (A)"):
        ok, msg = chA.check({"rep_point_rate": st.session_state.get("rep_point_rate")})
        if ok:
            st.success(msg)
            st.balloons()
        else:
            st.warning(msg)

# =========================================
# ACTIVITY 2 - Sweep over n (fixed p)
# =========================================
with right:
    st.subheader("Activity 2 · Sweep over $n$ at fixed $p$")
    st.caption(
        "Fix $p$, then compare how the logical error changes as you increase redundancy."
    )
    with st.form(key="rep_sweep_form", clear_on_submit=False):
        p2 = st.slider(
            "Flip probability p (for sweep)", 0.0, 0.5, 0.10, 0.01, key="rep_p2"
        )
        trial_per_point = st.slider(
            "Trials per point", 500, 50_000, 5_000, 500, key="rep_trials2"
        )
        ns_opts = st.multiselect(
            "n values to test",
            default=[1, 3, 5, 7, 9],
            options=[1, 3, 5, 7, 9, 11, 13],
            help="Pick which repetition lengths to include in the sweep.",
        )
        run_sweep = st.form_submit_button("Run sweep")
    if run_sweep:
        ns = np.array(sorted(set(int(x) for x in ns_opts)))
        rates = [
            repetition_mc_error(int(ni), float(p2), int(trial_per_point)) for ni in ns
        ]
        df = pd.DataFrame({"n": ns, "logical_error": rates})
        st.session_state["rep_sweep_df"] = df
        st.session_state["rep_sweep_curve"] = list(zip(ns.tolist(), rates))
        st.line_chart(df, x="n", y="logical_error", width="stretch")
        st.caption(
            "Observe when the curve goes down (coding helps) or up (coding hurts)."
        )
    elif "rep_sweep_df" in st.session_state:
        st.line_chart(
            st.session_state["rep_sweep_df"],
            x="n",
            y="logical_error",
            width="stretch",
        )

    # challenge tied to Activity 2 (smallest n below target)
    st.markdown("**Challenge B** - Find the smallest n that meets a target")
    targetB = st.number_input(
        r"Target error $\leq$ (sweep)",
        0.0,
        1.0,
        0.05,
        0.005,
        format="%.3f",
        key="rep_targetB",
    )
    chB = Challenge(
        prompt=rf"Using your last sweep at $p={p2:.2f}$, identify the **smallest** $n$ with error $\leq {targetB:.3f}$. "
        f"Then set that n in Activity 1 and verify.",
        check=check_smallest_n_below(targetB, key_curve="rep_sweep_curve"),
        hint="Run the sweep; pick the left-most n that dips below the target.",
    )
    if st.button("Check my answer (B)"):
        ok, msg = chB.check(
            {
                "rep_sweep_curve": st.session_state.get("rep_sweep_curve"),
                "n": st.session_state.get("rep_n1", None),  # what you set in Activity 1
            }
        )
        if ok:
            st.success(msg)
            st.balloons()
        else:
            st.warning(msg)

# polite footer to bridge to next page
st.divider()
st.caption(
    "Next: apply the same idea to a 3-qubit *quantum* code that corrects single bit flips using stabilizers."
)
