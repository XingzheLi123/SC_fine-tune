# Qwen3 1.7B LoRA

Notebook-first LoRA experiment for the primary fine-tuning target.

This folder currently focuses on three active adapters:

- `formula_direct`: trained on `benchmark/data/train_formula_direct/`, validated on `benchmark/data/val_formula_direct/`
- `algorithmic_scaffold`: trained on `benchmark/data/train_algorithmic_scaffold/`, validated on `benchmark/data/val_algorithmic_scaffold/`
- `algorithmic_scaffold_v2`: trained on `benchmark/data/train_algorithmic_scaffold_v2/`, validated on `benchmark/data/val_algorithmic_scaffold_v2/`
- `algorithmic_scaffold_v2_5`: historical biased-hitting intervention; this is the old v3 relabeled after it failed to improve biased hitting and caused spillover dips.
- `algorithmic_scaffold_v3`: trained on `benchmark/data/train_algorithmic_scaffold_v3/`, validated on `benchmark/data/val_algorithmic_scaffold_v3/`
- `algorithmic_scaffold_v3_1`: 10,000 fresh generated examples with v3-style patches for binary martingale/optional-stopping reasoning and v2-style non-binary scaffolds.
- `algorithmic_scaffold_v3_1_lora8`: same v3.1 data, trained as a separate 8-layer LoRA capacity ablation.
- `algorithmic_scaffold_v3_5`: 10,000 fresh generated examples with a field-style biased-hitting pipeline and concise compare-only binary scaffolds.
- `algorithmic_scaffold_v3_5_lora12`: same v3.5 data, trained as a separate 12-layer LoRA capacity ablation.

The older `explicit_theorems` and `implicit_theorems` adapters are kept as historical ablations, but they are intentionally suppressed from the default notebook run to save local training time.

All final adapters should be evaluated on the same frozen test set:

- `benchmark/data/test/`

## Notebook Order

1. `01_prepare_lora_data.ipynb`
   - Converts benchmark records into MLX-LM chat JSONL.
   - Writes `train.jsonl` and `valid.jsonl` for the active formula-direct and algorithmic-scaffold variants.
   - These files are derived artifacts under `data/` and are gitignored.

2. `02_train_lora_adapters.ipynb`
   - Runs `mlx_lm.lora` for each configured adapter in `EXPERIMENTS`.
   - Saves adapters under `results/fine_tunes/qwen3_1_7b_lora/`.
   - Defaults to `EXPERIMENTS_TO_RUN = ["algorithmic_scaffold_v3_5_lora12"]` so local iteration tests whether 12 LoRA layers improve or destabilize the current v3.5 data. Add names back to that list when you want to rerun older adapters.

3. `03_eval_lora_adapters.ipynb`
   - Loads each adapter with the Qwen3 1.7B MLX base model.
   - Evaluates selected adapters on the frozen 60-question test split.
   - Imports saved larger-model baseline outputs and regrades them with the current shared grader.
   - Saves comparison tables split by binary/non-binary answer type, subclass, family, and difficulty.
   - Saves comparison plots for answer type, subclass heatmaps, family splits, and difficulty splits.

For conclusions, treat binary and non-binary scores separately. Overall accuracy is only a quick headline because a binary true/false item and a numeric short-answer item are not equally informative.

Validation cells in `02_train_lora_adapters.ipynb` evaluate on each adapter's matching validation split. Use those validation results to choose LoRA settings before touching the frozen test split.

The same notebook also includes a train-generation diagnostic. It evaluates each adapter on a balanced sample from the training split with the same generation prompt and grader as validation:

- `TRAIN_DIAGNOSTIC_LIMIT = 120`
- results save under `results/fine_tunes/qwen3_1_7b_lora_train_diagnostic/`

Use this to distinguish underfitting from overfitting. If train-generation accuracy is also weak, the adapter has not learned the task. If train-generation accuracy is strong but validation is weak, the adapter is overfitting.

Validation is slower than training because it performs autoregressive generation one problem at a time. The notebook now defaults to the full validation split:

- `VALIDATION_LIMIT = None`
- `MAX_NEW_TOKENS = 512`
- `RESET_VALIDATION_OUTPUTS = True`

Set `VALIDATION_LIMIT = 60` only when you want a quick balanced debugging pass. Validation rows are checkpointed to `outputs.jsonl` after each problem.

