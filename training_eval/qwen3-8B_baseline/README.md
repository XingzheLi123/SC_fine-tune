# Qwen3 8B Baseline

Closed-book dev-preview baseline for `Qwen/Qwen3-8B`.

This is the stronger same-family comparison to the `Qwen/Qwen3-1.7B` baseline. It should be run in non-thinking mode first, so the comparison is a general model scaling check rather than a specialized reasoning-mode benchmark.

On a Colab T4, full 8B inference should be much more plausible than full 14B inference. If memory becomes an issue, use a smaller batch size, restart the runtime, or consider a quantized loading pass as a separate experiment.
