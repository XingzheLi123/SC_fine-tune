# Project Summary: Fine-Tuning Qwen3 1.7B for Stochastic Martingale Reasoning

## Executive Snapshot

This project studies whether a small local language model can acquire useful stochastic-process reasoning through low-resource fine-tuning.

The current focus is a discrete martingale / stopping-time benchmark rather than full stochastic calculus. Ito and SDE questions remain future extensions. The first serious target is Qwen3 1.7B, fine-tuned locally with MLX LoRA on a MacBook Air.

The project has now moved beyond planning. We have:

- generated train/validation/test benchmark splits
- built multiple reasoning-style training variants
- run local and API baselines
- trained many Qwen3 1.7B LoRA adapters
- evaluated fine-tuned adapters on validation and frozen test
- added OOD proof-style stochastic probes
- added hard number-theory proof controls
- built comparison tables and charts split by binary/non-binary answer type

The main result so far:

> Fine-tuning Qwen3 1.7B with algorithmic reasoning scaffolds substantially improves in-distribution stochastic benchmark performance, especially on non-binary computational tasks. The best LoRA adapters move Qwen3 1.7B from 19/60 to 47/60 on the frozen stochastic test set. However, OOD proof-style transfer remains weak: the tuned models improve only slightly on stochastic proof questions and do not become generally better proof models.

The strongest frozen-test fine-tuned result so far is:

```text
Qwen3 1.7B base:                  19/60 = 31.7%
Qwen3 1.7B LoRA v3.5:             47/60 = 78.3%
Qwen3 1.7B LoRA v3.5 lora12:      47/60 = 78.3%
```

This is a large local fine-tuning gain, but still below the strongest API baselines.

## Current Research Question

The project asks:

> Can a small local model be fine-tuned to solve specialized stochastic-process reasoning problems that it initially fails, and do the gains reflect reusable mathematical behavior rather than only benchmark-format imitation?

There are three levels of evidence:

1. In-distribution validation/test performance on generated stochastic benchmark tasks.
2. OOD stochastic proof-style performance on unseen formats.
3. Negative-control proof-style performance on unrelated hard number theory.

The current evidence supports a nuanced answer:

- yes, the model can learn the benchmark task distribution very substantially;
- yes, there is weak domain-specific transfer to stochastic proof-style prompts;
- no, the current fine-tuning does not create broad proof competence;
- no, the gains should not be described as generic mathematical reasoning improvement.

## Repository Structure

The working style is notebook-first. Notebooks are used for dataset preparation, training, evaluation, plots, and analysis. Python files are used for reusable generators and evaluator helpers.

Important folders:

```text
benchmark/
  specs/
  generators/
  data/
    train/
    val/
    test/
    train_algorithmic_scaffold_v*
    val_algorithmic_scaffold_v*
    ood_unseen_format/
    ood_math_control/

training_eval/
  eval_utils.py
  qwen3-1.7B_baseline/
  large_models_baseline/
  fine_tune_qwen1_7B/lora/
  ood_unseen_format/
  ood_math_control/

results/
  baselines/
  fine_tunes/
  ood_unseen_format/
  ood_math_control_number_theory_hard/
```

The source-of-truth benchmark records live under `benchmark/data/`. LoRA-specific exported training files under `training_eval/fine_tune_qwen1_7B/lora/data/` are derived artifacts and are gitignored.

## Benchmark Scope

The mathematical scope is intentionally narrow:

- martingale verification
- optional-stopping validity
- hitting-time expectations for random walks
- stopped-process expectations

The benchmark currently avoids continuous-time stochastic calculus. Ito, SDEs, Brownian motion, and mathematical-finance questions are natural future extensions, but the first version is discrete for better controllability and grading.

## Problem Families

The core benchmark has four families.

### 1. Martingale Verification

Binary tasks asking whether a proposed process is a martingale.

Subclasses include:

- centered random walk
- quadratic compensation
- exponential compensation for biased walks

Canonical answers use:

```json
{"is_martingale": true}
```

or

```json
{"is_martingale": false}
```

### 2. Optional-Stopping Validity

Binary tasks asking whether an optional-stopping step is valid.

Subclasses include:

