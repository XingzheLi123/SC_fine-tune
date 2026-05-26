# Val Split

Generated split for the stochastic reasoning benchmark.

Records include theorem-aware `reasoning` traces for fine-tuning/distillation. Evaluation prompts should use only `problem`.

This split is theorem-explicit: reasoning traces may state the relevant theorem before applying it. A paired theorem-implicit version lives in `../val_implicit_theorems/`.

48 records include manual surface perturbations of the problem and/or reasoning text. See `../manual_variation_log.md`.

```json
{
  "answer_types": {
    "binary": 120,
    "non_binary": 120
  },
  "difficulties": {
    "1": 80,
    "2": 80,
    "3": 80
  },
  "families": {
    "hitting_time_expectation": 60,
    "martingale_verification": 60,
    "optional_stopping_validity": 60,
    "stopped_process_expectation": 60
  },
  "includes_reasoning": true,
  "notes": "Generated from benchmark/generators. Records include problem, reasoning, and canonical_answer fields.",
  "num_records": 240,
  "problem_types": {
    "biased_boundaries_zero_a": 13,
    "bounded_time_valid": 20,
    "bounded_walk_expectation": 28,
    "centered_walk_basic": 20,
    "exponential_compensation": 11,
    "finite_state_hitting_valid": 7,
    "quadratic_compensation": 29,
    "quadratic_fixed_horizon": 26,
    "stopped_martingale_value": 6,
    "symmetric_boundaries_zero_a": 20,
    "symmetric_shifted_boundaries": 27,
    "unbounded_first_hit_invalid": 33
  },
  "split": "val"
}
```
