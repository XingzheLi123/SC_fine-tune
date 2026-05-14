# Generator Architecture

The benchmark is notebook-first, but reusable generation logic should live in small Python classes. Notebooks are the workbench for debugging, inspection, plotting, and exporting. Generator classes are the stable machinery that notebooks call.

## Folder Role

```text
benchmark/generators/
  base.py
  martingale_verification.py
  optional_stopping_validity.py
  stopped_process_expectation.py
  hitting_time_expectation.py
```

The family files do not need to exist until that family is being implemented. Each family can also have notebooks in this folder for interactive development.

## Core Interface

Every family generator should inherit from `ProblemGenerator` in `base.py` and implement:

```python
sample_params(seed: int, difficulty: int, split: str) -> dict
generate_problem(params: dict) -> str
generate_reasoning(params: dict) -> str
generate_solution(params: dict) -> dict
```

The inherited `generate_record(...)` method assembles the standard benchmark record.

## Data Flow

```text
seed, difficulty, split
  -> sample_params(...)
  -> generate_problem(params)
  -> generate_reasoning(params)
  -> generate_solution(params)
  -> generate_record(...)
```

`generate_problem` creates the prompt used for both training and evaluation.

`generate_reasoning` creates theorem-aware solution traces for fine-tuning or distillation. It should not be shown in held-out evaluation prompts.

`generate_solution` creates the exact canonical answer used for grading. It should return structured data, not prose.

## Families, Types, and Variants

Each family can contain many problem types and surface variants:

```text
family
  -> problem_type
      -> difficulty
      -> surface_variant
      -> parameters
```

For example:

```text
martingale_verification
  -> quadratic_compensation
      -> variance_given
      -> standard_deviation_given
      -> distribution_given
```

The public methods can dispatch internally:

```python
def generate_problem(self, params):
    if params["problem_type"] == "quadratic_compensation":
        return self._problem_quadratic_compensation(params)
    raise ValueError(...)
```

Keep the private type-specific methods short. If a function becomes painful to debug in a notebook, split out a helper.

## Record Shape

A generated record should look like:

```python
{
    "id": "hitting_time_expectation_dev_000123",
    "family": "hitting_time_expectation",
    "problem_type": "symmetric_boundaries_zero_a",
    "difficulty": 1,
    "split": "dev",
    "seed": 123,
    "params": {...},
    "problem": "...",
    "reasoning": "...",
    "canonical_answer": {"expected_time": "12"},
    "metadata": {...},
}
```

The `params`, `canonical_answer`, and `metadata` fields should be JSON-safe. Exact rational values should be represented as strings such as `"7/3"` at record-export time.

## Notebook Style

When developing in notebooks, keep cells small:

- one function or class method experiment per cell
- one smoke test per cell
- one export step per cell

The goal is easy debugging. The generator class should eventually absorb stable code from the notebook once the logic settles.
