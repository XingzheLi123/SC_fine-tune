"""Small shared helpers for benchmark evaluation notebooks."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import pandas as pd


def load_jsonl_records(data_dir: Path, pattern: str = "*.jsonl") -> list[dict[str, Any]]:
    """Load benchmark records from a directory of JSONL files."""
    records = []
    for path in sorted(data_dir.glob(pattern)):
        with path.open() as f:
            for line in f:
                record = json.loads(line)
                record.setdefault("answer_type", answer_type_from_answer(record["canonical_answer"]))
                records.append(record)
    return records


def balanced_eval_subset(records: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    """Pick a small deterministic subset spread across families, types, and difficulties."""
    if limit is None or limit >= len(records):
        return records

    selected = []
    selected_ids = set()

    sort_key = lambda record: (
        record["family"],
        record["problem_type"],
        record["difficulty"],
        record["id"],
    )

    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for record in sorted(records, key=sort_key):
        key = (record["family"], record["problem_type"], record["difficulty"])
        buckets.setdefault(key, []).append(record)

    while len(selected) < limit:
        added = False
        for key in sorted(buckets):
            if len(selected) >= limit:
                break
            while buckets[key] and buckets[key][0]["id"] in selected_ids:
                buckets[key].pop(0)
            if buckets[key]:
                record = buckets[key].pop(0)
                selected.append(record)
                selected_ids.add(record["id"])
                added = True
        if not added:
            break

    return selected


def default_train_dir(project_root: Path) -> Path:
    """Return the current training dataset directory."""
    return project_root / "benchmark" / "data" / "train"


def default_val_dir(project_root: Path) -> Path:
    """Return the current validation dataset directory."""
    return project_root / "benchmark" / "data" / "val"


def default_test_dir(project_root: Path) -> Path:
    """Return the current fixed test dataset directory."""
    return project_root / "benchmark" / "data" / "test"


def default_dev_dir(project_root: Path) -> Path:
    """Backward-compatible alias for the validation dataset directory."""
    return default_val_dir(project_root)


def default_private_test_dir(project_root: Path) -> Path:
    """Backward-compatible alias for the fixed test dataset directory."""
    return default_test_dir(project_root)


def make_closed_book_prompt(problem: str) -> str:
    """Prompt for closed-book evaluation: problem only, no theorem sheet."""
    return (
        "Return only the final JSON object. Do not explain. "
        "Put it inside <answer>...</answer>.\n\n"
        f"{problem}\n\n"
        "Final answer:\n<answer>"
    )


FINE_TUNE_SYSTEM_MESSAGE = (
    "You solve discrete stochastic-process problems. Give the reasoning, then put "
    "the final JSON answer inside <answer>...</answer>."
)


def make_fine_tuned_chat_messages(problem: str) -> list[dict[str, str]]:
    """Chat messages aligned with the supervised fine-tuning data."""
    return [
        {"role": "system", "content": FINE_TUNE_SYSTEM_MESSAGE},
        {"role": "user", "content": problem},
    ]


def answer_type_from_answer(answer: dict[str, Any] | None) -> str:
    """Classify the answer schema as binary or non-binary."""
    if answer and all(isinstance(value, bool) for value in answer.values()):
        return "binary"
    return "non_binary"


def tolerant_json_loads(text: str) -> dict[str, Any] | None:
    """Parse small JSON objects, allowing a few common model formatting slips."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    repaired = text.strip()
    repaired = re.sub(r":\s*(true|false|null)\"", r": \1", repaired, flags=re.I)
    repaired = re.sub(r":\s*(-?\d+(?:\.\d+)?)\"", r": \1", repaired)
    repaired = repaired.replace("True", "true").replace("False", "false").replace("None", "null")

    try:
        loaded = json.loads(repaired)
    except json.JSONDecodeError:
        return None

    return loaded if isinstance(loaded, dict) else None


def extract_json_object(text: str) -> dict[str, Any] | None:
    """Extract the first JSON object, preferring content inside answer tags."""
    tag_match = re.search(r"<answer>\s*(.*?)\s*</answer>", text, flags=re.S)
    if tag_match:
        text = tag_match.group(1)

    json_matches = re.findall(r"\{.*?\}", text, flags=re.S)
    for json_text in json_matches:
        parsed = tolerant_json_loads(json_text)
        if parsed is not None:
            return parsed

    return None


def normalize_scalar(value: Any) -> str:
    """Normalize scalar answer values for exact-ish grading."""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value)
    return str(value).strip().lower()


def coerce_answer_to_schema(answer: dict[str, Any] | None, canonical: dict[str, Any]) -> dict[str, Any] | None:
    """Map common schema aliases onto the canonical answer key."""
    if answer is None:
        return None
    if set(answer) == set(canonical):
        return answer

    if len(canonical) != 1:
        return answer

    canonical_key = next(iter(canonical))
    aliases = {
        "is_martingale": ["is_martingale", "isMartingale", "martingale", "result", "answer", "boolean"],
        "valid": ["valid", "validity", "is_valid", "is_justified", "justified", "result", "answer", "flag"],
        "expected_time": ["expected_time", "expectation", "value", "answer"],
        "value": ["value", "answer"],
    }

    for key in aliases.get(canonical_key, [canonical_key]):
        if key in answer:
            value = answer[key]
            if canonical_key in {"is_martingale", "valid"} and isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in {"yes", "true", "valid", "martingale"}:
                    value = True
                elif lowered in {"no", "false", "invalid", "not valid", "not martingale"}:
                    value = False
            return {canonical_key: value}

    return answer


def normalize_answer(answer: dict[str, Any] | None) -> dict[str, str] | None:
    """Normalize answer dictionaries for exact-match grading."""
    if answer is None:
        return None
    return {str(key): normalize_scalar(value) for key, value in answer.items()}


def is_correct(predicted: dict[str, Any] | None, canonical: dict[str, Any]) -> bool:
    """Exact-match comparison after lightweight normalization."""
    return normalize_answer(coerce_answer_to_schema(predicted, canonical)) == normalize_answer(canonical)


def rows_to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert raw result rows to a dataframe."""
    df = pd.DataFrame(rows)
    if "answer_type" not in df and "canonical_answer" in df:
        df["answer_type"] = df["canonical_answer"].apply(answer_type_from_answer)
    return df


def summarize_accuracy(df: pd.DataFrame) -> dict[str, Any]:
    """Return a compact metrics dictionary."""
    metrics = {
        "num_records": int(len(df)),
        "num_correct": int(df["correct"].sum()),
        "accuracy": float(df["correct"].mean()),
    }
    if "answer_type" in df:
        by_answer_type = {}
        for answer_type, group in df.groupby("answer_type"):
            by_answer_type[str(answer_type)] = {
                "num_records": int(len(group)),
                "num_correct": int(group["correct"].sum()),
                "accuracy": float(group["correct"].mean()),
            }
        metrics["by_answer_type"] = by_answer_type
    return metrics


def save_results(rows: list[dict[str, Any]], result_dir: Path, metrics: dict[str, Any]) -> tuple[Path, Path, Path]:
    """Save raw outputs, metrics, and a CSV table."""
    result_dir.mkdir(parents=True, exist_ok=True)

    outputs_path = result_dir / "outputs.jsonl"
    metrics_path = result_dir / "metrics.json"
    csv_path = result_dir / "outputs.csv"

    with outputs_path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    rows_to_frame(rows).to_csv(csv_path, index=False)

    with metrics_path.open("w") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)

    return outputs_path, metrics_path, csv_path