- bounded stopping times
- unbounded first-hit stopping times
- finite-state hitting-time settings

Canonical answers use:

```json
{"valid": true}
```

or

```json
{"valid": false}
```

### 3. Hitting-Time Expectation

Non-binary computational tasks for random-walk hitting times.

Subclasses include:

- symmetric interval hitting times with lower boundary 0
- shifted symmetric intervals
- biased finite-interval hitting times

Canonical answers use schemas such as:

```json
{"expected_time": "21"}
```

or rational strings such as:

```json
{"expected_time": "15/7"}
```

### 4. Stopped-Process Expectation

Non-binary computational tasks involving expected stopped values and stopped quadratic martingales.

Subclasses include:

- bounded stopped random-walk expectations
- fixed-horizon quadratic expectations
- stopped quadratic martingale values

Canonical answers use schemas such as:

```json
{"value": "2"}
```

## Data Splits

The current benchmark data includes the following main splits.

### Frozen Test Split

The frozen test split is:

```text
benchmark/data/test/
```

It contains 60 records:

- 15 hitting-time expectation
- 15 martingale verification
- 15 optional-stopping validity
- 15 stopped-process expectation

It is balanced by answer type:

- 30 binary
- 30 non-binary

This split is frozen because baseline results have already been computed on it. It should not be used for training, prompt iteration, teacher generation, or model selection.

### Base Train/Validation Splits

The base generated train/validation splits are:

```text
benchmark/data/train/      480 records
benchmark/data/val/        240 records
```

The validation split has 60 records per family.

### Theorem-Explicit and Theorem-Implicit Splits

Early experiments tested whether reasoning traces should explicitly state the underlying theorem.

Splits:

```text
benchmark/data/train/
benchmark/data/train_implicit_theorems/
benchmark/data/val/
benchmark/data/val_implicit_theorems/
```

The explicit version includes theorem statements in reasoning. The implicit version uses the theorem but does not fully state it.

Empirically, the distinction was less important than the reasoning scaffold quality.

### Formula-Direct Split

Formula-direct reasoning compresses each solution into:

- identify formula
- substitute parameters
- simplify
- final answer

Splits:

```text
benchmark/data/train_formula_direct/
benchmark/data/val_formula_direct/
```

This was useful as a contrast, but did not become the best-performing training approach.

### Algorithmic-Scaffold Splits

The algorithmic-scaffold variants became the central training direction.

The key idea is to teach the model a repeatable reasoning pipeline:

1. identify the problem type
2. extract parameters
3. choose the theorem/martingale
4. compute intermediate quantities
5. simplify
6. output the exact JSON answer

Important variants:

```text
train_algorithmic_scaffold/          3,200 records
train_algorithmic_scaffold_v2/       4,400 records
train_algorithmic_scaffold_v2_5/     4,400 records
train_algorithmic_scaffold_v3/       4,400 records
train_algorithmic_scaffold_v3_1/    10,000 records
train_algorithmic_scaffold_v3_5/    10,000 records
```

Matching validation splits stay at 240 records each. Validation was intentionally kept small because local autoregressive validation is much slower than LoRA training.

## Reasoning-Scaffold Experiment History

### Explicit / Implicit Theorem Training

Early training used theorem-explicit and theorem-implicit traces.

Validation results:

```text
explicit_theorems: 90/240 = 37.5%
  binary:      77/120 = 64.2%
  non-binary:  13/120 = 10.8%

implicit_theorems: 104/240 = 43.3%
  binary:      76/120 = 63.3%
  non-binary:  28/120 = 23.3%
```

These results were disappointing. They showed that merely including theorem statements in reasoning traces was not enough. The model often failed due to wrong answer format, weak formula selection, and poor arithmetic execution.

### Formula-Direct Training

Formula-direct training was introduced to reduce rambling and force compact solution steps.

Validation result:

```text
formula_direct: 97/240 = 40.4%
  binary:      63/120 = 52.5%
  non-binary:  34/120 = 28.3%
```

This helped non-binary tasks somewhat relative to theorem-explicit training, but it was not close to the desired level.

### Algorithmic Scaffold v1

The first algorithmic scaffold expanded training to 3,200 records and emphasized structured solution pipelines.

