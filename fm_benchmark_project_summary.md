# Project Summary: Fine-Tuning Small Models for Advanced Stochastic Reasoning

## What this project is

This project builds a contamination-resistant benchmark for advanced stochastic reasoning and uses it to study whether small language models can acquire domain-specific stochastic-calculus and martingale reasoning through low-resource fine-tuning.

The project is not mainly a prompt-engineering exercise. Prompting and API baselines are useful controls, but the central question is whether lightweight adaptation of smaller models produces measurable gains on held-out stochastic reasoning tasks.

The current mathematical scope is a narrow martingale/stopping-time domain chosen for depth and clean grading:

- martingale and stopping-time reasoning
- hitting-time expectations for random walks
- optional-stopping validity checks
- martingale verification
- stopped-process expectations

Ito/SDE and mathematical-finance variants are natural later extensions, but they are deliberately out of scope for the first fine-tuning pass.

The core artifact is the benchmark plus a rigorous evaluation framework and at least one small-model adaptation experiment, most likely supervised fine-tuning or distillation.

## Why this project exists

This project is designed to satisfy four goals at once.

First, it must be impressive under strict compute limits. The available hardware is a MacBook with no dedicated GPU, so the project has to derive its value from domain expertise, benchmark design, evaluation rigor, and measurable results rather than brute-force training.

Second, it should improve the author's profile for research-oriented tech roles, especially foundation-model-adjacent roles. The current profile is already strong in mathematics and quant, but lacks a direct high-signal FM-style research artifact.

Third, it should have a realistic path to an arXiv-style preprint. The benchmark itself can be a meaningful contribution if it is well designed, contamination-aware, and paired with careful empirical analysis.

Fourth, it should be useful as both a public research artifact and a career signal. The ideal outcome is a public benchmark, open-source evaluation code, model comparison results, at least one adapted small model, and a polished write-up.

## Why this is a good fit

This project matches the author's strengths:

- strong background in stochastic analysis, probability, and mathematical finance
- ability to design mathematically nontrivial tasks and verify solutions
- limited compute, but enough technical skill to build robust evaluation pipelines

The barrier to entry comes from mathematical taste and benchmark construction, not hardware.

## Core idea

Build a contamination-resistant benchmark of advanced stochastic reasoning problems, evaluate a mix of strong API models and small open models, then fine-tune or distill into one small local model and compare pre- versus post-adaptation performance.

In short:

benchmark -> synthetic training data -> baseline results -> small-model fine-tuning -> held-out evaluation -> write-up

## What the final project should contain

### 1. Benchmark

A dataset of advanced reasoning problems in one narrow mathematical domain.

The current benchmark has:

- 4 problem families
- 3 difficulty levels
- exact JSON-formatted canonical answers
- automatic grading for binary and non-binary answer types
- generated `train`, `val`, and frozen `test` splits
- theorem-explicit and theorem-implicit train/val variants

The strongest version is to generate questions from private templates or procedural generators with hidden seeds.

### 2. Evaluation engine

A reusable evaluation pipeline that:

- formats prompts consistently
- queries models
- extracts final answers robustly
- grades outputs automatically
- reports metrics by model, family, and difficulty

Preferred metrics include exact match, accuracy by problem family, accuracy by difficulty, and separate reporting for binary versus non-binary tasks.

### 3. Baseline results

The project should benchmark a small but credible set of models before any adaptation.

Suggested baseline mix:

- stronger remote API models for upper-bound comparison
- 1 or 2 small local open models for realistic low-resource baselines

The point is not to benchmark everything. The point is to establish a credible difficulty profile and reveal failure modes.

### 4. One lightweight intervention

After baseline evaluation, the project should include exactly one model-improvement step. The best candidates are:

- supervised fine-tuning on a small open model
- distillation from a stronger remote model into a smaller local model
- verifier-guided reranking as a secondary comparison if time permits

The intervention should be cheap enough to run locally or with modest API cost. The main result should compare the same small model before and after adaptation on a frozen held-out benchmark.

### 5. Results and analysis

The final project should not just report one headline metric. It should include:

- overall performance by model
- performance by problem family and difficulty
- clear examples of systematic failure modes
- a comparison of pre- and post-adaptation results
- a contamination and freshness discussion

## What makes the project research-worthy

This project becomes more than a portfolio demo if it does three things well:

1. Introduces a benchmark that is fresh, mathematically serious, and reasonably contamination-resistant.
2. Produces non-obvious empirical findings about model performance.
3. Shows whether low-resource fine-tuning changes the mathematical behavior of small models, not just their response style.
4. Uses a rigorous evaluation protocol with transparent grading and strong error analysis.

