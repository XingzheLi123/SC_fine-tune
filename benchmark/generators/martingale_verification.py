"""Generators for martingale-verification problems."""

from __future__ import annotations

from fractions import Fraction
import random

from .base import JsonDict, ProblemGenerator
from .theorem_bank import theorem_statement


class MartingaleVerificationGenerator(ProblemGenerator):
    """Generate discrete-time martingale verification examples."""

    family = "martingale_verification"

    def sample_params(self, seed: int, difficulty: int, split: str) -> JsonDict:
        rng = random.Random(seed)
        if difficulty <= 1:
            problem_type = "centered_walk_basic"
        elif difficulty == 2:
            problem_type = "quadratic_compensation"
        else:
            problem_type = rng.choice(["quadratic_compensation", "exponential_compensation"])

        params = {
            "problem_type": problem_type,
            "difficulty": difficulty,
            "split": split,
            "seed": seed,
            "process_notation": rng.choice(["S", "X"]),
            "time_notation": "n",
        }

        if problem_type == "centered_walk_basic":
            step = rng.choice([1, 2, 3, 4])
            params.update({"step": step, "is_martingale": True, "reason_code": "zero_drift"})
        elif problem_type == "quadratic_compensation":
            step = rng.choice([1, 2, 3, 4, 5, 10])
            variance = step * step
            compensation = variance if rng.random() < 0.65 else rng.choice([variance + 1, max(1, variance - 1), 2 * variance])
            surface_variant = rng.choice(["variance_given", "standard_deviation_given", "distribution_given"])
            params.update(
                {
                    "step": step,
                    "variance": variance,
                    "compensation": compensation,
                    "surface_variant": surface_variant,
                    "is_martingale": compensation == variance,
                    "reason_code": "correct_compensation" if compensation == variance else "wrong_compensation",
                }
            )
        elif problem_type == "exponential_compensation":
            p = rng.choice([Fraction(1, 3), Fraction(2, 5), Fraction(3, 5), Fraction(2, 3)])
            q = 1 - p
            theta_name = rng.choice(["theta", "lambda"])
            correct = rng.random() < 0.65
            denominator = f"p exp({theta_name}) + q exp(-{theta_name})" if correct else f"exp({theta_name})"
            params.update(
                {
                    "p": p,
                    "q": q,
                    "theta_name": theta_name,
                    "denominator": denominator,
                    "is_martingale": correct,
                    "reason_code": "correct_compensation" if correct else "wrong_compensation",
                }
            )
        else:
            raise ValueError(f"Unknown problem_type: {problem_type}")

        return params

    def generate_problem(self, params: JsonDict) -> str:
        if params["problem_type"] == "centered_walk_basic":
            return self._problem_centered_walk_basic(params)
        if params["problem_type"] == "quadratic_compensation":
            return self._problem_quadratic_compensation(params)
        if params["problem_type"] == "exponential_compensation":
            return self._problem_exponential_compensation(params)
        raise ValueError(f"Unknown problem_type: {params['problem_type']}")

    def generate_reasoning(self, params: JsonDict) -> str:
        if params["problem_type"] == "centered_walk_basic":
            return self._reasoning_centered_walk_basic(params)
        if params["problem_type"] == "quadratic_compensation":
            return self._reasoning_quadratic_compensation(params)
        if params["problem_type"] == "exponential_compensation":
            return self._reasoning_exponential_compensation(params)
        raise ValueError(f"Unknown problem_type: {params['problem_type']}")

    def generate_solution(self, params: JsonDict) -> JsonDict:
        return {"is_martingale": params["is_martingale"]}

    def generate_metadata(self, params: JsonDict) -> JsonDict:
        return {
            "reason_code": params["reason_code"],
            "theorem_labels": ["conditional_expectation_martingale_test"],
        }

    def _problem_centered_walk_basic(self, params: JsonDict) -> str:
        s = params["process_notation"]
        step = params["step"]
        return (
            f"Let {s}_0 = 0 and {s}_n = Y_1 + ... + Y_n, where the Y_k are independent and "
            f"P(Y_k = {step}) = P(Y_k = -{step}) = 1/2. With respect to the natural filtration, "
            f"is ({s}_n) a martingale? Answer with JSON of the form {{\"is_martingale\": true}} or "
            f"{{\"is_martingale\": false}} inside the answer tags."
        )

    def _problem_quadratic_compensation(self, params: JsonDict) -> str:
        s = params["process_notation"]
        step = params["step"]
        comp = params["compensation"]
        variant = params["surface_variant"]
        if variant == "variance_given":
            increment_text = f"the increments have mean 0 and variance {params['variance']}"
        elif variant == "standard_deviation_given":
            increment_text = f"the increments have mean 0 and standard deviation {step}"
        else:
            increment_text = f"P(Y_k = {step}) = P(Y_k = -{step}) = 1/2"

        return (
            f"Let {s}_n = Y_1 + ... + Y_n for independent increments with {increment_text}. "
            f"Consider M_n = {s}_n^2 - {comp} n. With respect to the natural filtration, "
            f"is (M_n) a martingale? Answer with JSON of the form {{\"is_martingale\": true}} or "
            f"{{\"is_martingale\": false}} inside the answer tags."
        )

    def _problem_exponential_compensation(self, params: JsonDict) -> str:
        s = params["process_notation"]
        theta = params["theta_name"]
        p = self.fraction_to_str(params["p"])
        q = self.fraction_to_str(params["q"])
        denom = params["denominator"]
        return (
            f"Let {s}_n = Y_1 + ... + Y_n, where the Y_k are independent with P(Y_k = 1) = {p} "
            f"and P(Y_k = -1) = {q}. For fixed {theta}, consider M_n = exp({theta} {s}_n) / "
            f"({denom})^n. With respect to the natural filtration, is (M_n) a martingale? "
            f"Answer with JSON of the form {{\"is_martingale\": true}} or "
            f"{{\"is_martingale\": false}} inside the answer tags."
        )

    def _reasoning_centered_walk_basic(self, params: JsonDict) -> str:
        s = params["process_notation"]
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('conditional_expectation_martingale_test')} "
            f"Here the process is adapted to the natural filtration. Since E[Y_(n+1)] = 0 and "
            f"Y_(n+1) is independent of the natural filtration, E[{s}_(n+1) | F_n] = {s}_n. "
            f"So ({s}_n) is a martingale.\n\n{self.answer_block(answer)}"
        )

    def _reasoning_quadratic_compensation(self, params: JsonDict) -> str:
        s = params["process_notation"]
        variance = params["variance"]
        comp = params["compensation"]
        answer = self.generate_solution(params)
        verdict = "equals" if params["is_martingale"] else "does not equal"
        return (
            f"{theorem_statement('quadratic_martingale_centered_increments')} "
            f"For this process, E[{s}_(n+1)^2 | F_n] = {s}_n^2 + Var(Y_(n+1)). "
            f"Here Var(Y_(n+1)) = {variance}. Therefore {s}_n^2 - c n is a martingale exactly "
            f"when c = {variance}. The proposed compensation is c = {comp}, which {verdict} "
            f"the variance.\n\n{self.answer_block(answer)}"
        )

    def _reasoning_exponential_compensation(self, params: JsonDict) -> str:
        s = params["process_notation"]
        theta = params["theta_name"]
        p = self.fraction_to_str(params["p"])
        q = self.fraction_to_str(params["q"])
        answer = self.generate_solution(params)
        return (
            f"{theorem_statement('exponential_martingale_discrete')} "
            f"For this two-point increment distribution, since the increment is independent, "
            f"E[exp({theta} {s}_(n+1)) | F_n] = exp({theta} {s}_n) "
            f"({p} exp({theta}) + {q} exp(-{theta})). The denominator must be this moment "
            f"generating factor at every step. Comparing with the proposed denominator gives the answer.\n\n"
            f"{self.answer_block(answer)}"
        )
