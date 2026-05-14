"""Generators for optional-stopping validity problems."""

from __future__ import annotations

import random

from .base import JsonDict, ProblemGenerator
from .theorem_bank import theorem_statement


class OptionalStoppingValidityGenerator(ProblemGenerator):
    """Generate examples asking whether optional stopping is justified."""

    family = "optional_stopping_validity"

    def sample_params(self, seed: int, difficulty: int, split: str) -> JsonDict:
        rng = random.Random(seed)
        if difficulty <= 1:
            problem_type = "bounded_time_valid"
        elif difficulty == 2:
            problem_type = "unbounded_first_hit_invalid"
        else:
            problem_type = rng.choice(["finite_state_hitting_valid", "unbounded_first_hit_invalid"])

        params = {
            "problem_type": problem_type,
            "difficulty": difficulty,
            "split": split,
            "seed": seed,
            "process_notation": rng.choice(["S", "X"]),
        }

        if problem_type == "bounded_time_valid":
            horizon = rng.choice([3, 5, 8, 10, 20])
            level = rng.choice([1, 2, 3])
            params.update({"horizon": horizon, "level": level, "valid": True, "condition": "bounded"})
        elif problem_type == "unbounded_first_hit_invalid":
            level = rng.choice([1, 2, 3, 4])
            params.update({"level": level, "valid": False, "condition": "fails"})
        elif problem_type == "finite_state_hitting_valid":
            upper = rng.choice([4, 5, 6, 8, 10])
            start = rng.randrange(1, upper)
            params.update({"upper": upper, "start": start, "valid": True, "condition": "finite_state"})
        else:
            raise ValueError(f"Unknown problem_type: {problem_type}")

        return params

    def generate_problem(self, params: JsonDict) -> str:
        if params["problem_type"] == "bounded_time_valid":
            return self._problem_bounded_time_valid(params)
        if params["problem_type"] == "unbounded_first_hit_invalid":
            return self._problem_unbounded_first_hit_invalid(params)
        if params["problem_type"] == "finite_state_hitting_valid":
            return self._problem_finite_state_hitting_valid(params)
        raise ValueError(f"Unknown problem_type: {params['problem_type']}")

    def generate_reasoning(self, params: JsonDict) -> str:
        if params["problem_type"] == "bounded_time_valid":
            return self._reasoning_bounded_time_valid(params)
        if params["problem_type"] == "unbounded_first_hit_invalid":
            return self._reasoning_unbounded_first_hit_invalid(params)
        if params["problem_type"] == "finite_state_hitting_valid":
            return self._reasoning_finite_state_hitting_valid(params)
        raise ValueError(f"Unknown problem_type: {params['problem_type']}")

    def generate_solution(self, params: JsonDict) -> JsonDict:
        return {"valid": params["valid"]}

    def generate_metadata(self, params: JsonDict) -> JsonDict:
        return {
            "condition": params["condition"],
            "theorem_labels": ["optional_stopping"],
        }

    def _problem_bounded_time_valid(self, params: JsonDict) -> str:
        s = params["process_notation"]
        n = params["horizon"]
        a = params["level"]
        return (
            f"Let ({s}_n) be a simple symmetric random walk with {s}_0 = 0 and natural filtration F_n. "
            f"Let T = inf{{k >= 0 : {s}_k = {a}}} and tau = min(T, {n}). A solution claims that optional stopping gives "
            f"E[{s}_tau] = E[{s}_0]. Is this use of optional stopping justified? Answer with JSON of "
            f"the form {{\"valid\": true}} or {{\"valid\": false}} inside the answer tags."
        )

    def _problem_unbounded_first_hit_invalid(self, params: JsonDict) -> str:
        s = params["process_notation"]
        a = params["level"]
        return (
            f"Let ({s}_n) be a simple symmetric random walk with {s}_0 = 0. Let tau = inf{{n >= 0 : "
            f"{s}_n = {a}}}. A solution claims that optional stopping directly gives "
            f"E[{s}_tau] = E[{s}_0] because ({s}_n) is a martingale. Is this use justified as stated? "
            f"Answer with JSON of the form {{\"valid\": true}} or {{\"valid\": false}} inside the answer tags."
        )

    def _problem_finite_state_hitting_valid(self, params: JsonDict) -> str:
        s = params["process_notation"]
        a = params["upper"]
        i = params["start"]
        return (
            f"Let ({s}_n) be a simple symmetric random walk on {{0, ..., {a}}}, absorbed when it hits "
            f"0 or {a}, with {s}_0 = {i}. Let tau be the absorption time. A solution applies optional "
            f"stopping to the bounded stopped process to conclude E[{s}_tau] = {i}. Is this use justified? "
            f"Answer with JSON of the form {{\"valid\": true}} or {{\"valid\": false}} inside the answer tags."
        )

    def _reasoning_bounded_time_valid(self, params: JsonDict) -> str:
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('optional_stopping_bounded')} First check the condition: tau is bounded "
            "by the deterministic horizon in its definition. Since the process is a martingale and tau "
            "is bounded, optional stopping applies, so the claimed equality is justified.\n\n"
            f"{self.answer_block(answer)}"
        )

    def _reasoning_unbounded_first_hit_invalid(self, params: JsonDict) -> str:
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('optional_stopping_bounded')} Check the hypotheses before applying it. "
            "The stopping time is not bounded, "
            "and the statement gives no integrability or uniform integrability condition that would "
            "justify optional stopping. The martingale property alone is not enough for this direct step.\n\n"
            f"{self.answer_block(answer)}"
        )

    def _reasoning_finite_state_hitting_valid(self, params: JsonDict) -> str:
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('optional_stopping_bounded_stopped_process')} In the finite absorbing state space, "
            "the stopped process can take only finitely many values, so it is bounded. This gives the "
            "required uniform integrability condition, so optional stopping is justified for the absorption time.\n\n"
            f"{self.answer_block(answer)}"
        )