## Local Notes

This path uses MLX-LM because it is the most practical local fine-tuning stack for Apple Silicon.

The source-of-truth datasets remain in `benchmark/data/`. The `lora/data/` directory is only an MLX-LM-ready export with the filenames and chat schema expected by `mlx_lm.lora`; regenerate it whenever the benchmark records change.

The formula-direct data variant keeps the same problems and canonical answers as the main train/validation split, but rewrites reasoning to be shorter and more operational: formula, substitution, conclusion, final answer block.

The notebook-first way to regenerate reasoning variants is:

- `benchmark/generators/build_reasoning_variants.ipynb`

The helper-module command is:

```bash
python3 benchmark/generators/build_formula_direct_variant.py
```

The algorithmic-scaffold data variants are larger and more explicit. They use parameter extraction, formula selection, substitution, simplification, and final answer formatting. They are controlled by `benchmark/generators/build_reasoning_variants.ipynb`.

The v2 split targets the main weaknesses from the first scaffold run:

- biased hitting times: explicit `p != q` branch and "do not use the symmetric formula" instruction
- fixed-horizon second moments: arithmetic split into square, variance term, and total
- stopped quadratic martingales: direct use of `E[X_tau^2 - tau] = E[M_tau] = E[M_0]`

The v2.5 split is the earlier biased-hitting intervention. It kept the v2 scaffold elsewhere, but replaced the biased expected-time closed form with a two-martingale-style route:

1. compute `P_x(hit b before 0)`
2. compute `E[X_tau]`
3. use `X_n - (p-q)n` to solve for `E[tau]`

The v3 split is deliberately more conservative. It returns to the v2 training mixture and applies small reasoning patches for recurring mistakes:

- biased hitting: stay on the direct biased finite-interval formula, with explicit warnings not to use the symmetric formula
- quadratic compensation: extract `Var(Y_1)` and compare the proposed `c` to it
- exponential compensation: compare only the proposed denominator factor to `p exp(theta) + q exp(-theta)`
- optional stopping: make the bounded/unbounded hypothesis check and final JSON schema more explicit

The v3.1 split is the current larger candidate. It uses fresh generated examples rather than reusing v2 rows, keeps the v2-style non-binary scaffolds, and applies v3 patches to binary martingale-verification and optional-stopping reasoning. Biased hitting is intentionally not treated as solved in this variant and should be reported separately during evaluation.

The v3.5 split pushes the remaining weaknesses. It keeps the 10,000-record scale, adds a field-style arithmetic pipeline for biased hitting, and makes the binary compensation/validity reasoning more concise and comparison-driven.

The helper-module command is:

```bash
python3 benchmark/generators/build_algorithmic_scaffold_variant.py
```

The algorithmic v1 training split has 3,200 records. The v2, v2.5, and v3 training splits have 4,400 records. The v3.1 and v3.5 training splits have 10,000 records. The matching validation splits stay at 240 records so validation does not become the bottleneck.

Training and validation use reasoning plus a final JSON answer in `<answer>...</answer>`. Validation uses a larger token cap so the model has room to reason and still close the final answer.

The system prompt now explicitly asks the model to end with exactly one final answer block:

```text
Final answer:
<answer>
{...}
</answer>
```

The shared evaluator is intentionally tolerant of format-only slips such as `isMartingale` versus `is_martingale`, `validity` versus `valid`, simple yes/no result fields, tiny JSON quoting mistakes, and obvious key/value pairs inside malformed JSON. Wrong mathematical answers are still marked wrong.

The current training settings are still local-machine friendly, but no longer just a smoke run:

- batch size 1
- 12 LoRA layers for the active `algorithmic_scaffold_v3_5_lora12` run
- gradient accumulation
- gradient checkpointing
- prompt masking
- `ITERS = 1500`

For rigorous retraining, the training notebook currently uses:

- `RESET_ADAPTERS_BEFORE_TRAINING = True`
- `SKIP_IF_ADAPTER_EXISTS = False`

That means `Run All` removes the old local adapter directories before training. Turn the reset off only when you intentionally want to resume or inspect an existing adapter.

If the 1,000-iteration algorithmic-scaffold run improves validation but is still underpowered, the next controlled step is to increase iterations before increasing LoRA layers.
