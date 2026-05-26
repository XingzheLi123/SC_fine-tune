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

- `results/baselines/{safe_model_name}_dev_closed_book_api/`

The folder name still says `dev` for historical continuity, but the active notebook uses `benchmark/data/test`.

The full-run cell checkpoints after every completed record by appending to `outputs.jsonl`. On rerun, cached record IDs are skipped model by model. API errors and empty responses are kept in the output table with `api_error` filled in and `correct = False`.

To retry cached failures, set one of these in the notebook before the full run:

- `RERUN_API_ERRORS = True`
- `RERUN_EMPTY_OUTPUTS = True`

The notebook is currently configured for normal safe `Run All` usage:

- `RERUN_API_ERRORS = True`
- `RERUN_EMPTY_OUTPUTS = True`
- `FILL_ONLY_EXISTING_EMPTY_OUTPUTS = False`
- `STOP_MODEL_ON_RATE_LIMIT = True`

That means good cached rows are skipped, cached empty/error rows are retried, and missing rows are run. If a model hits a rate limit, the current row is saved with `api_error`, then the notebook stops that model and moves on.

The full-run cell is also configured for overnight retry passes:

- `MAX_RETRY_PASSES = 100`
- `SLEEP_BETWEEN_PASSES_SECONDS = 300`

At the end of each pass, if any model/question pairs are still unfinished, it waits five minutes and tries again. Keep `caffeinate -dims` running in a terminal so the laptop does not sleep.
