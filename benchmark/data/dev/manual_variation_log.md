# Manual Variation Log

This dev preview set includes a small number of hand-edited prompt and reasoning variants. The goal is to reduce brittle dependence on the exact generator wording while preserving the original parameters, IDs, canonical answers, and mathematical validity.

The edits are intentionally limited to 12 of 60 dev preview records. Edited records also have `metadata.manual_variation = true`.

After the second variation pass, edited records also have granular tags:

- `metadata.manual_problem_variation = true` if the question prompt was manually changed
- `metadata.manual_reasoning_variation = true` if the reasoning trace was manually changed

The variation set now contains 36 of 60 dev preview records. This is intentionally a mixed set: some records have question-only variation, some reasoning-only variation, and some both.

## Hitting-Time Expectation

- `hitting_time_expectation_dev_004101`
  - Rephrased the prompt as a fair nearest-neighbor walk stopped at endpoints instead of using the default generator sentence.
  - Reworked the reasoning into a finite-interval martingale derivation with the same formula `E[tau] = i(a-i)`.
  - Canonical answer unchanged: `{"expected_time": "6"}`.

- `hitting_time_expectation_dev_004203`
  - Rephrased shifted-boundary problem as visiting two barriers.
  - Reasoning now explicitly translates the interval before applying the symmetric gambler's ruin hitting-time formula.
  - Canonical answer unchanged: `{"expected_time": "12"}`.

- `hitting_time_expectation_dev_004300`
  - Rephrased biased walk prompt using "moves up" and "moves down" language.
  - Reasoning now emphasizes first-step analysis and the boundary-value recurrence.
  - Canonical answer unchanged: `{"expected_time": "43/7"}`.

## Martingale Verification

- `martingale_verification_dev_001101`
  - Rephrased centered random walk prompt as a classification question.
  - Reasoning now directly checks the conditional expectation using the zero-mean increment.
  - Canonical answer unchanged: `{"is_martingale": true}`.

- `martingale_verification_dev_001201`
  - Kept the standard-deviation surface form but changed the wording away from the generator template.
  - Reasoning explicitly converts standard deviation to variance and checks the quadratic compensation.
  - Canonical answer unchanged: `{"is_martingale": true}`.

- `martingale_verification_dev_001301`
  - Rephrased exponential compensation problem with iid `+/-1` increment language.
  - Reasoning now makes the moment-generating denominator mismatch explicit.
  - Canonical answer unchanged: `{"is_martingale": false}`.

## Optional-Stopping Validity

- `optional_stopping_validity_dev_002101`
  - Rephrased the bounded stopping problem as a "legitimate application" question.
  - Reasoning now explicitly checks `tau <= N` before applying bounded optional stopping.
  - Canonical answer unchanged: `{"valid": true}`.

- `optional_stopping_validity_dev_002201`
  - Rephrased the unbounded first-hit case as a proposed solution to assess.
  - Reasoning now stresses that optional stopping needs boundedness or substitute integrability conditions.
  - Canonical answer unchanged: `{"valid": false}`.

- `optional_stopping_validity_dev_002302`
  - Rephrased finite-state absorption case in terms of a walk on a finite set.
  - Reasoning distinguishes bounded stopped process from deterministic bounded stopping time.
  - Canonical answer unchanged: `{"valid": true}`.

## Stopped-Process Expectation

- `stopped_process_expectation_dev_003101`
  - Reworded the stopped expectation prompt around first-visit time `T` and truncated stopping.
  - Reasoning now gives a compact bounded optional stopping argument.
  - Canonical answer unchanged: `{"value": "-3"}`.

- `stopped_process_expectation_dev_003201`
  - Rephrased fixed-horizon square-moment prompt using iid `+/- step` increments.
  - Reasoning now computes the variance from the step size and applies the quadratic martingale.
  - Canonical answer unchanged: `{"value": "29"}`.

- `stopped_process_expectation_dev_003301`
  - Rephrased a difficulty-3 bounded-walk example to avoid default generator wording.
  - Reasoning keeps the same bounded optional stopping argument.
  - Canonical answer unchanged: `{"value": "-2"}`.

## Second Variation Pass

### Hitting-Time Expectation

- `hitting_time_expectation_dev_004100`
  - Changed question only.
  - Rephrased as a fair random walk stopped at endpoints, using less template-like language.
  - Canonical answer unchanged: `{"expected_time": "21"}`.

- `hitting_time_expectation_dev_004102`
  - Changed reasoning only.
  - Reordered the martingale calculation and derived the terminal probability before applying the square martingale.
  - Canonical answer unchanged: `{"expected_time": "9"}`.

