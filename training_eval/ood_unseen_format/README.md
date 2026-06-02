# OOD Unseen-Format Evaluation

This folder evaluates models on the informal 20-question proof-style probe in:

- `benchmark/data/ood_unseen_format/`

The probe is deliberately separate from the official train/val/test benchmark. It is meant to check whether fine-tuning transfers to different presentations of the same martingale ideas.

Run:

1. `ood_unseen_format_eval.ipynb`

The notebook evaluates:

- Qwen3 1.7B base
- selected Qwen3 1.7B LoRA adapters, if their adapter folders exist

Results save under:

- `results/ood_unseen_format/`

The current probe is intentionally non-binary, so accuracy is not inflated by true/false guessing.
