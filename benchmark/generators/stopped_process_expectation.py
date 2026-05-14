"""Generators for stopped-process expectation problems."""

from __future__ import annotations

from fractions import Fraction
import random

from .base import JsonDict, ProblemGenerator
from .theorem_bank import theorem_statement


class StoppedProcessExpectationGenerator(ProblemGenerator):
    """Generate exact expectation questions for stopped martingales."""

    family = "stopped_process_expectation"

    def sample_params(self, seed: int, difficulty: int, split: str) -> JsonDict:
        rng = random.Random(seed)
        if difficulty <= 1:
            problem_type = "bounded_walk_expectation"
        elif difficulty == 2:
            problem_type = "quadratic_fixed_horizon"
        else:
            problem_type = rng.choice(["bounded_walk_expectation", "quadratic_fixed_horizon", "stopped_martingale_value"])

        params = {
            "problem_type": problem_type,
            "difficulty": difficulty,
            "split": split,
            "seed": seed,
            "process_notation": rng.choice(["S", "X"]),
        }

        if problem_type == "bounded_walk_expectation":
            start = rng.choice([-3, -2, -1, 0, 1, 2, 3])
            horizon = rng.choice([3, 5, 8, 10, 20])
            level = start + rng.choice([2, 3, 4])
            params.update({"start": start, "horizon": horizon, "level": level, "value": Fraction(start, 1)})
        elif problem_type == "quadratic_fixed_horizon":
            start = rng.choice([-3, -2, -1, 0, 1, 2, 3])
            horizon = rng.choice([2, 3, 5, 7, 10])
            step = rng.choice([1, 2, 3, 5])
            variance = step * step
            value = Fraction(start * start + horizon * variance, 1)
            params.update({"start": start, "horizon": horizon, "step": step, "variance": variance, "value": value})
        elif problem_type == "stopped_martingale_value":
            start = rng.choice([-2, -1, 0, 1, 2])
            horizon = rng.choice([4, 6, 8, 12])
            level = start + rng.choice([2, 3, 4])
            value = Fraction(start * start, 1)
            params.update({"start": start, "horizon": horizon, "level": level, "value": value})
        else:
            raise ValueError(f"Unknown problem_type: {problem_type}")

        return params

    def generate_problem(self, params: JsonDict) -> str:
        if params["problem_type"] == "bounded_walk_expectation":
            return self._problem_bounded_walk_expectation(params)
        if params["problem_type"] == "quadratic_fixed_horizon":
            return self._problem_quadratic_fixed_horizon(params)
        if params["problem_type"] == "stopped_martingale_value":
            return self._problem_stopped_martingale_value(params)
        raise ValueError(f"Unknown problem_type: {params['problem_type']}")

    def generate_reasoning(self, params: JsonDict) -> str:
        if params["problem_type"] == "bounded_walk_expectation":
            return self._reasoning_bounded_walk_expectation(params)
        if params["problem_type"] == "quadratic_fixed_horizon":
            return self._reasoning_quadratic_fixed_horizon(params)
        if params["problem_type"] == "stopped_martingale_value":
            return self._reasoning_stopped_martingale_value(params)
        raise ValueError(f"Unknown problem_type: {params['problem_type']}")

    def generate_solution(self, params: JsonDict) -> JsonDict:
        return {"value": params["value"]}

    def generate_metadata(self, params: JsonDict) -> JsonDict:
        labels = ["optional_stopping"]
        if "quadratic" in params["problem_type"] or params["problem_type"] == "stopped_martingale_value":
            labels.append("quadratic_martingale_symmetric_rw")
        return {"theorem_labels": labels}

    def _problem_bounded_walk_expectation(self, params: JsonDict) -> str:
        s = params["process_notation"]
        x = params["start"]
        n = params["horizon"]
        a = params["level"]
        return (
            f"Let ({s}_n) be a simple symmetric random walk with {s}_0 = {x}. Let T = inf{{k >= 0 : "
            f"{s}_k = {a}}} and tau = min(T, {n}). Compute E[{s}_tau]. Answer with JSON of the form "
            f"{{\"value\": \"...\"}} inside the answer tags."
        )

    def _problem_quadratic_fixed_horizon(self, params: JsonDict) -> str:
        s = params["process_notation"]
        x = params["start"]
        n = params["horizon"]
        step = params["step"]
        return (
            f"Let {s}_n = {x} + Y_1 + ... + Y_n, where P(Y_k = {step}) = P(Y_k = -{step}) = 1/2 "
            f"and the increments are independent. Compute E[{s}_{n}^2]. Answer with JSON of the form "
            f"{{\"value\": \"...\"}} inside the answer tags."
        )

    def _problem_stopped_martingale_value(self, params: JsonDict) -> str:
        s = params["process_notation"]
        x = params["start"]
        n = params["horizon"]
        a = params["level"]
        return (
            f"Let ({s}_n) be a simple symmetric random walk with {s}_0 = {x}. Let T = inf{{k >= 0 : "
            f"{s}_k = {a}}} and tau = min(T, {n}). Compute E[{s}_tau^2 - tau]. Answer with JSON of the form "
            f"{{\"value\": \"...\"}} inside the answer tags."
        )

    def _reasoning_bounded_walk_expectation(self, params: JsonDict) -> str:
        s = params["process_notation"]
        x = params["start"]
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('optional_stopping_bounded')} The process ({s}_n) is a martingale, and tau is "
            f"bounded by the deterministic horizon. Therefore E[{s}_tau] = E[{s}_0] = {x}.\n\n"
            f"{self.answer_block(self.to_json_safe(answer))}"
        )

    def _reasoning_quadratic_fixed_horizon(self, params: JsonDict) -> str:
        s = params["process_notation"]
        x = params["start"]
        n = params["horizon"]
        var = params["variance"]
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('quadratic_martingale_centered_increments')} Since Var(Y_k) = {var}, "
            f"M_n = {s}_n^2 - {var} n is a martingale with M_0 = {x}^2. Taking expectations at the "
            f"deterministic time {n} gives E[{s}_{n}^2] - {var} * {n} = {x}^2, so "
            f"E[{s}_{n}^2] = {x}^2 + {n} * {var}.\n\n"
            f"{self.answer_block(self.to_json_safe(answer))}"
        )

    def _reasoning_stopped_martingale_value(self, params: JsonDict) -> str:
        s = params["process_notation"]
        x = params["start"]
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('quadratic_martingale_centered_increments')} For the simple symmetric random "
            f"walk, sigma^2 = 1, so M_n = {s}_n^2 - n is a martingale. "
            f"{theorem_statement('optional_stopping_bounded')} The stopping time tau is bounded, so optional "
            f"stopping gives E[{s}_tau^2 - tau] = E[M_tau] = M_0 = {x}^2.\n\n"
            f"{self.answer_block(self.to_json_safe(answer))}"
        )
