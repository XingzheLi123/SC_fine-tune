# Private Test

This folder contains held-out evaluation records.

`balanced_private_test_v0.jsonl` is a small balanced test slice for early model baselines:

- 12 records total
- 3 records per family
- one difficulty-1, one difficulty-2, and one difficulty-3 record per family
- generated from seeds separate from the dev preview data

Use this split for quick baseline comparisons while iterating. Do not use these records for fine-tuning, teacher generation, prompt tuning, or manual dataset redesign.
