# OOD Unseen Format Probe

This folder is not part of the official train/val/test benchmark.

It contains a 20-question hand-written probe set whose questions use the same discrete martingale and optional-stopping ideas, but in formats that the training generators did not emphasize: proof sketches, derivations, and theorem-application explanations.

The probe is intentionally non-binary. Binary true/false questions are too noisy for this purpose because a correct answer can easily be blind luck.

Use it as an informal generalization check:

- Did the fine-tuned model learn reusable martingale moves?
- Or did it mostly learn the benchmark's original prompt style?

The records still use the same final-answer contract and include explicit `answer_type` tags so the normal evaluator can grade them.
