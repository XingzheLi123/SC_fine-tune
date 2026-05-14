# Martingale and Stopping-Time Benchmark Spec v0

## Scope

This benchmark slice tests compact, gradable stochastic reasoning around discrete-time martingales, stopping times, and optional stopping. The first version should avoid long proof questions and instead ask for final answers in constrained formats that are easy to grade.

The first implementation target is four problem families:

1. martingale verification
2. optional-stopping validity
3. stopped-process expectation
4. hitting-time expectation

These families are deliberately narrow. They cover enough mathematical texture to expose reasoning failures, but they should be simple enough to generate procedurally from parameter tables.

## Global Problem Record

Each generated problem should be representable as one JSON-like record:

```text
{
  "id": "mst_v0_dev_0001",
  "family": "martingale_verification",
  "difficulty": 1,
  "split": "dev",
  "seed": 12345,
  "problem": "...",
  "answer_schema": "...",
  "canonical_answer": {...},
  "metadata": {...}
}
```

The `problem` field should contain the exact prompt shown to the model. The `canonical_answer` field should be machine-gradable and should not require reading the natural-language solution.

## Splits

Use disjoint seeds for each split:

- `train_like`: synthetic fine-tuning and distillation data
- `dev`: prompt, generator, and grading debugging
- `private_test`: frozen held-out evaluation

The `private_test` split must not be used for fine-tuning, teacher generation, prompt selection, example selection, or manual error-driven redesign.

Suggested first sizes:

- `train_like`: 500 to 2,000 examples
- `dev`: 50 to 100 examples
- `private_test`: 100 examples

## Common Prompt Contract

Every problem should request a final answer in a small tagged block:

```text
Final answer:
<answer>
...
</answer>
```

Inside the block, prefer one of:

- `yes` or `no`
- an integer
- a rational number such as `7/3`
- a simple symbolic expression using fixed variable names
- a small JSON object with fixed keys

Avoid unconstrained proof-only answers in v0.

## Family 1: Martingale Verification

### Task

Given a discrete-time process defined from independent increments or a Markov chain, decide whether the process is a martingale with respect to its natural filtration.

### Generator Inputs

- increment distribution with exact rational probabilities
- process form, for example `S_n`, `S_n^2 - n sigma^2`, or `exp(theta S_n) / m(theta)^n`
- filtration statement
- optional bounded time horizon

### Difficulty

- 1: centered random walk, direct expectation check
- 2: polynomial compensation such as `S_n^2 - n sigma^2`
- 3: exponential or affine compensation with non-symmetric increments

### Answer Schema

```text
{"is_martingale": true|false}
```

Optional extension:

```text
{"is_martingale": true|false, "reason_code": "zero_drift|wrong_compensation|correct_compensation|not_adapted"}
```

### Grading

Exact match on `is_martingale`. Use `reason_code` only for diagnostic grading, not primary accuracy.

## Family 2: Optional-Stopping Validity

### Task

Given a martingale or candidate martingale and a stopping time, decide whether a proposed use of optional stopping is justified under stated assumptions.

### Generator Inputs

- base process, usually a random walk or compensated process
- stopping time definition
- claimed identity, such as `E[M_tau] = E[M_0]`
- condition profile: bounded stopping time, integrable stopping time, uniformly integrable stopped process, or missing condition

### Difficulty

- 1: bounded stopping time, valid optional stopping
- 2: invalid unbounded stopping time with tempting but false identity
- 3: valid by stronger condition but not by boundedness

### Answer Schema

```text
{"valid": true|false}
```

Optional extension:

```text
{"valid": true|false, "condition": "bounded|ui|integrable_increments|fails"}
```

### Grading

Exact match on `valid`. The `condition` field is secondary and should be used for error analysis.

## Family 3: Stopped-Process Expectation

### Task

Compute the expectation of a stopped martingale or compensated process at a bounded stopping time.

### Generator Inputs

- finite horizon `N`
- simple stopping time such as `tau = min(T_a, N)`
- martingale `M_n`
- requested value, usually `E[M_tau]`, `E[S_tau]`, or `E[S_tau^2]`

### Difficulty

- 1: direct optional stopping gives the answer immediately
- 2: compute a target expectation by rearranging a compensated martingale
- 3: combine stopping with boundary events or truncation

### Answer Schema

```text
{"value": "rational_or_integer"}
```

Examples:

```text
{"value": "0"}
{"value": "7/3"}
{"value": "N"}
```

### Grading

Parse exact integers and rational numbers. For symbolic answers, restrict variables to names declared in the problem metadata and use symbolic equivalence.

## Family 4: Hitting-Time Expectation

### Task

Compute an expected hitting time or absorption time for a one-dimensional random walk with finite boundaries.

### Generator Inputs

- starting point `i`
- lower and upper absorbing boundaries, usually `0` and `a`
- step probabilities, initially symmetric
- requested quantity such as `E_i[tau]`

### Difficulty

- 1: symmetric walk on `{0, ..., a}` with answer `i(a-i)`
- 2: shifted boundaries or nonzero starting point notation
- 3: biased walk with exact rational probabilities

### Answer Schema

```text
{"expected_time": "rational_or_integer"}
```

### Grading

Parse exact integers and rational numbers. Avoid decimal answers unless the problem explicitly asks for a decimal approximation.

## Contamination Controls

The benchmark should be generated from private seeds and parameterized templates. Public write-ups may describe the family-level logic but should not publish private-test seeds.

For each family, generate train-like and evaluation examples from separate seed ranges. Where possible, change surface forms between splits:

- notation variants, such as `X_n` versus `S_n`
- boundary labels, such as `{0, ..., a}` versus `{L, ..., U}`
- equivalent but different wording for filtrations and stopping times

Do not copy textbook problem statements verbatim.

## v0 Acceptance Criteria

The first benchmark version is acceptable when:

- all four families have at least one working generator path
- every generated record has a canonical answer
- `dev` examples can be graded automatically
- `private_test` examples are generated once and then frozen
- at least 20 examples have been manually spot-checked for mathematical correctness
