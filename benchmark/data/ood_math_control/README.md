# OOD Math Control Probe

This folder is not part of the official stochastic-process benchmark.

It is a negative-control probe: 20 hand-written non-binary proof-style questions from harder elementary number theory.

Purpose:

- If LoRA improves the stochastic proof-style probe but not this control, that suggests the transfer is somewhat domain-specific.
- If LoRA improves both, the gain may be mostly answer-formatting or generic proof-style behavior.
- If LoRA improves neither, the benchmark gains are probably narrow in-distribution template learning.

All records include explicit `answer_type: "non_binary"` and use the same final-answer contract as the main benchmark.