This was the first strong signal that the model needed procedural reasoning traces rather than theorem-name exposure.

### Algorithmic Scaffold v2

The v2 split expanded to 4,400 records and targeted weaknesses in:

- biased hitting times
- fixed-horizon quadratic expectations
- stopped quadratic martingales

Validation result:

```text
algorithmic_scaffold_v2: 187/240 = 77.9%
  binary:      87/120 = 72.5%
  non-binary: 100/120 = 83.3%
```

This was the first genuinely strong LoRA result. It also revealed an odd pattern: non-binary tasks could outperform binary tasks, partly because binary schema/format mistakes and true/false ambiguity were distorting evaluation.

### Algorithmic Scaffold v2.5

The old v3 was relabeled v2.5. It tried to fix biased hitting by pushing a different biased-boundary route, but it changed both the biased-hitting scaffold and the training mixture.

Outcome:

- it did not clearly solve biased hitting;
- it caused spillover dips in other categories;
- it was kept as a historical ablation rather than a recommended variant.

### Algorithmic Scaffold v3

The conservative v3 tried to patch common reasoning mistakes while keeping the v2 idea mostly intact.

It improved some binary behavior but introduced brittleness in some non-binary categories.

### Algorithmic Scaffold v3.1

The v3.1 split used 10,000 fresh generated examples. It kept v2-style non-binary scaffolds and applied more targeted patches to binary martingale/optional-stopping reasoning.

The 8-layer LoRA run was:

```text
algorithmic_scaffold_v3_1_lora8: 210/240 = 87.5%
  binary:      104/120 = 86.7%
  non-binary:  106/120 = 88.3%
```

This was a major improvement. It suggested that more examples plus sharper binary scaffolds helped, without needing to inflate validation size.

### Algorithmic Scaffold v3.5

The v3.5 split became the strongest default. It used 10,000 records and introduced:

- a field-style arithmetic pipeline for biased hitting;
- concise compare-only scaffolds for binary compensation/validity tasks;
- less verbose but more disciplined reasoning;
- a stronger emphasis on exact JSON final-answer discipline.

Validation result for the 10-layer v3.5 adapter:

```text
algorithmic_scaffold_v3_5: 221/240 = 92.1%
  binary:      110/120 = 91.7%
  non-binary:  111/120 = 92.5%
```

### Algorithmic Scaffold v3.5 LoRA-12

We then tested whether more LoRA layers would help. The v3.5_lora12 adapter used the same v3.5 data but 12 LoRA layers.

Validation result:

```text
algorithmic_scaffold_v3_5_lora12: 221/240 = 92.1%
  binary:      108/120 = 90.0%
  non-binary:  113/120 = 94.2%
```

This did not improve overall validation accuracy, but shifted performance:

- slightly better non-binary validation
- slightly worse binary validation
- more schema weirdness in some outputs

The 10-layer v3.5 adapter remains the cleaner default, while v3.5_lora12 is a useful capacity ablation.

## Fine-Tuning Setup

The local fine-tuning target is:

```text
Qwen/Qwen3-1.7B-MLX-bf16
```

Training is done with MLX-LM LoRA on Apple Silicon.

Current active LoRA hyperparameters:

```text
ITERS = 1500
BATCH_SIZE = 1
GRAD_ACCUMULATION_STEPS = 8
LEARNING_RATE = 1e-5
MASK_PROMPT = true
GRAD_CHECKPOINT = true
```

Layer ablations:

```text
algorithmic_scaffold_v3_5:          10 LoRA layers
algorithmic_scaffold_v3_5_lora12:   12 LoRA layers
```

Adapter weights are saved under:

```text
results/fine_tunes/qwen3_1_7b_lora/<adapter_name>/adapters/
```

For example:

```text
results/fine_tunes/qwen3_1_7b_lora/algorithmic_scaffold_v3_5/adapters/
results/fine_tunes/qwen3_1_7b_lora/algorithmic_scaffold_v3_5_lora12/adapters/
```

## Grading and Evaluation

All current evaluations use:

```text
training_eval/eval_utils.py
GRADING_POLICY = schema_tolerant_exact_match_v2
```

