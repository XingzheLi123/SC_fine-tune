# Train Split

Generated split for the stochastic reasoning benchmark.

Records include theorem-aware `reasoning` traces for fine-tuning/distillation. Evaluation prompts should use only `problem`.

This split is theorem-explicit: reasoning traces may state the relevant theorem before applying it. A paired theorem-implicit version lives in `../train_implicit_theorems/`.

96 records include manual surface perturbations of the problem and/or reasoning text. See `../manual_variation_log.md`.

```json
{
  "answer_types": {
    "binary": 240,
    "non_binary": 240
  },
  "difficulties": {
    "1": 160,
    "2": 160,
    "3": 160
  },
  "families": {
    "hitting_time_expectation": 120,
    "martingale_verification": 120,
    "optional_stopping_validity": 120,
    "stopped_process_expectation": 120
  },
  "includes_reasoning": true,
  "notes": "Generated from benchmark/generators. Records include problem, reasoning, and canonical_answer fields.",
  "num_records": 480,
  "problem_types": {
    "biased_boundaries_zero_a": 19,
    "bounded_time_valid": 40,
    "bounded_walk_expectation": 56,
    "centered_walk_basic": 40,
    "exponential_compensation": 15,
    "finite_state_hitting_valid": 20,
    "quadratic_compensation": 65,
    "quadratic_fixed_horizon": 53,
    "stopped_martingale_value": 11,
    "symmetric_boundaries_zero_a": 40,
    "symmetric_shifted_boundaries": 61,
    "unbounded_first_hit_invalid": 60
  },
  "split": "train"
}
```
