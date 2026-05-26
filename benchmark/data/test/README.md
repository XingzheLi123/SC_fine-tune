# Test Split

This is the original 60-question split, retained as the fixed test set because baseline results have already been computed on it.

Do not train on this split. Use `train/` for fine-tuning and `val/` for development checks.

```json
{
  "answer_types": {
    "binary": 30,
    "non_binary": 30
  },
  "difficulties": {
    "1": 20,
    "2": 20,
    "3": 20
  },
  "families": {
    "hitting_time_expectation": 15,
    "martingale_verification": 15,
    "optional_stopping_validity": 15,
    "stopped_process_expectation": 15
  },
  "notes": "Original 60-question split with existing baseline results. Do not train on this split.",
  "num_records": 60,
  "split": "test"
}
```
