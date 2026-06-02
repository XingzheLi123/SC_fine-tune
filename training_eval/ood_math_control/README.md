# Hard Number Theory Control Evaluation

This folder evaluates the same base and LoRA models on the negative-control probe in:

- `benchmark/data/ood_math_control/`

The questions are proof-style and non-binary, but they are not stochastic-process questions. The current control set is harder elementary number theory.

Run:

1. `ood_math_control_eval.ipynb`

Results save under:

- `results/ood_math_control_number_theory_hard/`

Interpretation:

- Improvement on `ood_unseen_format/` but not here suggests some stochastic-domain transfer.
- Similar improvement here suggests the LoRA may mostly improve formatting or generic proof-style behavior.
- No improvement here and weak improvement there suggests mostly in-distribution benchmark learning.
