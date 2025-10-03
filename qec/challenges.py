from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Challenge:
    """
    A UI-free challenge spec.
    - prompt: what the learner sees
    - check: function that receives current page state and returns (ok, feedback)
    - hint: optional string
    """

    prompt: str
    check: Callable[[dict[str, Any]], tuple[bool, str]]
    hint: str | None = None


def check_threshold(
    target: float, key_rate: str = "rate"
) -> Callable[[dict], tuple[bool, str]]:
    """Pass if current 'rate' in state <= target."""

    def _check(state: dict) -> tuple[bool, str]:
        r = state.get(key_rate, None)
        if r is None:
            return False, "Run the estimator first, then try again."
        return (r <= target, rf"Your rate $ = {r:.4f}$ (target $\leq {target:.4f}$).")

    return _check


def check_smallest_n_below(
    target: float, key_curve: str = "curve"
) -> Callable[[dict], tuple[bool, str]]:
    """
    Expect state['curve'] to be list[tuple[n, rate]]. Pass if the *current* n equals
    the minimal n achieving rate ≤ target.
    """

    def _check(state: dict) -> tuple[bool, str]:
        curve = state.get(key_curve, [])
        if not curve:
            return False, "Click 'Quick sweep' first to generate the curve."
        feasible = [(n, r) for n, r in curve if r <= target]
        if not feasible:
            return False, "No n in the sweep achieves that target at current p."
        n_min = min(feasible, key=lambda x: x[0])[0]
        n_now = state.get("n", None)
        ok = n_now == n_min
        msg = rf"Smallest $n$ achieving $\leq {target:.3f}$ is $n={n_min}$. You have $n={n_now}$."
        return ok, msg

    return _check
