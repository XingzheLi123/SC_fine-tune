"""Small shared helpers for benchmark evaluation notebooks."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import pandas as pd


def load_jsonl_records(data_dir: Path, pattern: str = "*_preview.jsonl") -> list[dict[str, Any]]:
    """Load benchmark records from a directory of JSONL files."""
    records = []
    for path in sorted(data_dir.glob(pattern)):
        with path.open() as f:
            for line in f:
                records.append(json.loads(line))
    return records


def default_dev_dir(project_root: Path) -> Path:
    """Return the current dev-preview dataset directory."""
    return project_root / "benchmark" / "data" / "dev"


def make_closed_book_prompt(problem: str) -> str:
    """Prompt for closed-book evaluation: problem only, no theorem sheet."""
    return (
        "Solve the following stochastic-process problem. "
        "Return only the requested JSON inside the answer tags.\n\n"
        f"{problem}\n\n"
        "Final answer:\n<answer>"
    )


def extract_json_object(text: str) -> dict[str, Any] | None:
    """Extract the first JSON object, preferring content inside answer tags."""
    tag_match = re.search(r"<answer>\s*(.*?)\s*</answer>", text, flags=re.S)
    if tag_match:
        text = tag_match.group(1)

    json_match = re.search(r"\{.*?\}", text, flags=re.S)
    if not json_match:
        return None

    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return None


def normalize_answer(answer: dict[str, Any] | None) -> dict[str, str] | None:
    """Normalize answer dictionaries for exact-match grading."""
    if answer is None:
        return None
    return {str(key): str(value).lower() if isinstance(value, bool) else str(value) for key, value in answer.items()}


def is_correct(predicted: dict[str, Any] | None, canonical: dict[str, Any]) -> bool:
    """Exact-match comparison after lightweight normalization."""
    return normalize_answer(predicted) == normalize_answer(canonical)


def rows_to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert raw result rows to a dataframe."""
    return pd.DataFrame(rows)


def summarize_accuracy(df: pd.DataFrame) -> dict[str, Any]:
    """Return a compact metrics dictionary."""
    return {
        "num_records": int(len(df)),
        "num_correct": int(df["correct"].sum()),
        "accuracy": float(df["correct"].mean()),
    }


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
