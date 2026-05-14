"""Generators for hitting-time expectation problems."""

from __future__ import annotations

from fractions import Fraction
import random

from .base import JsonDict, ProblemGenerator
from .theorem_bank import theorem_statement


class HittingTimeExpectationGenerator(ProblemGenerator):
    """Generate exact absorption-time expectation examples."""

    family = "hitting_time_expectation"

    def sample_params(self, seed: int, difficulty: int, split: str) -> JsonDict:
        rng = random.Random(seed)
        if difficulty <= 1:
            problem_type = "symmetric_boundaries_zero_a"
        elif difficulty == 2:
            problem_type = "symmetric_shifted_boundaries"
        else:
            problem_type = rng.choice(["symmetric_shifted_boundaries", "biased_boundaries_zero_a"])

        params = {
            "problem_type": problem_type,
            "difficulty": difficulty,
            "split": split,
            "seed": seed,
            "process_notation": rng.choice(["S", "X"]),
        }

        if problem_type == "symmetric_boundaries_zero_a":
            upper = rng.choice([4, 5, 6, 8, 10, 12])
            start = rng.randrange(1, upper)
            expected_time = Fraction(start * (upper - start), 1)
            params.update({"lower": 0, "upper": upper, "start": start, "expected_time": expected_time})
        elif problem_type == "symmetric_shifted_boundaries":
            lower = rng.choice([-5, -3, -2, 1, 2])
            width = rng.choice([4, 5, 6, 8, 10])
            upper = lower + width
            start = rng.randrange(lower + 1, upper)
            expected_time = Fraction((start - lower) * (upper - start), 1)
            params.update({"lower": lower, "upper": upper, "start": start, "expected_time": expected_time})
        elif problem_type == "biased_boundaries_zero_a":
            upper = rng.choice([4, 5, 6, 7])
            start = rng.randrange(1, upper)
            p = rng.choice([Fraction(1, 3), Fraction(2, 5), Fraction(3, 5), Fraction(2, 3)])
            q = 1 - p
            expected_time = self._biased_expected_time(start=start, upper=upper, p=p)
            params.update({"lower": 0, "upper": upper, "start": start, "p": p, "q": q, "expected_time": expected_time})
        else:
            raise ValueError(f"Unknown problem_type: {problem_type}")

        return params

    def generate_problem(self, params: JsonDict) -> str:
        if params["problem_type"] == "symmetric_boundaries_zero_a":
            return self._problem_symmetric_boundaries_zero_a(params)
        if params["problem_type"] == "symmetric_shifted_boundaries":
            return self._problem_symmetric_shifted_boundaries(params)
        if params["problem_type"] == "biased_boundaries_zero_a":
            return self._problem_biased_boundaries_zero_a(params)
        raise ValueError(f"Unknown problem_type: {params['problem_type']}")

    def generate_reasoning(self, params: JsonDict) -> str:
        if params["problem_type"] == "symmetric_boundaries_zero_a":
            return self._reasoning_symmetric_boundaries_zero_a(params)
        if params["problem_type"] == "symmetric_shifted_boundaries":
            return self._reasoning_symmetric_shifted_boundaries(params)
        if params["problem_type"] == "biased_boundaries_zero_a":
            return self._reasoning_biased_boundaries_zero_a(params)
        raise ValueError(f"Unknown problem_type: {params['problem_type']}")

    def generate_solution(self, params: JsonDict) -> JsonDict:
        return {"expected_time": params["expected_time"]}

    def generate_metadata(self, params: JsonDict) -> JsonDict:
        if params["problem_type"] == "biased_boundaries_zero_a":
            labels = ["finite_difference_hitting_time_equation"]
        else:
            labels = ["quadratic_martingale_symmetric_rw", "optional_stopping_finite_state_hitting_time"]
        return {"theorem_labels": labels}

    def _problem_symmetric_boundaries_zero_a(self, params: JsonDict) -> str:
        s = params["process_notation"]
        a = params["upper"]
        i = params["start"]
        return (
            f"Let ({s}_n) be a simple symmetric random walk on the integers with {s}_0 = {i}. "
            f"Let tau = inf{{n >= 0 : {s}_n in {{0, {a}}}}}. Compute E[tau]. Answer with JSON "
            f"of the form {{\"expected_time\": \"...\"}} inside the answer tags."
        )

    def _problem_symmetric_shifted_boundaries(self, params: JsonDict) -> str:
        s = params["process_notation"]
        lower = params["lower"]
        upper = params["upper"]
        start = params["start"]
        return (
            f"Let ({s}_n) be a simple symmetric random walk with {s}_0 = {start}. Let tau be the first "
            f"time the walk hits either {lower} or {upper}. Compute E[tau]. Answer with JSON of the "
            f"form {{\"expected_time\": \"...\"}} inside the answer tags."
        )

    def _problem_biased_boundaries_zero_a(self, params: JsonDict) -> str:
        s = params["process_notation"]
        a = params["upper"]
        i = params["start"]
        p = self.fraction_to_str(params["p"])
        q = self.fraction_to_str(params["q"])
        return (
            f"Let ({s}_n) be a nearest-neighbor random walk on the integers with {s}_0 = {i}, "
            f"P({s}_(n+1) = {s}_n + 1 | F_n) = {p}, and P({s}_(n+1) = {s}_n - 1 | F_n) = {q}. "
            f"Let tau = inf{{n >= 0 : {s}_n in {{0, {a}}}}}. Compute E[tau]. Answer with JSON "
            f"of the form {{\"expected_time\": \"...\"}} inside the answer tags."
        )

    def _reasoning_symmetric_boundaries_zero_a(self, params: JsonDict) -> str:
        s = params["process_notation"]
        a = params["upper"]
        i = params["start"]
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('optional_stopping_bounded_stopped_process')} "
            f"Use two martingales for the finite-boundary simple symmetric random walk. First, ({s}_n) "
            f"is a martingale, and optional stopping gives E[{s}_tau] = {i}. "
            f"{theorem_statement('quadratic_martingale_centered_increments')} "
            f"For a simple symmetric random walk, sigma^2 = 1, so M_n = {s}_n^2 - n is a martingale. At tau, "
            f"{s}_tau is either 0 or {a}. Also E[{s}_tau] = {i}, so P({s}_tau = {a}) = {i}/{a}. "
            f"Thus E[{s}_tau^2] = {a}^2 * {i}/{a} = {a} * {i}. Optional stopping for M gives "
            f"E[tau] = E[{s}_tau^2] - {i}^2 = {i}({a}-{i}).\n\n"
            f"{self.answer_block(self.to_json_safe(answer))}"
        )

    def _reasoning_symmetric_shifted_boundaries(self, params: JsonDict) -> str:
        lower = params["lower"]
        upper = params["upper"]
        start = params["start"]
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('symmetric_gambler_ruin_hitting_time')} "
            f"Reduce to the standard finite-boundary simple symmetric random walk. Shift the walk by "
            f"subtracting the lower boundary {lower}. The shifted start is "
            f"{start - lower} and the shifted upper boundary is {upper - lower}. The symmetric "
            f"gambler's ruin hitting-time formula gives E[tau] = (start-lower)(upper-start).\n\n"
            f"{self.answer_block(self.to_json_safe(answer))}"
        )

    def _reasoning_biased_boundaries_zero_a(self, params: JsonDict) -> str:
        i = params["start"]
        a = params["upper"]
        p = self.fraction_to_str(params["p"])
        q = self.fraction_to_str(params["q"])
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('first_step_hitting_time_equation')} For the biased walk, "
            f"e_0 = e_{a} = 0, p = {p}, and q = {q}. Solving this second-order difference equation "
            f"gives e_i = (a((q/p)^i - 1)/((q/p)^a - 1) - i)/(p-q). Substituting i = {i} and "
            f"a = {a} gives the canonical value.\n\n{self.answer_block(self.to_json_safe(answer))}"
        )

    @staticmethod
    def _biased_expected_time(start: int, upper: int, p: Fraction) -> Fraction:
        q = 1 - p
        r = q / p
        numerator = Fraction(upper, 1) * (r**start - 1)
        denominator = r**upper - 1
        return (numerator / denominator - start) / (p - q)