The grader extracts the final answer from:

```text
<answer>
{...}
</answer>
```

and compares the resulting JSON object to the canonical answer after lightweight normalization.

The grader is deliberately tolerant of harmless binary-schema variations, such as:

- `isJustified`
- `is_validated`
- `isMartingale`
- bare `true` / `false` answer blocks
- yes/no strings where the canonical schema is binary

However, it still marks wrong mathematical values wrong.

Important evaluation principle:

> Binary and non-binary tasks must always be reported separately.

Binary true/false tasks are less informative because blind guessing can achieve 50%. Non-binary exact numeric/rational outputs are a better signal of computational reasoning.

## Baseline Experiments

### Local Base Model

The local base model is Qwen3 1.7B.

Frozen test result:

```text
Qwen3 1.7B base: 19/60 = 31.7%
  binary:      17/30 = 56.7%
  non-binary:   2/30 =  6.7%
```

This was an excellent baseline for the project because it showed:

- the model is not completely useless;
- binary questions are near guessing level;
- non-binary stochastic computations are almost entirely unsolved.

### API Baselines

The main API baselines were run through OpenRouter and saved under `results/baselines/`.

Frozen test results after current regrading:

```text
Qwen3 8B API: 58/60 = 96.7%
  binary:      30/30 = 100.0%
  non-binary:  28/30 =  93.3%

Qwen3 235B-A22B API: 58/60 = 96.7%
  binary:      29/30 = 96.7%
  non-binary:  29/30 = 96.7%

GPT OSS 20B API: 54/60 = 90.0%
  binary:      30/30 = 100.0%
  non-binary:  24/30 =  80.0%

Qwen3 32B API: 49/59 = 83.1%
  binary:      28/30 = 93.3%
  non-binary:  21/29 = 72.4%
```

DeepSeek V4 Flash has only 2 saved test rows in the current result folder, so it should be treated as incomplete:

```text
DeepSeek V4 Flash API: 0/2 saved test rows
```

The larger-model results show that the frozen test set is solvable for strong models, but nontrivial for small local models.

## Fine-Tuned Frozen-Test Results

Final LoRA adapters were evaluated on the frozen 60-question test split.

The main comparison table:

```text
Qwen3 1.7B base:                         19/60 = 31.7%
  binary:      17/30 = 56.7%
  non-binary:   2/30 =  6.7%

LoRA algorithmic_scaffold_v2:             37/60 = 61.7%
  binary:      20/30 = 66.7%
  non-binary:  17/30 = 56.7%

LoRA algorithmic_scaffold_v3_1_lora8:     45/60 = 75.0%
  binary:      24/30 = 80.0%
  non-binary:  21/30 = 70.0%

LoRA algorithmic_scaffold_v3_5:           47/60 = 78.3%
  binary:      24/30 = 80.0%
  non-binary:  23/30 = 76.7%

LoRA algorithmic_scaffold_v3_5_lora12:    47/60 = 78.3%
  binary:      25/30 = 83.3%
  non-binary:  22/30 = 73.3%
```

The strongest fine-tuned local models are still below Qwen3 8B and Qwen3 235B, but they close a large amount of the gap from the 1.7B base.

### Frozen-Test Subclass Notes

Important subclass behavior:

- `centered_walk_basic` became easy for all models, including base.
- `quadratic_compensation` was also easy for the base model, but other binary optional-stopping categories were not.
- `bounded_time_valid` improved from 0/5 for base to 5/5 for v3.5 and v3.5_lora12.
- `symmetric_boundaries_zero_a` improved from 0/5 for base to 5/5 for v3.5 and v3.5_lora12.
- `symmetric_shifted_boundaries` improved from 0/5 for base to 5/5 for v3.5 and v3.5_lora12.
- `quadratic_fixed_horizon` improved from 0/6 for base to 5/6 for v3.5 and v3.5_lora12.
- `bounded_walk_expectation` improved from 2/9 for base to 7/9 for v3.5 and v3.5_lora12.

The remaining major weakness is biased hitting:

```text
biased_boundaries_zero_a on frozen test:
Qwen3 1.7B base:              0/5
LoRA v2:                      0/5
LoRA v3.1_lora8:              0/5
LoRA v3.5:                    1/5
LoRA v3.5_lora12:             0/5
Qwen3 8B API:                 4/5
Qwen3 235B-A22B API:          5/5
```

This is important because validation had suggested biased hitting was improving. On the frozen test, biased hitting remains the most important local-model failure mode.

## OOD Stochastic Proof-Style Probe

To test whether the LoRA adapters learned anything beyond benchmark surface format, we created:

```text
benchmark/data/ood_unseen_format/
```

This is not part of the official train/val/test benchmark.

It contains 20 hand-written non-binary proof/derivation-style stochastic questions using the same martingale ideas but unseen prompt formats.

Examples include:

- proof-style exit probability derivations
- proof-style expected hitting time derivations
- biased hitting derivations via exponential martingales
- derivation of drift compensation
- derivation of quadratic compensation coefficients
- stopped-value proofs using optional stopping

OOD stochastic proof results:

```text
Qwen3 1.7B base:                  2/20 = 10%
LoRA algorithmic_scaffold_v2:     5/20 = 25%
LoRA algorithmic_scaffold_v3_5:   4/20 = 20%
LoRA v3_5_lora12:                3/20 = 15%
```

Interpretation:

- The tuned models improve slightly over base.
- The improvement is weak and uneven.
- The model learned some local stochastic moves, but not robust proof-style stochastic reasoning.
- The current training data mostly teaches benchmark-task execution, not flexible proof recomposition.

## Hard Number-Theory Proof Control

To avoid mistaking generic proof ability for stochastic-domain transfer, we created a negative-control set:

```text
benchmark/data/ood_math_control/
```

The current version contains 20 non-binary hard elementary number-theory proof questions:

- CRT with three moduli
- multiplicative orders
- Carmichael lambda
- extended Euclidean inverse
- modular powers
- p-adic valuations
- trailing zeros in non-decimal base
- quadratic congruence solution counts
- quadratic residue counts
- Mobius function
- divisor-counting and divisor-sum functions
- Legendre symbol

Difficulty split:

```text
difficulty 3: 15 questions
difficulty 4:  5 questions
```

Hard number-theory control results:

```text
Qwen3 1.7B base:                  14/20 = 70%
LoRA algorithmic_scaffold_v3_5_lora12: 12/20 = 60%
LoRA algorithmic_scaffold_v2:     11/20 = 55%
LoRA algorithmic_scaffold_v3_5:   10/20 = 50%
```

This is a striking control result.

The base model is far better at hard proof-style number theory than at stochastic proof-style questions. This likely reflects pretraining: number theory patterns are abundant in textbooks, contest solutions, and online math data, while optional-stopping/martingale proof patterns are much rarer.

The LoRA adapters do not improve number-theory control performance; they reduce it. This suggests:

- the stochastic LoRA did not make the model generally better at proof-style mathematics;
- the fine-tuning caused some domain specialization / interference;
- the small stochastic OOD gain is more plausibly domain-specific than generic formatting improvement.

## Main Empirical Findings So Far

### 1. The Base Model Is Very Weak on Non-Binary Stochastic Computation

Qwen3 1.7B base gets:

```text
non-binary frozen test: 2/30 = 6.7%
```

This is the strongest motivation for fine-tuning. The base model can sometimes classify binary martingale/OST facts, but it almost never executes exact stochastic computations correctly.

### 2. Reasoning Scaffold Quality Matters More Than Theorem Naming

The theorem-explicit vs theorem-implicit experiments showed that merely stating the theorem is not enough.

The model needed:

- parameter extraction
- explicit formula selection
- stable intermediate variables
- arithmetic discipline
- final JSON schema discipline

The algorithmic scaffolds were far more effective than theorem-name exposure.

### 3. More and Better Data Helped

Moving from small theorem-explicit data to 10,000-record algorithmic-scaffold data gave the biggest gains.

Validation progression:

```text
explicit_theorems:              37.5%
implicit_theorems:              43.3%
formula_direct:                 40.4%
algorithmic_scaffold_v2:        77.9%
algorithmic_scaffold_v3_1_lora8:87.5%
algorithmic_scaffold_v3_5:      92.1%
```