A new training algorithm is not required. A benchmark plus a careful small-model adaptation study is already a plausible preprint if the methodology is clean and the results are nontrivial.

## Working style

The project should be notebook-first. Notebooks are the main place for exploration, dataset inspection, model experiments, plots, and error analysis. Small `.py` files should be used only for helper classes, reusable generators, graders, or utilities that become annoying to duplicate across notebooks.

The current benchmark folder is:

```text
benchmark/
  README.md
  specs/
  generators/
  data/
    train/
    train_implicit_theorems/
    val/
    val_implicit_theorems/
    test/
```

Each folder can contain notebooks for the work naturally associated with that folder. For example, `specs/` can include design notebooks, `generators/` can include generator-development notebooks, and `data/` can include inspection notebooks.

Training and evaluation experiments live together under `training_eval/`, with one folder per concrete experiment. This matches the project workflow: define a model/training setup, run the corresponding evaluation, and save the resulting metrics and raw outputs as a single experiment artifact.

The `test` split is the original 60-question set with existing baseline results. It is frozen and excluded from fine-tuning, teacher generation, and prompt iteration. The larger `train` and `val` splits are for adaptation and development checks.

## Practical execution plan

### Phase 1: Scope

Pick one domain only. The best default is martingale and stopping-time reasoning because it is mathematically deep, controllable, and often easier to grade cleanly than more open-ended topics.

### Phase 2: Benchmark generation

Create a benchmark specification and generate the first version of the dataset.

Current structure:

- 480 train records
- 240 validation records
- 60 frozen test records
- balanced binary/non-binary answer types
- separate theorem-explicit and theorem-implicit train/val variants

Training-style data should be generated separately from the evaluation data. It can use the same broad mathematical families, but should use different seeds and, where possible, different parameter ranges or surface forms.

### Phase 3: Evaluation harness

Build the scoring and model-calling pipeline before tuning anything.

The harness should:

- standardize prompting
- save raw outputs
- extract final answers in a robust format
- compute metrics automatically
- output tables suitable for a paper or README

### Phase 4: Baseline evaluation

Run baseline models on the frozen benchmark and inspect errors carefully.

This stage should answer:

- where do models fail?
- which problem families are hardest?
- do larger or stronger models fail in similar ways?
- does reasoning style affect performance?

### Phase 5: Lightweight adaptation

Choose one fine-tuning-centered intervention and apply it to one small local model.

The most realistic default is either:

- supervised fine-tuning on benchmark-style data
- distillation using outputs from a stronger API model

Retrieval-only prompting can be kept as a comparison, but it should not be the main intervention.

### Phase 6: Post-adaptation evaluation

Re-run the exact same eval pipeline on the same held-out test set.

This stage should measure:

- overall gains
- gains by family
- where the intervention helped most
- where the model still fails badly

### Phase 7: Packaging

Publish the work as a clean repo plus write-up.

The final repo should contain:

- benchmark generation code
- benchmark data or a generation script
- evaluation harness
- baseline and post-adaptation result tables
- methodology notes
- a short paper or preprint draft

## Model strategy

The project should use a hybrid setup.

### Remote models

Use 1 or 2 stronger API models as teacher or upper-bound baselines.

The current remote-baseline lane is Qwen-family first, while still allowing opportunistic large-model comparisons when an endpoint is available.

Default remote references are larger Qwen models through OpenRouter, such as Qwen3 8B, Qwen3 32B, and Qwen3 235B-A22B. DeepSeek or other very large MoE systems can be recorded as upper-bound references rather than fair size-matched baselines.

### Local models

Use a small open model that can run on a MacBook for repeated evaluation and lightweight adaptation.

The current default local model is Qwen3 1.7B. It is the primary baseline and first fine-tuning target. Because the available local machine is a 16GB MacBook Air, the first adaptation pass should prioritize parameter-efficient methods rather than full fine-tuning.

The local model does not need to be frontier-scale. The point is to show measurable gains on a hard benchmark.

## What success looks like

A strong outcome would look like this:

- a benchmark of advanced stochastic reasoning problems with a credible contamination story
- a reusable eval harness with automatic grading
- baseline results across a few strong and small models
- one fine-tuned or distilled small model that improves by a measurable margin
- a write-up strong enough for GitHub, a blog post, or an arXiv preprint

## Short one-sentence description

This project builds a contamination-resistant benchmark for advanced stochastic reasoning and tests whether low-resource fine-tuning can produce measurable reasoning gains in small language models.
