# Benchmark

This folder contains the contamination-resistant stochastic reasoning benchmark.

The intended workflow is notebook-first:

- use notebooks inside each folder for exploration, dataset inspection, plots, and error analysis
- use `specs/` for task-family definitions, answer schemas, and grading rules
- use `generators/` for reusable helper classes or functions that are easier to import than duplicate
- use `data/train/`, `data/val/`, and `data/test/` for generated splits

The `test` split should stay frozen and excluded from fine-tuning, teacher generation, prompt iteration, and manual debugging.

Start with specs before generators. Each spec should make the generator nearly mechanical by fixing the problem family, parameter ranges, canonical answer format, grading rule, and split policy.

See `generators/architecture.md` for the shared generator class pattern.

## Current Splits

- `data/train/`: 480 generated training records, including theorem-aware reasoning traces.
- `data/train_implicit_theorems/`: theorem-implicit mirror of train; same questions and answers, but reasoning omits explicit theorem statements.
- `data/val/`: 240 generated validation records for development checks.
- `data/val_implicit_theorems/`: theorem-implicit mirror of val.
- `data/test/`: original 60-question split, kept frozen because baseline results have already been computed on it.

Report binary and non-binary tasks separately. The binary tasks are mainly martingale verification and optional-stopping validity questions; high accuracy there is less impressive than high accuracy on exact numeric/rational outputs.

Some train/val records include manual surface perturbations in the problem and/or reasoning text. These are logged in `data/manual_variation_log.md`; the perturbations are meant to reduce brittle template memorization without changing the canonical answers.
