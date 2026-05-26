# Training and Evaluation

Active baseline lanes:

- `qwen3-1.7B_baseline/`: local Hugging Face inference for the primary small model and likely LoRA target.
- `large_models_baseline/`: API inference for whichever larger model endpoints are currently available.
- `fine_tune_qwen1_7B/`: local parameter-efficient fine-tuning workspace for Qwen3 1.7B.

Current datasets:

- train: `benchmark/data/train/`
- theorem-implicit train ablation: `benchmark/data/train_implicit_theorems/`
- validation: `benchmark/data/val/`
- theorem-implicit validation ablation: `benchmark/data/val_implicit_theorems/`
- frozen test: `benchmark/data/test/`

Baseline notebooks evaluate on the frozen 60-question test split. Fine-tuning should use train/val only, then report final results on test.

If the grader changes, use `regrade_saved_outputs.py` to rescore existing `outputs.jsonl` files without rerunning model calls.
