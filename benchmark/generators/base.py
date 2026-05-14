"""Shared generator interface for benchmark problem families."""

from __future__ import annotations

from abc import ABC, abstractmethod
from fractions import Fraction
import json
from typing import Any


JsonDict = dict[str, Any]


class ProblemGenerator(ABC):
    """Base class for one benchmark problem family."""

    family: str

    @abstractmethod
    def sample_params(self, seed: int, difficulty: int, split: str) -> JsonDict:
        """Sample a complete parameter dictionary for one problem."""

    @abstractmethod
    def generate_problem(self, params: JsonDict) -> str:
        """Generate the prompt shown to the model."""

    @abstractmethod
    def generate_reasoning(self, params: JsonDict) -> str:
        """Generate theorem-aware reasoning for fine-tuning data."""

    @abstractmethod
    def generate_solution(self, params: JsonDict) -> JsonDict:
        """Generate the canonical machine-gradable answer."""

    def generate_metadata(self, params: JsonDict) -> JsonDict:
        """Generate optional metadata for analysis."""
        return {}

    def generate_record(self, seed: int, difficulty: int, split: str) -> JsonDict:
        """Generate one complete benchmark record."""
        params = self.sample_params(seed=seed, difficulty=difficulty, split=split)
        solution = self.generate_solution(params)

        return {
            "id": self.make_id(split=split, seed=seed),
            "family": self.family,
            "problem_type": params["problem_type"],
            "difficulty": difficulty,
            "split": split,
            "seed": seed,
            "params": self.to_json_safe(params),
            "problem": self.generate_problem(params),
            "reasoning": self.generate_reasoning(params),
            "canonical_answer": self.to_json_safe(solution),
            "metadata": self.to_json_safe(self.generate_metadata(params)),
        }

    def make_id(self, split: str, seed: int) -> str:
        """Create a stable example id."""
        return f"{self.family}_{split}_{seed:06d}"

    @staticmethod
    def answer_block(answer: JsonDict) -> str:
        """Format a structured answer inside the benchmark answer tags."""
        return "Final answer:\n<answer>\n" + json.dumps(answer, sort_keys=True) + "\n</answer>"

    @classmethod
    def to_json_safe(cls, value: Any) -> Any:
        """Convert common exact math objects into JSON-safe values."""
        if isinstance(value, Fraction):
            return cls.fraction_to_str(value)
        if isinstance(value, dict):
            return {key: cls.to_json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls.to_json_safe(item) for item in value]
        if isinstance(value, tuple):
            return [cls.to_json_safe(item) for item in value]
        return value

    @staticmethod
    def fraction_to_str(value: Fraction) -> str:
        """Render an exact rational number as an integer or fraction string."""
        if value.denominator == 1:
            return str(value.numerator)
        return f"{value.numerator}/{value.denominator}"

