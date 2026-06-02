# Large Models Baseline

Generic API baseline notebook for larger reference models.

Current default provider:

- OpenRouter OpenAI-compatible endpoint: `https://openrouter.ai/api/v1`
- Env var: `OPENROUTER_API_KEY`

The default `MODEL_NAMES` list is Qwen-family first:

- `qwen/qwen3-8b`
- `qwen/qwen3-32b`
- `qwen/qwen3-235b-a22b`

DeepSeek or other available endpoints can still be added manually as upper-bound comparisons. Edit `MODEL_NAMES`, run the smoke test, then run the full 60-question frozen test evaluation.

Gemma is intentionally excluded for now because the available endpoint produced verbose non-JSON answers and rate-limit noise, making it an unhelpful baseline for this exact-match setup.

Results save under:

- `results/baselines/{safe_model_name}_test_closed_book_api/`

The notebook is currently configured for rigorous fresh reruns:

- `RESET_OUTPUTS_BEFORE_RUN = True`

That means `Run All` clears old cached API outputs before the smoke/full run. Turn this off only when you want to resume from cached rows.

The full-run cell checkpoints after every completed record by appending to `outputs.jsonl`. When `RESET_OUTPUTS_BEFORE_RUN = False`, cached terminal rows are skipped model by model. API errors are kept in the output table with `api_error` filled in and `correct = False`.

The notebook is currently configured as a serious run with bounded output-error retries:

- no sleep routine
- API failures are saved and not retried
- empty responses and unparsable JSON are marked as `output_error` and retried
- output errors get up to 10 tries before we call it
- rate limits stop the current model for that run

Current settings:

- `RERUN_API_ERRORS = False`
- `RERUN_OUTPUT_ERRORS = True`
- `MAX_OUTPUT_RETRY_PASSES = 10`
- `FILL_ONLY_EXISTING_EMPTY_OUTPUTS = False`
- `STOP_MODEL_ON_RATE_LIMIT = True`

All metrics use the shared `schema_tolerant_exact_match_v1` grader from `training_eval/eval_utils.py`.