This strongly suggests the project is not just measuring prompt engineering. The model behavior changed substantially after fine-tuning.

### 4. The Best Validation Model Is Not Unambiguously the Best Test Model

On validation:

```text
v3.5:         221/240 = 92.1%
v3.5_lora12: 221/240 = 92.1%
```

On frozen test:

```text
v3.5:         47/60 = 78.3%
v3.5_lora12: 47/60 = 78.3%
```

The two are tied overall on test, but split differently:

- v3.5 has better non-binary test accuracy: 23/30 vs 22/30
- v3.5_lora12 has better binary test accuracy: 25/30 vs 24/30

Given the greater importance of non-binary tasks, v3.5 remains the cleaner default.

### 5. Biased Hitting Remains the Key Failure Mode

Despite targeted scaffolds, biased finite-interval hitting is still the hardest local-model subclass.

Validation improved, but frozen-test biased hitting remained weak:

```text
v3.5 on biased_boundaries_zero_a: 1/5
v3.5_lora12 on biased_boundaries_zero_a: 0/5
```

This suggests the model has not robustly internalized the exponential-martingale / drift-martingale pipeline.

### 6. OOD Transfer Exists but Is Weak

On stochastic proof-style OOD:

```text
base:      2/20
best LoRA: 5/20
```

That is evidence of some transfer, but not proof-level mastery.

The tuned models learned fragments such as:

- variance compensation
- bounded stopped-value logic
- some shifted exit probabilities

They did not learn robust recomposition for:

- biased hitting-time derivations
- full expected-time proof derivations
- choosing and combining multiple martingales in unfamiliar formats

### 7. Number-Theory Control Shows the Gap Is Domain-Specific

The hard number-theory control result is:

```text
Qwen3 1.7B base: 14/20
best LoRA:       12/20
```

This means the model is not generally bad at proof-style math. It is specifically much weaker at stochastic/martingale proof-style math.

This strengthens the benchmark motivation:

> The benchmark targets a domain where small models have much less pretraining fluency than they do for common contest-style number theory.

## Current Best Interpretation

The fairest interpretation is:

1. Qwen3 1.7B has weak prior competence on discrete stochastic-process reasoning.
2. LoRA fine-tuning with structured algorithmic scaffolds gives large in-distribution gains.
3. These gains are not merely format correction; non-binary exact computation improves dramatically.
4. The gains remain distribution-sensitive.
5. The model does not become a generally better mathematical proof model.
6. Some limited stochastic-domain transfer appears in proof-style OOD tasks.
7. The hard number-theory control suggests this transfer is domain-specific rather than generic proof-format learning.

## What Can Be Claimed Carefully

Safe claim:

> Low-resource LoRA fine-tuning on structured stochastic-process reasoning traces substantially improves Qwen3 1.7B on a held-out discrete martingale benchmark, from 31.7% to 78.3% overall and from 6.7% to 76.7% on non-binary computational tasks for the best 10-layer v3.5 adapter.

Safe claim:

> The improvement is strongest in-distribution and weaker on proof-style OOD prompts.

Safe claim:

> Hard number-theory controls show that the base model is already much stronger on common proof-style number theory than on stochastic-process proof reasoning.

Safe claim:

> The fine-tuned stochastic adapters do not improve unrelated number-theory proof performance and may slightly degrade it, suggesting domain-specific specialization.

Claim to avoid:

> The fine-tuned model has learned general stochastic calculus.

Claim to avoid:

> The fine-tuned model has become broadly better at mathematical proof.

Claim to avoid:

> The benchmark proves deep reasoning rather than benchmark-pattern learning.

The correct framing is narrower and stronger:

> The project demonstrates measurable domain-specific adaptation of a small model to a difficult, underrepresented stochastic reasoning distribution, with clear limits on OOD proof transfer.

## Current Weaknesses and Open Questions

### 1. Frozen Test Size

The frozen test split has only 60 questions. This was practical and useful for early baselines, but future work should create a larger frozen test set.

However, because existing baselines are computed on the 60-question test, that split should remain frozen and preserved.

### 2. Biased Hitting

Biased hitting remains the hardest non-binary subclass for local LoRA models. Future work should either:

