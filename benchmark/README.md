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

Use `generators/build_reasoning_variants.ipynb` when you want notebook-level control over derived reasoning variants such as formula-direct and algorithmic-scaffold splits. The `.py` files beside it are importable helper modules for the notebook.

## Current Splits

- `data/train/`: 480 generated training records, including theorem-aware reasoning traces.
- `data/train_implicit_theorems/`: theorem-implicit mirror of train; same questions and answers, but reasoning omits explicit theorem statements.
- `data/train_formula_direct/`: formula-direct mirror of train; same questions and answers, but reasoning is shortened into formula, substitution, conclusion, and final answer.
- `data/train_algorithmic_scaffold/`: 3,200 generated training records with parameter extraction, formula selection, substitution, simplification, and final answer formatting. Non-binary computational families are oversampled.
- `data/train_algorithmic_scaffold_v2/`: 4,400 generated training records with targeted oversampling and sharper traces for biased hitting times, fixed-horizon second moments, and stopped quadratic martingales.
- `data/train_algorithmic_scaffold_v2_5/`: 4,400 generated training records from the earlier biased-hitting intervention. This is the old v3, relabeled because it changed both the biased-hitting scaffold and the training mixture.
- `data/train_algorithmic_scaffold_v3/`: 4,400 generated training records using the v2 mixture with conservative reasoning patches for common mistakes: biased-hitting formula discipline, quadratic variance comparison, exponential denominator comparison, and optional-stopping final-answer schema.
- `data/train_algorithmic_scaffold_v3_1/`: 10,000 fresh generated training records with v3-style patches for binary martingale verification and optional-stopping validity, and v2-style non-binary scaffolds. Biased hitting remains an explicitly unresolved subclass to report separately.
- `data/train_algorithmic_scaffold_v3_5/`: 10,000 fresh generated training records with a field-style biased-hitting arithmetic pipeline plus concise compare-only scaffolds for binary compensation/validity tasks.
- `data/val/`: 240 generated validation records for development checks.
- `data/val_implicit_theorems/`: theorem-implicit mirror of val.
- `data/val_formula_direct/`: formula-direct mirror of val.
- `data/val_algorithmic_scaffold/`: 240-record validation split with algorithmic-scaffold reasoning; validation size is intentionally not increased.
- `data/val_algorithmic_scaffold_v2/`: 240-record validation split with the v2 scaffold style.
- `data/val_algorithmic_scaffold_v2_5/`: 240-record validation split matching the relabeled v2.5 scaffold style.
- `data/val_algorithmic_scaffold_v3/`: 240-record validation split matching the conservative v3 scaffold style.
- `data/val_algorithmic_scaffold_v3_1/`: 240-record validation split matching the v3.1 binary-only patch style.
- `data/val_algorithmic_scaffold_v3_5/`: 240-record validation split matching the v3.5 scaffold style.
- `data/test/`: original 60-question split, kept frozen because baseline results have already been computed on it.
- `data/ood_unseen_format/`: informal proof/derivation probe using the same martingale ideas in unseen formats. This is separate from train/val/test and should not be treated as an official benchmark split.
- `data/ood_math_control/`: hard number-theory proof/derivation negative-control probe.

Report binary and non-binary tasks separately. The binary tasks are mainly martingale verification and optional-stopping validity questions; high accuracy there is less impressive than high accuracy on exact numeric/rational outputs.

Some train/val records include manual surface perturbations in the problem and/or reasoning text. These are logged in `data/manual_variation_log.md`; the perturbations are meant to reduce brittle template memorization without changing the canonical answers.
