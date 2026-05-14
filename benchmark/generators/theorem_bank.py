"""Reusable theorem statements for generated reasoning traces."""

from __future__ import annotations


THEOREM_BANK = {
    "conditional_expectation_martingale_test": (
        "Use the conditional expectation martingale test: an adapted integrable process (M_n) is a "
        "martingale with respect to (F_n) if E[M_(n+1) | F_n] = M_n for every n."
    ),
    "quadratic_martingale_centered_increments": (
        "Use the quadratic martingale for centered independent increments: if S_n = S_0 + "
        "Y_1 + ... + Y_n, the increments have mean 0 and variance sigma^2, and the increments are "
        "independent of the past, then M_n = S_n^2 - n sigma^2 is a martingale."
    ),
    "exponential_martingale_discrete": (
        "Use the discrete exponential martingale: if S_n = Y_1 + ... + Y_n has independent increments "
        "and m(theta) = E[exp(theta Y_1)], then M_n = exp(theta S_n) / m(theta)^n is a martingale "
        "whenever m(theta) is finite."
    ),
    "optional_stopping_bounded": (
        "Use the bounded optional stopping theorem: if (M_n) is a martingale and tau is a bounded "
        "stopping time, then E[M_tau] = E[M_0]."
    ),
    "optional_stopping_bounded_stopped_process": (
        "Use optional stopping for a bounded stopped process: if (M_n) is a martingale and the stopped "
        "family (M_{n wedge tau}) is bounded, then E[M_tau] = E[M_0] for the finite-valued limit."
    ),
    "first_step_hitting_time_equation": (
        "Use first-step analysis for hitting times: if e_i = E_i[tau], then conditioning on the first "
        "step gives e_i = 1 + p e_(i+1) + q e_(i-1), with boundary values e_0 = e_a = 0."
    ),
    "symmetric_gambler_ruin_hitting_time": (
        "Use the symmetric gambler's ruin hitting-time formula: for a simple symmetric random walk "
        "started at i and stopped when it first hits 0 or a, E_i[tau] = i(a-i)."
    ),
}


def theorem_statement(label: str) -> str:
    """Return a reusable theorem statement by label."""
    try:
        return THEOREM_BANK[label]
    except KeyError as exc:
        raise KeyError(f"Unknown theorem label: {label}") from exc