- create more diverse biased-hitting training variants;
- add proof-style biased-hitting augmentations;
- isolate biased hitting as a separate diagnostic;
- or explicitly report results with and without biased hitting.

### 3. OOD Stochastic Proof Generalization

Current stochastic OOD proof performance is low. To improve it, future training should include format augmentation:

- direct compute prompt
- proof request
- critique a false proof
- fill in missing theorem step
- derive formula before computation
- choose which martingale applies
- explain why optional stopping applies or fails

This would test whether format augmentation can improve true transfer.

### 4. Larger and Cleaner Test Sets

A future benchmark version should include:

- larger official test set
- non-binary-only reporting track
- separate binary track
- proof-style stochastic OOD track
- negative-control math track

### 5. Statistical Stability

Some observed differences are based on small counts, especially 20-question OOD probes and 5-question subclasses. These are useful signals but should not be overinterpreted.

## Current Best Model Choices

### Best Small Local Adapter

Best default:

```text
Qwen3 1.7B LoRA algorithmic_scaffold_v3_5
```

Reason:

- tied for best frozen-test accuracy
- slightly better non-binary frozen-test accuracy than lora12
- cleaner behavior than 12-layer ablation
- strong validation accuracy

### Useful Ablation

```text
Qwen3 1.7B LoRA algorithmic_scaffold_v3_5_lora12
```

Reason:

- same overall validation/test accuracy
- slightly better non-binary validation
- slightly better binary test
- but more schema weirdness and worse non-binary test

### Historical Baselines

Keep these for analysis:

```text
explicit_theorems
implicit_theorems
formula_direct
algorithmic_scaffold_v2
algorithmic_scaffold_v3_1_lora8
```

They tell the story of how the training approach improved.

## File Map for Results

### Main Baselines

```text
results/baselines/qwen3_1_7b_test_closed_book/
results/baselines/qwen_qwen3_8b_test_closed_book_api/
results/baselines/qwen_qwen3_32b_test_closed_book_api/
results/baselines/qwen_qwen3_235b_a22b_test_closed_book_api/
results/baselines/openai_gpt_oss_20b_free_test_closed_book_api/
```

### LoRA Validation

```text
results/fine_tunes/qwen3_1_7b_lora_validation/
```

### LoRA Frozen Test

```text
results/fine_tunes/qwen3_1_7b_lora_eval/
```

### LoRA / Baseline Comparison Tables

```text
results/fine_tunes/qwen3_1_7b_lora_eval_comparison/
  summary.csv
  by_answer_type.csv
  by_subclass.csv
  by_family.csv
  by_difficulty.csv
  all_outputs_regraded.csv
```

### OOD Stochastic Proof Probe

```text
benchmark/data/ood_unseen_format/
training_eval/ood_unseen_format/
results/ood_unseen_format/
```

### Hard Number-Theory Control

```text
benchmark/data/ood_math_control/
training_eval/ood_math_control/
results/ood_math_control_number_theory_hard/
```

## Current Paper-Style Story

A possible paper narrative:

1. Define a contamination-aware benchmark for discrete martingale reasoning.
2. Show that Qwen3 1.7B is weak, especially on non-binary stochastic computations.
3. Show that strong API models perform well, establishing that the benchmark is solvable.
4. Fine-tune Qwen3 1.7B locally using MLX LoRA.
5. Show that naive theorem-explicit reasoning traces are not enough.
6. Show that algorithmic scaffolds and larger synthetic training sets produce large gains.
7. Report final frozen-test improvement from 19/60 to 47/60.
8. Separate binary and non-binary results to avoid inflated true/false claims.
9. Analyze biased hitting as the main remaining weakness.
10. Add proof-style OOD stochastic probes and hard number-theory controls.
11. Conclude that the model learned useful domain-specific benchmark behavior, with limited OOD stochastic proof transfer and no broad proof improvement.

## Short One-Sentence Description

This project builds a discrete martingale reasoning benchmark and shows that local LoRA fine-tuning can move Qwen3 1.7B from weak baseline performance to strong in-distribution stochastic reasoning, while OOD and control experiments reveal that the gains are domain-specific and still brittle.

