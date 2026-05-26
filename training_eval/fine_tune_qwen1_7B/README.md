# Fine-Tune Qwen 1.7B

Workspace for local parameter-efficient fine-tuning of the primary small model:

- base model: `Qwen/Qwen3-1.7B`
- train data: `benchmark/data/train/` or `benchmark/data/train_implicit_theorems/`
- validation data: `benchmark/data/val/` or `benchmark/data/val_implicit_theorems/`
- held-out test data: `benchmark/data/test/`

The first goal is not to maximize model quality at any cost. The goal is to get a small, local, repeatable adaptation experiment that can be compared against the frozen Qwen3 1.7B baseline and the larger API baselines.

## Candidate Fine-Tuning Structures

### Full Fine-Tuning

Update all model weights.

This is not appropriate for the current setup. It is too memory-heavy for a 16GB MacBook Air and would be overkill for the first experiment.

### LoRA

Freeze the base model and train low-rank adapter matrices on selected linear layers.

This is the standard default for small-model adaptation. It is well supported by PEFT tooling and by MLX on Apple Silicon, easy to explain, and a strong baseline for a research write-up. On a 1.7B model it should be the most reliable local path, especially with small batches, gradient accumulation, short contexts, and a small number of tuned layers.

### QLoRA

Load the base model in low-bit quantized form and train LoRA adapters.

This is attractive on CUDA machines, but the Mac local path is more awkward because the common QLoRA stack is optimized around bitsandbytes/CUDA. It is not the cleanest first local experiment on Apple Silicon.

MLX can train adapters on top of quantized models, so an MLX-flavored QLoRA path is plausible if plain LoRA is too memory-heavy.

### DoRA

A LoRA variant that decomposes weight direction and magnitude.

DoRA can improve quality over LoRA in some settings, but it adds complexity and may increase memory/runtime cost. It is not the first choice for this project unless plain LoRA is already working comfortably.

### VeRA

Freeze shared random projection matrices and train a much smaller set of scaling parameters.

VeRA is a good fit for the project constraints because it trains fewer parameters than LoRA. That makes it appealing for a 16GB MacBook Air and for a clean low-resource adaptation story. The tradeoff is that support may be less universal than LoRA, and it is less standard as a baseline.

The main risk is tooling friction: Hugging Face PEFT supports VeRA, but the smoothest Apple-Silicon training path is usually MLX, where LoRA/QLoRA/DoRA are the better-supported defaults.

## Recommended First Pass

Start with MLX LoRA unless VeRA is immediately painless. It is the most likely route to a complete local loop on a 16GB MacBook Air.

VeRA is still worth testing as the second pass if PEFT-on-MPS behaves well. It matches the research story nicely:

```text
Can a very small adapter budget teach a 1.7B model specialized stochastic reasoning?
```

If plain LoRA is too heavy, try MLX QLoRA before giving up. If LoRA works comfortably, DoRA can be a later quality comparison.

Practical first configuration:

- start with theorem-explicit `train/` and `val/`
- keep context length modest
- train on final-answer-plus-reasoning traces
- save adapters only, not a merged full model
- evaluate on frozen `benchmark/data/test/`
- report binary and non-binary accuracy separately

Then run the same setup on `train_implicit_theorems/` and `val_implicit_theorems/` as an ablation.

## Suggested Notebook Flow

The fine-tuning notebook in this folder should stay notebook-first and minimal:

1. Load train/val JSONL records.
2. Convert each record into supervised chat examples.
3. Load Qwen3 1.7B locally.
4. Attach VeRA or LoRA adapters.
5. Run a tiny smoke train on 8 examples.
6. Run a short pilot train.
7. Save adapter artifacts under `results/fine_tunes/`.
8. Reuse the existing eval utilities on `benchmark/data/test/`.

The first successful run can be tiny. The important thing is a complete loop from data to adapter to held-out evaluation.

The first concrete LoRA implementation lives in `lora/`.
