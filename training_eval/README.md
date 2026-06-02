# Training and Evaluation

Active baseline lanes:

- `qwen3-1.7B_baseline/`: local Hugging Face inference for the primary small model and likely LoRA target.
- `large_models_baseline/`: API inference for whichever larger model endpoints are currently available.
- `fine_tune_qwen1_7B/`: local parameter-efficient fine-tuning workspace for Qwen3 1.7B.
- `ood_unseen_format/`: informal proof-style generalization probe for base and fine-tuned models.
- `ood_math_control/`: non-stochastic proof-style negative-control probe.

Current datasets:

- train: `benchmark/data/train/`
- theorem-implicit train ablation: `benchmark/data/train_implicit_theorems/`
- formula-direct train ablation: `benchmark/data/train_formula_direct/`
- larger algorithmic-scaffold train variant: `benchmark/data/train_algorithmic_scaffold/`
- targeted algorithmic-scaffold v2 train variant: `benchmark/data/train_algorithmic_scaffold_v2/`
- biased-hitting-focused algorithmic-scaffold v2.5 train variant: `benchmark/data/train_algorithmic_scaffold_v2_5/`
- conservative patched algorithmic-scaffold v3 train variant: `benchmark/data/train_algorithmic_scaffold_v3/`
- binary-patched algorithmic-scaffold v3.1 train variant: `benchmark/data/train_algorithmic_scaffold_v3_1/`
- pushed algorithmic-scaffold v3.5 train variant: `benchmark/data/train_algorithmic_scaffold_v3_5/`
- validation: `benchmark/data/val/`
- theorem-implicit validation ablation: `benchmark/data/val_implicit_theorems/`
- formula-direct validation ablation: `benchmark/data/val_formula_direct/`
- algorithmic-scaffold validation variant: `benchmark/data/val_algorithmic_scaffold/`
- algorithmic-scaffold v2 validation variant: `benchmark/data/val_algorithmic_scaffold_v2/`
- algorithmic-scaffold v2.5 validation variant: `benchmark/data/val_algorithmic_scaffold_v2_5/`
- algorithmic-scaffold v3 validation variant: `benchmark/data/val_algorithmic_scaffold_v3/`
- algorithmic-scaffold v3.1 validation variant: `benchmark/data/val_algorithmic_scaffold_v3_1/`
- algorithmic-scaffold v3.5 validation variant: `benchmark/data/val_algorithmic_scaffold_v3_5/`
- frozen test: `benchmark/data/test/`
- OOD proof-style probe: `benchmark/data/ood_unseen_format/`
- OOD math control probe: `benchmark/data/ood_math_control/`

Baseline notebooks evaluate on the frozen 60-question test split. Fine-tuning should use train/val only, then report final results on test.

All current baseline and fine-tuned evaluations use the shared `schema_tolerant_exact_match_v2` grader from `training_eval/eval_utils.py`. It accepts harmless binary schema-format variants, such as bare `<answer>false</answer>`, `isJustified`, and `isMartingale`, while still marking wrong mathematical answers wrong.
