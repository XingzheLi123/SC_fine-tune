"""Small shared helpers for benchmark evaluation notebooks."""

from __future__ import annotations

import json
from pathlib import Path
import re
import ast
from typing import Any

import pandas as pd


GRADING_POLICY = "schema_tolerant_exact_match_v2"


def load_jsonl_records(data_dir: Path, pattern: str = "*.jsonl") -> list[dict[str, Any]]:
    """Load benchmark records from a directory of JSONL files."""
    records = []
    for path in sorted(data_dir.glob(pattern)):
        with path.open() as f:
            for line in f:
                record = json.loads(line)
                if "answer_type" not in record:
                    raise KeyError(f"{path} record {record.get('id')} is missing answer_type")
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
    "You solve discrete stochastic-process problems. Give concise reasoning, then "
    "end with exactly one final answer block: Final answer:\n<answer>\n{...}\n"
    "</answer>. Do not write anything after </answer>."
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
        try:
            loaded = ast.literal_eval(text.strip())
        except (SyntaxError, ValueError):
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

    # Recover obvious boolean answers from malformed or truncated JSON such as
    # {"isMartingale": true, "reasoning": "...", where the object never closes.
    boolean_key_patterns = {
        "is_martingale": r'"is_martingale"\s*:\s*(true|false)',
        "isMartingale": r'"isMartingale"\s*:\s*(true|false)',
        "martingale": r'"martingale"\s*:\s*(true|false)',
        "valid": r'"valid"\s*:\s*(true|false)',
        "validity": r'"validity"\s*:\s*(true|false)',
        "validityFlag": r'"validityFlag"\s*:\s*"?(true|false)"?',
        "validity_flag": r'"validity_flag"\s*:\s*"?(true|false)"?',
        "isValid": r'"isValid"\s*:\s*(true|false)',
        "is_validated": r'"is_validated"\s*:\s*(true|false)',
        "isJustified": r'"isJustified"\s*:\s*(true|false)',
        "is_justified": r'"is_justified"\s*:\s*(true|false)',
        "justified": r'"justified"\s*:\s*(true|false)',
    }
    for key, pattern in boolean_key_patterns.items():
        match = re.search(pattern, text, flags=re.I)
        if match:
            return {key: match.group(1).lower() == "true"}

    # Recover obvious scalar answers from malformed JSON. This is deliberately
    # key-based, so we do not guess numbers from reasoning text.
    scalar_key_patterns = {
        "expected_time": r'"expected_time"\s*:\s*"?([^",}\n]+)"?',
        "expectation": r'"expectation"\s*:\s*"?([^",}\n]+)"?',
        "value": r'"value"\s*:\s*"?([^",}\n]+)"?',
        "answer": r'"answer"\s*:\s*"?([^",}\n]+)"?',
    }
    for key, pattern in scalar_key_patterns.items():
        match = re.search(pattern, text, flags=re.I)
        if match:
            return {key: match.group(1).strip()}

    return None


def extract_answer(text: str, canonical: dict[str, Any]) -> dict[str, Any] | None:
    """Extract an answer, using the canonical schema to recover mild format slips."""
    parsed = extract_json_object(text)
    if parsed is not None:
        return parsed

    if len(canonical) != 1:
        return None

    key = next(iter(canonical))
    value = canonical[key]
    if isinstance(value, bool):
        tag_match = re.search(r"<answer>\s*(.*?)\s*</answer>", text, flags=re.S | re.I)
        answer_text = tag_match.group(1).strip() if tag_match else text.strip()
        bare_boolean = re.fullmatch(r'["\']?\s*(true|false|yes|no)\s*["\']?', answer_text, flags=re.I)
        if bare_boolean:
            token = bare_boolean.group(1).lower()
            return {key: token in {"true", "yes"}}

        if key == "is_martingale":
            yes_patterns = [
                r"\bis\s+(?:a\s+)?martingale\b",
                r"\bmartingale\s*[:=]\s*true\b",
                r"\banswer\s*[:=]\s*true\b",
            ]
            no_patterns = [
                r"\bis\s+not\s+(?:a\s+)?martingale\b",
                r"\bnot\s+(?:a\s+)?martingale\b",
                r"\bmartingale\s*[:=]\s*false\b",
                r"\banswer\s*[:=]\s*false\b",
            ]
        elif key == "valid":
            yes_patterns = [
                r"\bis\s+justified\b",
                r"\bis\s+valid\b",
                r"\bvalid\s*[:=]\s*true\b",
                r"\bjustified\s*[:=]\s*true\b",
                r"\bisjustified\s*[:=]\s*true\b",
                r"\banswer\s*[:=]\s*true\b",
            ]
            no_patterns = [
                r"\bis\s+not\s+justified\b",
                r"\bnot\s+justified\b",
                r"\bis\s+invalid\b",
                r"\bvalid\s*[:=]\s*false\b",
                r"\bjustified\s*[:=]\s*false\b",
                r"\bisjustified\s*[:=]\s*false\b",
                r"\banswer\s*[:=]\s*false\b",
            ]
        else:
            return None

        lower_text = text.lower()
        no_hit = any(re.search(pattern, lower_text) for pattern in no_patterns)
        yes_hit = any(re.search(pattern, lower_text) for pattern in yes_patterns)
        if no_hit != yes_hit:
            return {key: not no_hit}
        return None

    scalar_patterns = {
        "expected_time": [
            r"expected\s+(?:hitting\s+)?time\s*(?:is|=)\s*([\-0-9/\.]+)",
            r"e\s*\[\s*tau\s*\]\s*(?:is|=)\s*([\-0-9/\.]+)",
            r"e\s*\[\s*\\tau\s*\]\s*(?:is|=)\s*([\-0-9/\.]+)",
        ],
        "value": [
            r"value\s*(?:is|=)\s*([\-0-9/\.]+)",
            r"expectation\s*(?:is|=)\s*([\-0-9/\.]+)",
            r"e\s*\[[^\]]+\]\s*(?:is|=)\s*([\-0-9/\.]+)",
        ],
    }
    for pattern in scalar_patterns.get(key, []):
        matches = re.findall(pattern, text, flags=re.I)
        if matches:
            return {key: matches[-1].strip()}

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
        "is_martingale": [
            "is_martingale",
            "isMartingale",
            "is_martingale_checkbox",
            "martingale",
            "result",
            "answer",
            "boolean",
        ],
        "valid": [
            "valid",
            "validity",
            "validityFlag",
            "validity_flag",
            "isValid",
            "is_valid",
            "is_validated",
            "isJustified",
            "is_justified",
            "justified",
            "result",
            "answer",
            "flag",
        ],
        "expected_time": ["expected_time", "expectation", "value", "answer"],
        "value": ["value", "answer"],
    }

    for key in aliases.get(canonical_key, [canonical_key]):
        if key in answer:
            value = answer[key]
            if canonical_key in {"is_martingale", "valid"} and isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in {"yes", "true", "valid", "martingale"} or lowered.startswith("yes"):
                    value = True
                elif lowered in {"no", "false", "invalid", "not valid", "not martingale"} or lowered.startswith("no"):
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
    if len(df) and "answer_type" not in df:
        raise KeyError("result rows are missing answer_type")
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
