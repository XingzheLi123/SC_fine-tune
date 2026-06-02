"""Build formula-direct train/validation variants from the canonical benchmark data."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "benchmark" / "data"


def final_answer(answer: dict[str, Any]) -> str:
    return "Final answer:\n<answer>\n" + json.dumps(answer, sort_keys=True) + "\n</answer>"


def as_fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def hitting_time_reasoning(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    lower = params["lower"]
    upper = params["upper"]
    start = params["start"]

    if record["problem_type"] in {"symmetric_boundaries_zero_a", "symmetric_shifted_boundaries"}:
        return (
            "Use the finite-boundary hitting-time formula for a simple symmetric random walk:\n"
            "E_x[tau] = (x-a)(b-x), where a and b are the absorbing boundaries.\n\n"
            f"Here a = {lower}, b = {upper}, and x = {start}.\n"
            f"Substitute: E_x[tau] = ({start}-{lower})({upper}-{start}) = "
            f"{answer['expected_time']}.\n\n"
            + final_answer(answer)
        )

    p = as_fraction(params["p"])
    q = as_fraction(params["q"])
    r = q / p
    r_start = r**start
    r_upper = r**upper
    weighted_boundary = upper * (r_start - 1) / (r_upper - 1)
    return (
        "Use the finite-boundary hitting-time formula for a biased nearest-neighbor walk. "
        "For boundaries a < x < b and upward/downward probabilities p and q, solve the "
        "second-order difference equation h(x) = 1 + p h(x+1) + q h(x-1), with "
        "h(a)=h(b)=0.\n\n"
        f"Here a = {lower}, b = {upper}, x = {start}, p = {p}, and q = {q}. "
        f"The ratio q/p is {r}. For lower boundary 0, the formula is "
        "E_x[tau] = (b((q/p)^x - 1)/((q/p)^b - 1) - x)/(p-q).\n"
        f"Compute (q/p)^x = {r_start} and (q/p)^b = {r_upper}. "
        f"Then b((q/p)^x - 1)/((q/p)^b - 1) = {weighted_boundary}, so "
        f"E_x[tau] = ({weighted_boundary} - {start})/({p} - {q}) = {answer['expected_time']}.\n\n"
        + final_answer(answer)
    )


def stopped_process_reasoning(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    problem_type = record["problem_type"]
    start = params["start"]

    if problem_type == "bounded_walk_expectation":
        return (
            "Use optional stopping for the bounded stopped martingale X_tau. "
            "Since tau is capped by a deterministic horizon, optional stopping applies.\n\n"
            f"Formula: E[X_tau] = E[X_0] = {start}.\n"
            f"Therefore the requested value is {answer['value']}.\n\n"
            + final_answer(answer)
        )

    if problem_type == "quadratic_fixed_horizon":
        horizon = params["horizon"]
        variance = params["variance"]
        return (
            "Use the second-moment formula for a centered independent-increment walk:\n"
            "E[X_n^2] = X_0^2 + n sigma^2.\n\n"
            f"Here X_0 = {start}, n = {horizon}, and sigma^2 = {variance}.\n"
            f"Substitute: E[X_{horizon}^2] = ({start})^2 + {horizon}({variance}) = "
            f"{answer['value']}.\n\n"
            + final_answer(answer)
        )

    return (
        "Use the martingale M_n = X_n^2 - n for a simple symmetric random walk. "
        "Because tau is bounded by a deterministic horizon, optional stopping applies "
        "to M_tau.\n\n"
        f"The requested stopped-martingale value is E[X_tau^2 - tau] = E[M_tau] = "
        f"E[M_0] = X_0^2 = ({start})^2 = {answer['value']}.\n\n"
        + final_answer(answer)
    )


def martingale_reasoning(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    problem_type = record["problem_type"]
    result = answer["is_martingale"]

    if problem_type == "centered_walk_basic":
        step = params["step"]
        return (
            "Check the martingale condition E[S_{n+1} | F_n] = S_n.\n\n"
            f"The next increment has values +{step} and -{step} with equal probability, "
            "so its conditional mean is 0. Therefore E[S_{n+1} | F_n] = S_n.\n"
            f"Conclusion: is_martingale = {str(result).lower()}.\n\n"
            + final_answer(answer)
        )

    if problem_type == "quadratic_compensation":
        variance = params["variance"]
        compensation = params["compensation"]
        return (
            "For centered independent increments with variance sigma^2, the compensated "
            "quadratic martingale is S_n^2 - n sigma^2.\n\n"
            f"Here sigma^2 = {variance}, but the proposed compensation is {compensation}. "
            f"The compensation is {'correct' if compensation == variance else 'not correct'}.\n"
            f"Conclusion: is_martingale = {str(result).lower()}.\n\n"
            + final_answer(answer)
        )

    denominator = params["denominator"]
    p = params["p"]
    q = params["q"]
    theta_name = params["theta_name"]
    return (
        "For an exponential random-walk martingale, the denominator must be the one-step "
        "moment generating factor E[exp(theta Y)].\n\n"
        f"Here E[exp({theta_name} Y)] = {p} exp({theta_name}) + {q} exp(-{theta_name}). "
        f"The proposed denominator is {denominator}. Check whether these match.\n"
        f"Conclusion: is_martingale = {str(result).lower()}.\n\n"
        + final_answer(answer)
    )


def optional_stopping_reasoning(record: dict[str, Any]) -> str:
    params = record["params"]
    answer = record["canonical_answer"]
    condition = params["condition"]
    result = answer["valid"]

    if condition == "bounded":
        check = "tau is bounded by the deterministic horizon in min(T, horizon)"
    elif condition == "finite_state":
        check = "the stopped/absorbed process is finite-state and bounded"
    else:
        check = "tau is an unbounded first-hitting time, so the bounded-stopping hypothesis is missing"

    return (
        "Check the optional-stopping hypotheses before using E[M_tau] = E[M_0].\n\n"
        f"Key condition: {check}.\n"
        f"Therefore the quoted optional-stopping step has valid = {str(result).lower()}.\n\n"
        + final_answer(answer)
    )


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
    metadata["reasoning_variant"] = "formula_direct"
    transformed["metadata"] = metadata
    return transformed


def write_variant_split(source_split: str, target_split: str, answer_type: str | None = None) -> None:
    source_dir = DATA_ROOT / source_split
    target_dir = DATA_ROOT / target_split
    target_dir.mkdir(parents=True, exist_ok=True)

    for source_path in sorted(source_dir.glob("*.jsonl")):
        rows = []
        with source_path.open() as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    if answer_type is not None and row.get("answer_type") != answer_type:
                        continue
                    rows.append(transform_record(row))

        with (target_dir / source_path.name).open("w") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + "\n")

    readme = (
        f"# {target_split}\n\n"
        "Formula-direct reasoning variant generated from the canonical benchmark split.\n\n"
        "The problems and canonical answers are unchanged. The reasoning is rewritten to be "
        "shorter, more operational, and more explicit about formula substitution and final "
        "answer formatting.\n"
    )
    if answer_type is not None:
        readme += f"\nThis filtered split keeps only `{answer_type}` records.\n"
    (target_dir / "README.md").write_text(readme)


def main() -> None:
    write_variant_split("train", "train_formula_direct")
    write_variant_split("val", "val_formula_direct")


if __name__ == "__main__":
    main()
