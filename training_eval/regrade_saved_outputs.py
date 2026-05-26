"""Regrade saved benchmark outputs with the current evaluator.

This script does not rerun any model calls. It reads existing `outputs.jsonl`
files, re-extracts answers from `raw_output`, recomputes correctness with the
current formatter-tolerant grader, and writes refreshed metrics/CSV files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from training_eval.eval_utils import extract_json_object, is_correct, rows_to_frame, summarize_accuracy


def load_rows(outputs_path: Path) -> list[dict[str, Any]]:
    with outputs_path.open() as f:
        return [json.loads(line) for line in f]


def regrade_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    regraded = []
    for row in rows:
        row = dict(row)
        predicted = extract_json_object(row.get("raw_output", ""))
        row["predicted_answer"] = predicted
        row["correct"] = is_correct(predicted, row["canonical_answer"])
        regraded.append(row)
    return regraded


def write_rows(rows: list[dict[str, Any]], outputs_path: Path) -> None:
    with outputs_path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def regrade_result_dir(result_dir: Path) -> dict[str, Any]:
    outputs_path = result_dir / "outputs.jsonl"
    metrics_path = result_dir / "metrics.json"
    csv_path = result_dir / "outputs.csv"

    rows = regrade_rows(load_rows(outputs_path))
    metrics = summarize_accuracy(rows_to_frame(rows))

    if metrics_path.exists():
        old_metrics = json.loads(metrics_path.read_text())
        for key in ["model", "provider", "adapter", "dataset", "split_role"]:
            if key in old_metrics:
                metrics[key] = old_metrics[key]
        metrics["regraded_with_current_evaluator"] = True

    write_rows(rows, outputs_path)
    rows_to_frame(rows).to_csv(csv_path, index=False)
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+", type=Path)
    args = parser.parse_args()

    for result_dir in args.result_dirs:
        metrics = regrade_result_dir(result_dir)
        print(f"{result_dir}: {metrics['num_correct']}/{metrics['num_records']} = {metrics['accuracy']:.3f}")


if __name__ == "__main__":
    main()
