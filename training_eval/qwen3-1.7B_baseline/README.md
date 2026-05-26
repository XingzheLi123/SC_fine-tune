# Qwen3 1.7B Local Baseline

Primary small-model baseline and likely LoRA fine-tuning target.

Model:

- `Qwen/Qwen3-1.7B`

Dataset:

- all 60 fixed test records in `benchmark/data/test`

Results save to:

- `results/baselines/qwen3_1_7b_dev_closed_book/`

The notebook is set up for local VS Code usage with the project root pinned to this local checkout.

This baseline is the pre-fine-tuning comparison point for experiments in `training_eval/fine_tune_qwen1_7B/`.