- `hitting_time_expectation_dev_004200`
  - Changed both question and reasoning.
  - Rephrased as absorption between two barriers and used a compact shifted-interval derivation.
  - Canonical answer unchanged: `{"expected_time": "3"}`.

- `hitting_time_expectation_dev_004201`
  - Changed question only.
  - Rephrased the walk as being killed at barriers.
  - Canonical answer unchanged: `{"expected_time": "9"}`.

- `hitting_time_expectation_dev_004301`
  - Changed reasoning only.
  - Emphasized first-step equations and contrasted biased hitting time with the symmetric formula.
  - Canonical answer unchanged: `{"expected_time": "22980/2059"}`.

- `hitting_time_expectation_dev_004304`
  - Changed both question and reasoning.
  - Rephrased the biased walk prompt and shortened the recurrence-based solution.
  - Canonical answer unchanged: `{"expected_time": "50/13"}`.

### Martingale Verification

- `martingale_verification_dev_001100`
  - Changed question only.
  - Described the random walk through its step rule instead of summation notation.
  - Canonical answer unchanged: `{"is_martingale": true}`.

- `martingale_verification_dev_001102`
  - Changed reasoning only.
  - Used a direct conditional-mean calculation without the theorem-bank phrasing.
  - Canonical answer unchanged: `{"is_martingale": true}`.

- `martingale_verification_dev_001200`
  - Changed both question and reasoning.
  - Rephrased the compensated-square question and reasoned through one-step drift cancellation.
  - Canonical answer unchanged: `{"is_martingale": true}`.

- `martingale_verification_dev_001204`
  - Changed question only.
  - Used a shorter standard-deviation prompt.
  - Canonical answer unchanged: `{"is_martingale": true}`.

- `martingale_verification_dev_001302`
  - Changed reasoning only.
  - Explained exponential normalization through the one-step moment factor.
  - Canonical answer unchanged: `{"is_martingale": true}`.

- `martingale_verification_dev_001304`
  - Changed both question and reasoning.
  - Rephrased the exponential-martingale check and highlighted the missing probability-weighted normalizer.
  - Canonical answer unchanged: `{"is_martingale": false}`.

### Optional-Stopping Validity

- `optional_stopping_validity_dev_002100`
  - Changed question only.
  - Rephrased the stopping time as the earlier of a deterministic time and a first hit.
  - Canonical answer unchanged: `{"valid": true}`.

- `optional_stopping_validity_dev_002103`
  - Changed reasoning only.
  - Focused the explanation on deterministic boundedness of `tau`.
  - Canonical answer unchanged: `{"valid": true}`.

- `optional_stopping_validity_dev_002200`
  - Changed both question and reasoning.
  - Reframed as assessing whether a proposed solution step should be accepted.
  - Canonical answer unchanged: `{"valid": false}`.

- `optional_stopping_validity_dev_002300`
  - Changed question only.
  - Made the unbounded stopping-time trap less formulaic.
  - Canonical answer unchanged: `{"valid": false}`.

- `optional_stopping_validity_dev_002303`
  - Changed reasoning only.
  - Explained finite-state boundedness using interval notation.
  - Canonical answer unchanged: `{"valid": true}`.

- `optional_stopping_validity_dev_002304`
  - Changed both question and reasoning.
  - Reframed as a proof-validity question and emphasized that the martingale property alone is insufficient.
  - Canonical answer unchanged: `{"valid": false}`.

### Stopped-Process Expectation

- `stopped_process_expectation_dev_003100`
  - Changed question only.
  - Rephrased the task as the expected stopped position.
  - Canonical answer unchanged: `{"value": "2"}`.

- `stopped_process_expectation_dev_003102`
  - Changed reasoning only.
  - Used a terse mean-preservation argument under bounded optional stopping.
  - Canonical answer unchanged: `{"value": "1"}`.

- `stopped_process_expectation_dev_003200`
  - Changed both question and reasoning.
  - Rephrased the fixed-horizon second-moment problem in jump-size language.
  - Canonical answer unchanged: `{"value": "125"}`.

- `stopped_process_expectation_dev_003203`
  - Changed question only.
  - Rephrased the fixed-horizon problem chronologically.
  - Canonical answer unchanged: `{"value": "11"}`.

- `stopped_process_expectation_dev_003300`
  - Changed reasoning only.
  - Used variance decomposition language instead of the theorem statement.
  - Canonical answer unchanged: `{"value": "36"}`.

- `stopped_process_expectation_dev_003304`
  - Changed both question and reasoning.
  - Rephrased the stopped-value prompt and shortened the optional-stopping explanation.
  - Canonical answer unchanged: `{"value": "1"}`.
