"""Build larger algorithmic-scaffold train/validation variants."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.generators.hitting_time_expectation import HittingTimeExpectationGenerator
from benchmark.generators.martingale_verification import MartingaleVerificationGenerator
from benchmark.generators.optional_stopping_validity import OptionalStoppingValidityGenerator
from benchmark.generators.stopped_process_expectation import StoppedProcessExpectationGenerator


DATA_ROOT = PROJECT_ROOT / "benchmark" / "data"

TRAIN_COUNTS = {
    "hitting_time_expectation": 1200,
    "stopped_process_expectation": 1200,
    "martingale_verification": 400,
    "optional_stopping_validity": 400,
}

TRAIN_TYPE_COUNTS_V2 = {
    "hitting_time_expectation": {
        "symmetric_boundaries_zero_a": 450,
        "symmetric_shifted_boundaries": 450,
        "biased_boundaries_zero_a": 900,
    },
    "stopped_process_expectation": {
        "bounded_walk_expectation": 500,
        "quadratic_fixed_horizon": 700,
        "stopped_martingale_value": 500,
    },
    "martingale_verification": {
        "centered_walk_basic": 120,
        "quadratic_compensation": 200,
        "exponential_compensation": 120,
    },
    "optional_stopping_validity": {
        "bounded_time_valid": 120,
        "unbounded_first_hit_invalid": 220,
        "finite_state_hitting_valid": 120,
    },
}

TRAIN_TYPE_COUNTS_V2_5 = {
    "hitting_time_expectation": {
        "symmetric_boundaries_zero_a": 350,
        "symmetric_shifted_boundaries": 350,
        "biased_boundaries_zero_a": 1200,
    },
    "stopped_process_expectation": {
        "bounded_walk_expectation": 500,
        "quadratic_fixed_horizon": 700,
        "stopped_martingale_value": 500,
    },
    "martingale_verification": {
        "centered_walk_basic": 100,
        "quadratic_compensation": 180,
        "exponential_compensation": 120,
    },
    "optional_stopping_validity": {
        "bounded_time_valid": 100,
        "unbounded_first_hit_invalid": 200,
        "finite_state_hitting_valid": 100,
    },
}

TRAIN_TYPE_COUNTS_V3 = TRAIN_TYPE_COUNTS_V2

TRAIN_TYPE_COUNTS_V3_1 = {
    "hitting_time_expectation": {
        "symmetric_boundaries_zero_a": 1000,
        "symmetric_shifted_boundaries": 1000,
        "biased_boundaries_zero_a": 1800,
    },
    "stopped_process_expectation": {
        "bounded_walk_expectation": 1000,
        "quadratic_fixed_horizon": 1600,
        "stopped_martingale_value": 1200,
    },
    "martingale_verification": {
        "centered_walk_basic": 250,
        "quadratic_compensation": 550,
        "exponential_compensation": 350,
    },
    "optional_stopping_validity": {
        "bounded_time_valid": 300,
        "unbounded_first_hit_invalid": 650,
        "finite_state_hitting_valid": 300,
    },
}

TRAIN_TYPE_COUNTS_V3_5 = TRAIN_TYPE_COUNTS_V3_1

GENERATORS = {
    "hitting_time_expectation": HittingTimeExpectationGenerator(),
    "stopped_process_expectation": StoppedProcessExpectationGenerator(),
    "martingale_verification": MartingaleVerificationGenerator(),
    "optional_stopping_validity": OptionalStoppingValidityGenerator(),
}


def as_fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def final_answer(answer: dict[str, Any]) -> str:
    return "Final answer:\n<answer>\n" + json.dumps(answer, sort_keys=True) + "\n</answer>"


def answer_type(answer: dict[str, Any]) -> str:
    if answer and all(isinstance(value, bool) for value in answer.values()):
        return "binary"
    return "non_binary"


def make_record_from_params(generator: Any, params: dict[str, Any], split: str, seed: int) -> dict[str, Any]:
    solution = generator.generate_solution(params)
    return {
        "id": generator.make_id(split=split, seed=seed),
        "family": generator.family,
        "problem_type": params["problem_type"],
        "answer_type": answer_type(solution),
        "difficulty": params["difficulty"],
        "split": split,
        "seed": seed,
        "params": generator.to_json_safe(params),
        "problem": generator.generate_problem(params),
        "reasoning": generator.generate_reasoning(params),
        "canonical_answer": generator.to_json_safe(solution),
        "metadata": generator.to_json_safe(generator.generate_metadata(params)),
    }


def hitting_time_reasoning(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    problem_type = record["problem_type"]
    lower = params["lower"]
    upper = params["upper"]
    start = params["start"]

    if problem_type in {"symmetric_boundaries_zero_a", "symmetric_shifted_boundaries"}:
        left_gap = start - lower
        right_gap = upper - start
        return (
            "Step 1: Identify the task.\n"
            "This is a finite-interval hitting-time expectation for a simple symmetric random walk.\n\n"
            "Step 2: Extract the parameters.\n"
            f"Lower boundary a = {lower}; upper boundary b = {upper}; starting point x = {start}.\n\n"
            "Step 3: Select the formula.\n"
            "For a simple symmetric random walk stopped on hitting a or b,\n"
            "E_x[tau] = (x-a)(b-x).\n\n"
            "Step 4: Substitute and simplify.\n"
            f"x-a = {start}-{lower} = {left_gap}.\n"
            f"b-x = {upper}-{start} = {right_gap}.\n"
            f"E_x[tau] = ({left_gap})({right_gap}) = {answer['expected_time']}.\n\n"
            + final_answer(answer)
        )

    p = as_fraction(params["p"])
    q = as_fraction(params["q"])
    r = q / p
    r_start = r**start
    r_upper = r**upper
    weighted_boundary = Fraction(upper, 1) * (r_start - 1) / (r_upper - 1)
    expectation = (weighted_boundary - start) / (p - q)

    return (
        "Step 1: Identify the task.\n"
        "This is a finite-interval hitting-time expectation for a biased nearest-neighbor walk.\n\n"
        "Step 2: Extract the parameters.\n"
        f"Lower boundary a = {lower}; upper boundary b = {upper}; starting point x = {start}.\n"
        f"Up probability p = {p}; down probability q = {q}; ratio r = q/p = {r}.\n\n"
        "Step 3: Select the formula.\n"
        "For p != q and tau = inf{n >= 0 : X_n in {0,b}},\n"
        "E_x[tau] = (b((q/p)^x - 1)/((q/p)^b - 1) - x)/(p-q).\n\n"
        "Step 4: Substitute and simplify.\n"
        f"r^x = ({r})^{start} = {r_start}.\n"
        f"r^b = ({r})^{upper} = {r_upper}.\n"
        f"b(r^x - 1)/(r^b - 1) = {weighted_boundary}.\n"
        f"E_x[tau] = ({weighted_boundary} - {start})/({p} - {q}) = {expectation}.\n\n"
        "Step 5: Return the canonical JSON answer.\n"
        + final_answer(answer)
    )


def stopped_process_reasoning(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    problem_type = record["problem_type"]
    start = params["start"]
    symbol = params["process_notation"]

    if problem_type == "bounded_walk_expectation":
        horizon = params["horizon"]
        level = params["level"]
        return (
            "Step 1: Identify the task.\n"
            "This asks for the expectation of a bounded stopped simple symmetric random walk.\n\n"
            "Step 2: Extract the parameters.\n"
            f"{symbol}_0 = {start}; target level = {level}; deterministic cap = {horizon}.\n"
            f"The stopping time is tau = min(T, {horizon}), so tau is bounded.\n\n"
            "Step 3: Select the martingale relation.\n"
            f"({symbol}_n) is a martingale, so optional stopping gives E[{symbol}_tau] = E[{symbol}_0].\n\n"
            "Step 4: Substitute and simplify.\n"
            f"E[{symbol}_tau] = E[{symbol}_0] = {start}.\n\n"
            + final_answer(answer)
        )

    if problem_type == "quadratic_fixed_horizon":
        horizon = params["horizon"]
        variance = params["variance"]
        step = params["step"]
        value = start * start + horizon * variance
        return (
            "Step 1: Identify the task.\n"
            "This asks for the second moment of a centered independent-increment walk at a fixed time.\n\n"
            "Step 2: Extract the parameters.\n"
            f"{symbol}_0 = {start}; n = {horizon}; increments are +/-{step}; Var(Y_k) = {variance}.\n\n"
            "Step 3: Select the formula.\n"
            f"For centered independent increments, E[{symbol}_n^2] = {symbol}_0^2 + n Var(Y_1).\n\n"
            "Step 4: Substitute and simplify.\n"
            f"E[{symbol}_{horizon}^2] = ({start})^2 + {horizon}({variance}) = {value}.\n\n"
            + final_answer(answer)
        )

    horizon = params["horizon"]
    level = params["level"]
    value = start * start
    return (
        "Step 1: Identify the task.\n"
        "This asks for the expectation of a stopped quadratic martingale.\n\n"
        "Step 2: Extract the parameters.\n"
        f"{symbol}_0 = {start}; target level = {level}; deterministic cap = {horizon}.\n"
        f"The stopping time tau = min(T, {horizon}) is bounded.\n\n"
        "Step 3: Select the martingale relation.\n"
        f"For a simple symmetric random walk, M_n = {symbol}_n^2 - n is a martingale.\n"
        f"Optional stopping gives E[{symbol}_tau^2 - tau] = E[M_tau] = E[M_0].\n\n"
        "Step 4: Substitute and simplify.\n"
        f"M_0 = {symbol}_0^2 - 0 = ({start})^2 = {value}.\n\n"
        + final_answer(answer)
    )


def martingale_reasoning(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    problem_type = record["problem_type"]
    result = str(answer["is_martingale"]).lower()
    symbol = params["process_notation"]

    if problem_type == "centered_walk_basic":
        step = params["step"]
        return (
            "Step 1: Identify the martingale test.\n"
            f"Check whether E[{symbol}_(n+1) | F_n] = {symbol}_n.\n\n"
            "Step 2: Compute the conditional increment mean.\n"
            f"The next increment is +{step} or -{step} with equal probability, so its mean is 0.\n\n"
            "Step 3: Conclude.\n"
            f"E[{symbol}_(n+1) | F_n] = {symbol}_n + 0 = {symbol}_n, so is_martingale = {result}.\n\n"
            + final_answer(answer)
        )

    if problem_type == "quadratic_compensation":
        variance = params["variance"]
        compensation = params["compensation"]
        verdict = "matches" if answer["is_martingale"] else "does not match"
        return (
            "Step 1: Identify the required compensation.\n"
            f"For a centered walk, {symbol}_n^2 - c n is a martingale exactly when c = Var(Y_1).\n\n"
            "Step 2: Extract and compare.\n"
            f"Var(Y_1) = {variance}; proposed c = {compensation}; proposed c {verdict} the variance.\n\n"
            "Step 3: Conclude.\n"
            f"is_martingale = {result}.\n\n"
            + final_answer(answer)
        )

    p = params["p"]
    q = params["q"]
    theta = params["theta_name"]
    denominator = params["denominator"]
    return (
        "Step 1: Identify the required exponential compensation.\n"
        "The denominator must equal the one-step moment generating factor.\n\n"
        "Step 2: Compute the required factor.\n"
        f"E[exp({theta} Y)] = {p} exp({theta}) + {q} exp(-{theta}).\n\n"
        "Step 3: Compare with the proposed denominator.\n"
        f"Proposed denominator: {denominator}.\n\n"
        "Step 4: Conclude.\n"
        f"is_martingale = {result}.\n\n"
        + final_answer(answer)
    )


def optional_stopping_reasoning(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    condition = params["condition"]
    result = str(answer["valid"]).lower()

    if condition == "bounded":
        check = "tau is explicitly capped by a deterministic horizon, so tau is bounded"
    elif condition == "finite_state":
        check = "the stopped/absorbed process is finite-state, so the stopped process is bounded"
    else:
        check = "tau is an unbounded first-hitting time, and no extra integrability condition is given"

    return (
        "Step 1: Identify the optional-stopping issue.\n"
        "Before using E[M_tau] = E[M_0], check the stopping-time hypotheses.\n\n"
        "Step 2: Check the condition in this problem.\n"
        f"{check}.\n\n"
        "Step 3: Conclude.\n"
        f"valid = {result}.\n\n"
        + final_answer(answer)
    )


def hitting_time_reasoning_v2(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    lower = params["lower"]
    upper = params["upper"]
    start = params["start"]

    if record["problem_type"] in {"symmetric_boundaries_zero_a", "symmetric_shifted_boundaries"}:
        left_gap = start - lower
        right_gap = upper - start
        return (
            "Step 1: Identify the walk type.\n"
            "The walk is simple symmetric, so p = q = 1/2. Use the symmetric finite-interval formula.\n\n"
            "Step 2: Extract the interval parameters.\n"
            f"Lower boundary a = {lower}; upper boundary b = {upper}; start x = {start}.\n\n"
            "Step 3: Select the formula.\n"
            "For the symmetric walk, E_x[tau] = (x-a)(b-x).\n\n"
            "Step 4: Compute each factor.\n"
            f"x-a = {start} - ({lower}) = {left_gap}.\n"
            f"b-x = {upper} - ({start}) = {right_gap}.\n\n"
            "Step 5: Multiply.\n"
            f"E_x[tau] = {left_gap} * {right_gap} = {answer['expected_time']}.\n\n"
            + final_answer(answer)
        )

    p = as_fraction(params["p"])
    q = as_fraction(params["q"])
    r = q / p
    r_start = r**start
    r_upper = r**upper
    numerator_piece = r_start - 1
    denominator_piece = r_upper - 1
    boundary_piece = Fraction(upper, 1) * numerator_piece / denominator_piece
    drift = p - q
    expectation = (boundary_piece - start) / drift

    return (
        "Step 1: Identify the walk type.\n"
        f"Here p = {p} and q = {q}. Since p != q, the walk is biased.\n"
        "Do not use the symmetric formula E_x[tau] = (x-a)(b-x).\n\n"
        "Step 2: Extract the interval parameters.\n"
        f"Lower boundary a = {lower}; upper boundary b = {upper}; start x = {start}.\n\n"
        "Step 3: Select the biased formula.\n"
        "For tau = inf{n >= 0 : X_n in {0,b}} and p != q,\n"
        "E_x[tau] = (b((q/p)^x - 1)/((q/p)^b - 1) - x)/(p-q).\n\n"
        "Step 4: Compute the ratio powers.\n"
        f"q/p = ({q})/({p}) = {r}.\n"
        f"(q/p)^x = ({r})^{start} = {r_start}.\n"
        f"(q/p)^b = ({r})^{upper} = {r_upper}.\n\n"
        "Step 5: Compute the boundary term.\n"
        f"(q/p)^x - 1 = {numerator_piece}.\n"
        f"(q/p)^b - 1 = {denominator_piece}.\n"
        f"b((q/p)^x - 1)/((q/p)^b - 1) = {upper} * {numerator_piece}/{denominator_piece} = {boundary_piece}.\n\n"
        "Step 6: Finish the expectation.\n"
        f"p-q = {p} - {q} = {drift}.\n"
        f"E_x[tau] = ({boundary_piece} - {start})/({drift}) = {expectation}.\n\n"
        + final_answer(answer)
    )


def stopped_process_reasoning_v2(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    problem_type = record["problem_type"]
    start = params["start"]
    symbol = params["process_notation"]

    if problem_type == "bounded_walk_expectation":
        horizon = params["horizon"]
        level = params["level"]
        return (
            "Step 1: Identify the stopped process.\n"
            f"The process is the simple symmetric random walk ({symbol}_n), and tau = min(T, {horizon}).\n"
            "Because tau has a deterministic cap, tau is bounded.\n\n"
            "Step 2: Extract the starting value.\n"
            f"{symbol}_0 = {start}. The target level {level} does not change the optional-stopping value.\n\n"
            "Step 3: Apply optional stopping directly.\n"
            f"E[{symbol}_tau] = E[{symbol}_0] = {start}.\n\n"
            + final_answer(answer)
        )

    if problem_type == "quadratic_fixed_horizon":
        horizon = params["horizon"]
        variance = params["variance"]
        step = params["step"]
        start_square = start * start
        variance_term = horizon * variance
        total = start_square + variance_term
        return (
            "Step 1: Identify the fixed-time second-moment task.\n"
            f"We need E[{symbol}_{horizon}^2] for a centered independent-increment walk.\n\n"
            "Step 2: Extract the parameters.\n"
            f"{symbol}_0 = {start}; n = {horizon}; increments are +{step} or -{step} with probability 1/2 each.\n"
            f"The variance of one increment is sigma^2 = ({step})^2 = {variance}.\n\n"
            "Step 3: Select the formula.\n"
            f"E[{symbol}_n^2] = {symbol}_0^2 + n sigma^2.\n\n"
            "Step 4: Do the arithmetic in small pieces.\n"
            f"{symbol}_0^2 = ({start})^2 = {start_square}.\n"
            f"n sigma^2 = {horizon} * {variance} = {variance_term}.\n"
            f"Total = {start_square} + {variance_term} = {total}.\n\n"
            + final_answer(answer)
        )

    horizon = params["horizon"]
    level = params["level"]
    start_square = start * start
    return (
        "Step 1: Identify the stopped quadratic martingale task.\n"
        f"The requested expression is E[{symbol}_tau^2 - tau]. Do not compute E[{symbol}_tau^2] and E[tau] separately.\n\n"
        "Step 2: Extract the bounded stopping time.\n"
        f"{symbol}_0 = {start}; target level = {level}; tau = min(T, {horizon}).\n"
        f"Since tau is capped by {horizon}, optional stopping applies.\n\n"
        "Step 3: Use the martingale directly.\n"
        f"For a simple symmetric random walk, M_n = {symbol}_n^2 - n is a martingale.\n"
        f"Therefore E[{symbol}_tau^2 - tau] = E[M_tau] = E[M_0].\n\n"
        "Step 4: Compute M_0.\n"
        f"M_0 = {symbol}_0^2 - 0 = ({start})^2 = {start_square}.\n\n"
        + final_answer(answer)
    )


REASONING_BUILDERS_V2 = {
    "hitting_time_expectation": hitting_time_reasoning_v2,
    "stopped_process_expectation": stopped_process_reasoning_v2,
    "martingale_verification": martingale_reasoning,
    "optional_stopping_validity": optional_stopping_reasoning,
}


def hitting_time_reasoning_v2_5(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    lower = params["lower"]
    upper = params["upper"]
    start = params["start"]

    if record["problem_type"] in {"symmetric_boundaries_zero_a", "symmetric_shifted_boundaries"}:
        return hitting_time_reasoning_v2(record)

    p = as_fraction(params["p"])
    q = as_fraction(params["q"])
    r = q / p
    r_start = r**start
    r_upper = r**upper
    hit_upper_probability = (1 - r_start) / (1 - r_upper)
    terminal_expectation = Fraction(upper, 1) * hit_upper_probability
    drift = p - q
    expected_time = (terminal_expectation - start) / drift

    return (
        "Step 1: Identify the walk type.\n"
        f"Here p = {p} and q = {q}. Since p != q, this is a biased walk.\n"
        "Do not use the symmetric formula E_x[tau] = (x-a)(b-x).\n\n"
        "Step 2: Extract the interval parameters.\n"
        f"The lower boundary is 0, the upper boundary is b = {upper}, and the start is x = {start}.\n\n"
        "Step 3: Compute the probability of hitting the upper boundary.\n"
        "For a biased walk on {0,...,b}, with r = q/p,\n"
        "P_x(hit b before 0) = (1-r^x)/(1-r^b).\n"
        f"r = q/p = ({q})/({p}) = {r}.\n"
        f"r^x = ({r})^{start} = {r_start}.\n"
        f"r^b = ({r})^{upper} = {r_upper}.\n"
        f"P_x(hit b before 0) = (1 - {r_start})/(1 - {r_upper}) = {hit_upper_probability}.\n\n"
        "Step 4: Convert this to the expected terminal position.\n"
        f"At time tau, X_tau is either 0 or {upper}.\n"
        f"E[X_tau] = 0 * (1 - {hit_upper_probability}) + {upper} * {hit_upper_probability} = {terminal_expectation}.\n\n"
        "Step 5: Use the drift martingale to get E[tau].\n"
        "For this walk, X_n - (p-q)n is a martingale, so E[X_tau] - (p-q)E[tau] = x.\n"
        "Rearrange: E[tau] = (E[X_tau] - x)/(p-q).\n"
        f"p-q = {p} - {q} = {drift}.\n"
        f"E[tau] = ({terminal_expectation} - {start})/({drift}) = {expected_time}.\n\n"
        + final_answer(answer)
    )


REASONING_BUILDERS_V2_5 = {
    "hitting_time_expectation": hitting_time_reasoning_v2_5,
    "stopped_process_expectation": stopped_process_reasoning_v2,
    "martingale_verification": martingale_reasoning,
    "optional_stopping_validity": optional_stopping_reasoning,
}


def hitting_time_reasoning_v3(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    lower = params["lower"]
    upper = params["upper"]
    start = params["start"]

    if record["problem_type"] in {"symmetric_boundaries_zero_a", "symmetric_shifted_boundaries"}:
        return hitting_time_reasoning_v2(record)

    p = as_fraction(params["p"])
    q = as_fraction(params["q"])
    r = q / p
    r_start = r**start
    r_upper = r**upper
    numerator_piece = r_start - 1
    denominator_piece = r_upper - 1
    boundary_piece = Fraction(upper, 1) * numerator_piece / denominator_piece
    drift = p - q
    expectation = (boundary_piece - start) / drift

    return (
        "Step 1: Classify the walk before choosing a formula.\n"
        f"The up probability is p = {p} and the down probability is q = {q}. Since p != q, this is biased.\n"
        "Therefore the symmetric formula (x-a)(b-x) is not allowed.\n\n"
        "Step 2: Extract the finite interval.\n"
        f"Lower boundary a = {lower}; upper boundary b = {upper}; start x = {start}.\n\n"
        "Step 3: Use exactly the biased finite-interval expectation formula.\n"
        "For boundaries 0 and b, with r = q/p,\n"
        "E_x[tau] = (b(r^x - 1)/(r^b - 1) - x)/(p-q).\n\n"
        "Step 4: Compute the ratio terms.\n"
        f"r = q/p = ({q})/({p}) = {r}.\n"
        f"r^x = ({r})^{start} = {r_start}.\n"
        f"r^b = ({r})^{upper} = {r_upper}.\n\n"
        "Step 5: Compute the boundary term.\n"
        f"r^x - 1 = {numerator_piece}.\n"
        f"r^b - 1 = {denominator_piece}.\n"
        f"b(r^x - 1)/(r^b - 1) = {upper} * {numerator_piece}/{denominator_piece} = {boundary_piece}.\n\n"
        "Step 6: Divide by the drift.\n"
        f"p-q = {p} - {q} = {drift}.\n"
        f"E_x[tau] = ({boundary_piece} - {start})/({drift}) = {expectation}.\n\n"
        "Step 7: Return only the requested JSON object.\n"
        + final_answer(answer)
    )


def martingale_reasoning_v3(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    problem_type = record["problem_type"]
    result = str(answer["is_martingale"]).lower()
    symbol = params["process_notation"]

    if problem_type == "quadratic_compensation":
        variance = params["variance"]
        compensation = params["compensation"]
        if answer["is_martingale"]:
            comparison = f"proposed c = {compensation}, which equals Var(Y_1) = {variance}"
        else:
            comparison = f"proposed c = {compensation}, which is not equal to Var(Y_1) = {variance}"
        return (
            "Step 1: Use the quadratic martingale checklist.\n"
            f"For a centered independent-increment walk, {symbol}_n^2 - c n is a martingale exactly when c = Var(Y_1).\n\n"
            "Step 2: Extract the one-step variance from the problem statement.\n"
            f"Here Var(Y_1) = {variance}. Do not default to c = 1 or c = 2 unless the variance says so.\n\n"
            "Step 3: Compare the proposed compensation with the variance.\n"
            f"{comparison}.\n\n"
            "Step 4: Conclude from the comparison.\n"
            f"is_martingale = {result}.\n\n"
            + final_answer(answer)
        )

    if problem_type == "exponential_compensation":
        p = params["p"]
        q = params["q"]
        theta = params["theta_name"]
        denominator = params["denominator"]
        if answer["is_martingale"]:
            comparison = "matches"
        else:
            comparison = "does not match"
        return (
            "Step 1: Use the one-step exponential martingale checklist.\n"
            "Do not expand the whole product. Only compare the denominator factor with the one-step moment factor.\n\n"
            "Step 2: Compute the required one-step factor.\n"
            f"E[exp({theta} Y_1)] = {p} exp({theta}) + {q} exp(-{theta}).\n\n"
            "Step 3: Compare with the proposed denominator factor.\n"
            f"Proposed denominator factor: {denominator}.\n"
            f"The proposed factor {comparison} the required factor.\n\n"
            "Step 4: Conclude from the comparison.\n"
            f"is_martingale = {result}.\n\n"
            + final_answer(answer)
        )

    return martingale_reasoning(record)


def optional_stopping_reasoning_v3(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    condition = params["condition"]
    result = str(answer["valid"]).lower()

    if condition == "bounded":
        check = "tau is capped by a deterministic horizon, so tau is bounded"
        rule = "bounded stopping time"
    elif condition == "finite_state":
        check = "the stopped/absorbed process takes values in a finite state space, so the stopped process is bounded"
        rule = "finite-state bounded stopped process"
    else:
        check = "tau is an uncapped first-hitting time, and no integrability or boundedness condition is supplied"
        rule = "missing optional-stopping hypothesis"

    return (
        "Step 1: Check the optional-stopping hypothesis before using E[M_tau] = E[M_0].\n"
        f"The relevant condition is: {check}.\n\n"
        "Step 2: Apply the rule.\n"
        f"This is a {rule} case.\n\n"
        "Step 3: Conclude with the exact required schema.\n"
        f"valid = {result}.\n\n"
        + final_answer(answer)
    )


REASONING_BUILDERS_V3 = {
    "hitting_time_expectation": hitting_time_reasoning_v3,
    "stopped_process_expectation": stopped_process_reasoning_v2,
    "martingale_verification": martingale_reasoning_v3,
    "optional_stopping_validity": optional_stopping_reasoning_v3,
}


def hitting_time_reasoning_v3_5(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    lower = params["lower"]
    upper = params["upper"]
    start = params["start"]

    if record["problem_type"] in {"symmetric_boundaries_zero_a", "symmetric_shifted_boundaries"}:
        return hitting_time_reasoning_v2(record)

    p = as_fraction(params["p"])
    q = as_fraction(params["q"])
    r = q / p
    r_x = r**start
    r_b = r**upper
    numerator = r_x - 1
    denominator = r_b - 1
    ratio = numerator / denominator
    boundary_term = Fraction(upper, 1) * ratio
    drift = p - q
    shifted_value = boundary_term - start
    expectation = shifted_value / drift

    return (
        "Step 1: Classify the walk and choose the biased pipeline.\n"
        f"p = {p}, q = {q}, and p != q, so this is biased. Do not use (x-a)(b-x).\n\n"
        "Step 2: Extract the interval.\n"
        f"a = {lower}, b = {upper}, x = {start}.\n\n"
        "Step 3: Use named intermediate quantities to avoid sign mistakes.\n"
        "For boundaries 0 and b, define r = q/p and\n"
        "E_x[tau] = (b * ((r^x - 1)/(r^b - 1)) - x)/(p-q).\n\n"
        "Step 4: Compute the powers and differences.\n"
        f"r = {r}.\n"
        f"A = r^x = {r}^{start} = {r_x}.\n"
        f"B = r^b = {r}^{upper} = {r_b}.\n"
        f"C = A - 1 = {r_x} - 1 = {numerator}.\n"
        f"D = B - 1 = {r_b} - 1 = {denominator}.\n\n"
        "Step 5: Compute the boundary term before dividing by drift.\n"
        f"C/D = ({numerator})/({denominator}) = {ratio}.\n"
        f"U = b * C/D = {upper} * {ratio} = {boundary_term}.\n"
        f"V = U - x = {boundary_term} - {start} = {shifted_value}.\n\n"
        "Step 6: Divide by p-q.\n"
        f"p-q = {p} - {q} = {drift}.\n"
        f"E_x[tau] = V/(p-q) = ({shifted_value})/({drift}) = {expectation}.\n\n"
        "Step 7: Return the JSON answer.\n"
        + final_answer(answer)
    )


def martingale_reasoning_v3_5(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    problem_type = record["problem_type"]
    result = str(answer["is_martingale"]).lower()
    symbol = params["process_notation"]

    if problem_type == "quadratic_compensation":
        variance = params["variance"]
        compensation = params["compensation"]
        relation = "equal" if answer["is_martingale"] else "not equal"
        return (
            "Step 1: Use only the compensation comparison.\n"
            f"For a centered independent-increment walk, {symbol}_n^2 - c n is a martingale exactly when c = Var(Y_1).\n\n"
            "Step 2: Read the two numbers.\n"
            f"Required c = Var(Y_1) = {variance}.\n"
            f"Proposed c = {compensation}.\n\n"
            "Step 3: Compare.\n"
            f"Proposed c is {relation} to the required c.\n\n"
            "Step 4: Conclude with the required JSON schema.\n"
            f"is_martingale = {result}.\n\n"
            + final_answer(answer)
        )

    if problem_type == "exponential_compensation":
        p = params["p"]
        q = params["q"]
        theta = params["theta_name"]
        denominator = params["denominator"]
        relation = "same" if answer["is_martingale"] else "different"
        return (
            "Step 1: Use only the denominator-factor comparison.\n"
            "Do not expand the whole conditional expectation.\n\n"
            "Step 2: Required factor.\n"
            f"required = E[exp({theta}Y_1)] = {p} exp({theta}) + {q} exp(-{theta}).\n\n"
            "Step 3: Proposed factor.\n"
            f"proposed = {denominator}.\n\n"
            "Step 4: Compare and conclude.\n"
            f"The proposed factor and required factor are {relation}, so is_martingale = {result}.\n\n"
            + final_answer(answer)
        )

    return martingale_reasoning(record)


def optional_stopping_reasoning_v3_5(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    condition = params["condition"]
    result = str(answer["valid"]).lower()

    if condition == "bounded":
        check = "tau has a deterministic cap, so tau is bounded"
    elif condition == "finite_state":
        check = "the stopped process is finite-state and therefore bounded"
    else:
        check = "tau is uncapped and no boundedness or integrability hypothesis is supplied"

    return (
        "Step 1: Check the optional-stopping condition.\n"
        f"{check}.\n\n"
        "Step 2: Decide validity.\n"
        f"The proposed use of E[M_tau] = E[M_0] has valid = {result}.\n\n"
        "Step 3: Return exactly the required JSON schema.\n"
        + final_answer(answer)
    )


REASONING_BUILDERS_V3_5 = {
    "hitting_time_expectation": hitting_time_reasoning_v3_5,
    "stopped_process_expectation": stopped_process_reasoning_v2,
    "martingale_verification": martingale_reasoning_v3_5,
    "optional_stopping_validity": optional_stopping_reasoning_v3_5,
}


REASONING_BUILDERS = {
    "hitting_time_expectation": hitting_time_reasoning,
    "stopped_process_expectation": stopped_process_reasoning,
    "martingale_verification": martingale_reasoning,
    "optional_stopping_validity": optional_stopping_reasoning,
}


def transform_record(record: dict[str, Any]) -> dict[str, Any]:
    transformed = dict(record)
    transformed["reasoning"] = REASONING_BUILDERS[record["family"]](record)
    metadata = dict(transformed.get("metadata", {}))
    metadata["reasoning_variant"] = "algorithmic_scaffold"
    transformed["metadata"] = metadata
    return transformed


def transform_record_v2(record: dict[str, Any]) -> dict[str, Any]:
    transformed = dict(record)
    transformed["reasoning"] = REASONING_BUILDERS_V2[record["family"]](record)
    metadata = dict(transformed.get("metadata", {}))
    metadata["reasoning_variant"] = "algorithmic_scaffold_v2"
    transformed["metadata"] = metadata
    return transformed


def transform_record_v3(record: dict[str, Any]) -> dict[str, Any]:
    transformed = dict(record)
    transformed["reasoning"] = REASONING_BUILDERS_V3[record["family"]](record)
    metadata = dict(transformed.get("metadata", {}))
    metadata["reasoning_variant"] = "algorithmic_scaffold_v3"
    transformed["metadata"] = metadata
    return transformed


def transform_record_v2_5(record: dict[str, Any]) -> dict[str, Any]:
    transformed = dict(record)
    transformed["reasoning"] = REASONING_BUILDERS_V2_5[record["family"]](record)
    metadata = dict(transformed.get("metadata", {}))
    metadata["reasoning_variant"] = "algorithmic_scaffold_v2_5"
    transformed["metadata"] = metadata
    return transformed


def transform_record_v3_1(record: dict[str, Any]) -> dict[str, Any]:
    transformed = dict(record)
    if record["family"] in {"martingale_verification", "optional_stopping_validity"}:
        transformed["reasoning"] = REASONING_BUILDERS_V3[record["family"]](record)
    else:
        transformed["reasoning"] = REASONING_BUILDERS_V2[record["family"]](record)
    metadata = dict(transformed.get("metadata", {}))
    metadata["reasoning_variant"] = "algorithmic_scaffold_v3_1"
    metadata["variant_note"] = "fresh larger split with v3 binary reasoning patches and v2-style non-binary scaffolds"
    transformed["metadata"] = metadata
    return transformed


def transform_record_v3_5(record: dict[str, Any]) -> dict[str, Any]:
    transformed = dict(record)
    transformed["reasoning"] = REASONING_BUILDERS_V3_5[record["family"]](record)
    metadata = dict(transformed.get("metadata", {}))
    metadata["reasoning_variant"] = "algorithmic_scaffold_v3_5"
    metadata["variant_note"] = "larger split with field-style biased hitting and concise binary comparison scaffolds"
    transformed["metadata"] = metadata
    return transformed


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def write_readme(target_dir: Path, train: bool) -> None:
    if train:
        size_note = (
            "This is a larger generated training split. Non-binary computational families "
            "are deliberately oversampled relative to the binary diagnostic families.\n"
        )
    else:
        size_note = "This validation split keeps the same size as the existing validation data.\n"

    readme = (
        f"# {target_dir.name}\n\n"
        "Algorithmic-scaffold reasoning variant.\n\n"
        "The reasoning is written as parameter extraction, formula selection, substitution, "
        "simplification, and final JSON answer. The goal is to teach a small model a stable "
        "computational routine rather than only expose it to compact theorem prose.\n\n"
        f"{size_note}"
    )
    (target_dir / "README.md").write_text(readme)


def build_train_split() -> None:
    target_dir = DATA_ROOT / "train_algorithmic_scaffold"
    target_dir.mkdir(parents=True, exist_ok=True)

    for family, count in TRAIN_COUNTS.items():
        generator = GENERATORS[family]
        rows = []
        for offset in range(count):
            seed = 700000 + 100000 * list(TRAIN_COUNTS).index(family) + offset
            difficulty = 1 + (offset % 3)
            record = generator.generate_record(seed=seed, difficulty=difficulty, split="train")
            rows.append(transform_record(record))
        write_jsonl(rows, target_dir / f"{family}.jsonl")

    write_readme(target_dir, train=True)


def build_val_split() -> None:
    source_dir = DATA_ROOT / "val"
    target_dir = DATA_ROOT / "val_algorithmic_scaffold"
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source_dir.glob("*.jsonl")):
        rows = []
        with source_path.open() as f:
            for line in f:
                if line.strip():
                    rows.append(transform_record(json.loads(line)))
        write_jsonl(rows, target_dir / source_path.name)

    write_readme(target_dir, train=False)


def difficulty_for_problem_type(problem_type: str) -> int:
    if problem_type in {"symmetric_boundaries_zero_a", "bounded_walk_expectation", "centered_walk_basic", "bounded_time_valid"}:
        return 1
    if problem_type in {"symmetric_shifted_boundaries", "quadratic_fixed_horizon", "unbounded_first_hit_invalid"}:
        return 2
    return 3


def targeted_records(
    family: str,
    problem_type: str,
    count: int,
    seed_start: int,
    transform=transform_record_v2,
) -> list[dict[str, Any]]:
    generator = GENERATORS[family]
    rows = []
    seed = seed_start
    difficulty = difficulty_for_problem_type(problem_type)

    while len(rows) < count:
        params = generator.sample_params(seed=seed, difficulty=difficulty, split="train")
        if params["problem_type"] == problem_type:
            record = make_record_from_params(generator, params, split="train", seed=seed)
            rows.append(transform(record))
        seed += 1

    return rows


def build_train_split_v2() -> None:
    target_dir = DATA_ROOT / "train_algorithmic_scaffold_v2"
    target_dir.mkdir(parents=True, exist_ok=True)

    family_offsets = {
        "hitting_time_expectation": 1200000,
        "stopped_process_expectation": 1400000,
        "martingale_verification": 1600000,
        "optional_stopping_validity": 1800000,
    }

    for family, type_counts in TRAIN_TYPE_COUNTS_V2.items():
        rows = []
        type_index = 0
        for problem_type, count in type_counts.items():
            seed_start = family_offsets[family] + 10000 * type_index
            rows.extend(targeted_records(family, problem_type, count, seed_start))
            type_index += 1
        write_jsonl(rows, target_dir / f"{family}.jsonl")

    write_readme(target_dir, train=True)


def build_val_split_v2() -> None:
    source_dir = DATA_ROOT / "val"
    target_dir = DATA_ROOT / "val_algorithmic_scaffold_v2"
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source_dir.glob("*.jsonl")):
        rows = []
        with source_path.open() as f:
            for line in f:
                if line.strip():
                    rows.append(transform_record_v2(json.loads(line)))
        write_jsonl(rows, target_dir / source_path.name)

    write_readme(target_dir, train=False)


def build_train_split_v2_5() -> None:
    target_dir = DATA_ROOT / "train_algorithmic_scaffold_v2_5"
    target_dir.mkdir(parents=True, exist_ok=True)

    family_offsets = {
        "hitting_time_expectation": 2200000,
        "stopped_process_expectation": 2400000,
        "martingale_verification": 2600000,
        "optional_stopping_validity": 2800000,
    }

    for family, type_counts in TRAIN_TYPE_COUNTS_V2_5.items():
        rows = []
        type_index = 0
        for problem_type, count in type_counts.items():
            seed_start = family_offsets[family] + 10000 * type_index
            rows.extend(targeted_records(family, problem_type, count, seed_start, transform=transform_record_v2_5))
            type_index += 1
        write_jsonl(rows, target_dir / f"{family}.jsonl")

    write_readme(target_dir, train=True)


def build_val_split_v2_5() -> None:
    source_dir = DATA_ROOT / "val"
    target_dir = DATA_ROOT / "val_algorithmic_scaffold_v2_5"
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source_dir.glob("*.jsonl")):
        rows = []
        with source_path.open() as f:
            for line in f:
                if line.strip():
                    rows.append(transform_record_v2_5(json.loads(line)))
        write_jsonl(rows, target_dir / source_path.name)

    write_readme(target_dir, train=False)


def build_train_split_v3() -> None:
    target_dir = DATA_ROOT / "train_algorithmic_scaffold_v3"
    target_dir.mkdir(parents=True, exist_ok=True)

    family_offsets = {
        "hitting_time_expectation": 3200000,
        "stopped_process_expectation": 3400000,
        "martingale_verification": 3600000,
        "optional_stopping_validity": 3800000,
    }

    for family, type_counts in TRAIN_TYPE_COUNTS_V3.items():
        rows = []
        type_index = 0
        for problem_type, count in type_counts.items():
            seed_start = family_offsets[family] + 10000 * type_index
            rows.extend(targeted_records(family, problem_type, count, seed_start, transform=transform_record_v3))
            type_index += 1
        write_jsonl(rows, target_dir / f"{family}.jsonl")

    write_readme(target_dir, train=True)


def build_val_split_v3() -> None:
    source_dir = DATA_ROOT / "val"
    target_dir = DATA_ROOT / "val_algorithmic_scaffold_v3"
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source_dir.glob("*.jsonl")):
        rows = []
        with source_path.open() as f:
            for line in f:
                if line.strip():
                    rows.append(transform_record_v3(json.loads(line)))
        write_jsonl(rows, target_dir / source_path.name)

    write_readme(target_dir, train=False)


def build_train_split_v3_1() -> None:
    target_dir = DATA_ROOT / "train_algorithmic_scaffold_v3_1"
    target_dir.mkdir(parents=True, exist_ok=True)

    family_offsets = {
        "hitting_time_expectation": 4200000,
        "stopped_process_expectation": 4400000,
        "martingale_verification": 4600000,
        "optional_stopping_validity": 4800000,
    }

    for family, type_counts in TRAIN_TYPE_COUNTS_V3_1.items():
        rows = []
        type_index = 0
        for problem_type, count in type_counts.items():
            seed_start = family_offsets[family] + 10000 * type_index
            rows.extend(targeted_records(family, problem_type, count, seed_start, transform=transform_record_v3_1))
            type_index += 1
        write_jsonl(rows, target_dir / f"{family}.jsonl")

    write_readme(target_dir, train=True)


def build_val_split_v3_1() -> None:
    source_dir = DATA_ROOT / "val"
    target_dir = DATA_ROOT / "val_algorithmic_scaffold_v3_1"
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source_dir.glob("*.jsonl")):
        rows = []
        with source_path.open() as f:
            for line in f:
                if line.strip():
                    rows.append(transform_record_v3_1(json.loads(line)))
        write_jsonl(rows, target_dir / source_path.name)

    write_readme(target_dir, train=False)


def build_train_split_v3_5() -> None:
    target_dir = DATA_ROOT / "train_algorithmic_scaffold_v3_5"
    target_dir.mkdir(parents=True, exist_ok=True)

    family_offsets = {
        "hitting_time_expectation": 5200000,
        "stopped_process_expectation": 5400000,
        "martingale_verification": 5600000,
        "optional_stopping_validity": 5800000,
    }

    for family, type_counts in TRAIN_TYPE_COUNTS_V3_5.items():
        rows = []
        type_index = 0
        for problem_type, count in type_counts.items():
            seed_start = family_offsets[family] + 10000 * type_index
            rows.extend(targeted_records(family, problem_type, count, seed_start, transform=transform_record_v3_5))
            type_index += 1
        write_jsonl(rows, target_dir / f"{family}.jsonl")

    write_readme(target_dir, train=True)


def build_val_split_v3_5() -> None:
    source_dir = DATA_ROOT / "val"
    target_dir = DATA_ROOT / "val_algorithmic_scaffold_v3_5"
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source_dir.glob("*.jsonl")):
        rows = []
        with source_path.open() as f:
            for line in f:
                if line.strip():
                    rows.append(transform_record_v3_5(json.loads(line)))
        write_jsonl(rows, target_dir / source_path.name)

    write_readme(target_dir, train=False)


def main() -> None:
    build_train_split()
    build_val_split()
    build_train_split_v2()
    build_val_split_v2()
    build_train_split_v2_5()
    build_val_split_v2_5()
    build_train_split_v3()
    build_val_split_v3()
    build_train_split_v3_1()
    build_val_split_v3_1()
    build_train_split_v3_5()
    build_val_split_v3_5()


if __name__ == "__main__":
    main()
