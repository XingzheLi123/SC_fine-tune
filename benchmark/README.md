# Benchmark

This folder contains the contamination-resistant stochastic reasoning benchmark.

The intended workflow is notebook-first:

- use notebooks inside each folder for exploration, dataset inspection, plots, and error analysis
- use `specs/` for task-family definitions, answer schemas, and grading rules
- use `generators/` for reusable helper classes or functions that are easier to import than duplicate
- use `data/train_like/`, `data/dev/`, and `data/private_test/` for generated splits

The `private_test` split should be frozen early and excluded from fine-tuning, teacher generation, prompt iteration, and manual debugging.

Start with specs before generators. Each spec should make the generator nearly mechanical by fixing the problem family, parameter ranges, canonical answer format, grading rule, and split policy.

See `generators/architecture.md` for the shared generator class pattern.
