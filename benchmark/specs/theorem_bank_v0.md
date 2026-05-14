# Theorem Bank v0

This file records theorem and method statements that may be inserted into generated fine-tuning reasoning traces. Evaluation prompts should not include these statements unless an experiment is explicitly testing open-book theorem access.

## conditional_expectation_martingale_test

An adapted integrable process `(M_n)` is a martingale with respect to `(F_n)` if

```text
E[M_(n+1) | F_n] = M_n
```

for every `n`.

## quadratic_martingale_centered_increments

If

```text
S_n = S_0 + Y_1 + ... + Y_n
```

where the increments are independent of the past, have mean `0`, and have variance `sigma^2`, then

```text
M_n = S_n^2 - n sigma^2
```

is a martingale.

## exponential_martingale_discrete

If

```text
S_n = Y_1 + ... + Y_n
```

has independent increments and

```text
m(theta) = E[exp(theta Y_1)],
```

then

```text
M_n = exp(theta S_n) / m(theta)^n
```

is a martingale whenever `m(theta)` is finite.

## optional_stopping_bounded

If `(M_n)` is a martingale and `tau` is a bounded stopping time, then

```text
E[M_tau] = E[M_0].
```

## optional_stopping_bounded_stopped_process

If `(M_n)` is a martingale and the stopped family `(M_{n wedge tau})` is bounded, then optional stopping applies to the finite-valued stopped limit and gives

```text
E[M_tau] = E[M_0].
```

## first_step_hitting_time_equation

For a nearest-neighbor walk with hitting time `tau` of the boundary set `{0, a}`, define

```text
e_i = E_i[tau].
```

Conditioning on the first step gives

```text
e_i = 1 + p e_(i+1) + q e_(i-1),
```

with boundary values

```text
e_0 = e_a = 0.
```

## symmetric_gambler_ruin_hitting_time

For a simple symmetric random walk started at `i` and stopped when it first hits `0` or `a`,

```text
E_i[tau] = i(a-i).
```
