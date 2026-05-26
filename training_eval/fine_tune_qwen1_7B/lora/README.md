# Qwen3 1.7B LoRA

Notebook-first LoRA experiment for the primary fine-tuning target.

This folder trains two separate adapters:

- `explicit_theorems`: trained on `benchmark/data/train/`, validated on `benchmark/data/val/`
- `implicit_theorems`: trained on `benchmark/data/train_implicit_theorems/`, validated on `benchmark/data/val_implicit_theorems/`

Both adapters should be evaluated on the same frozen test set:

- `benchmark/data/test/`

## Notebook Order

1. `01_prepare_lora_data.ipynb`
   - Converts benchmark records into MLX-LM chat JSONL.
   - Writes `train.jsonl` and `valid.jsonl` for both theorem styles.
   - These files are derived artifacts under `data/` and are gitignored.

2. `02_train_lora_adapters.ipynb`
   - Runs `mlx_lm.lora` twice: once for explicit-theorem data and once for implicit-theorem data.
   - Saves adapters under `results/fine_tunes/qwen3_1_7b_lora/`.

3. `03_eval_lora_adapters.ipynb`
   - Loads each adapter with the Qwen3 1.7B MLX base model.
   - Evaluates both adapters on the frozen 60-question test split.
   - Saves exact-match results and metrics.

## Local Notes

This path uses MLX-LM because it is the most practical local fine-tuning stack for Apple Silicon.

The source-of-truth datasets remain in `benchmark/data/`. The `lora/data/` directory is only an MLX-LM-ready export with the filenames and chat schema expected by `mlx_lm.lora`; regenerate it whenever the benchmark records change.

The initial training settings are intentionally conservative:

- batch size 1
- 4 LoRA layers
- gradient accumulation
- gradient checkpointing
- prompt masking

The first successful run can be short. Once the loop works end to end, increase `ITERS` in the training notebook.
