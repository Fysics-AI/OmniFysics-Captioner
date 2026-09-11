#!/usr/bin/env python3
"""Score OPC 1K predictions against a local private answer file.

The private answer file is intentionally not distributed with this repository.
Predictions must contain one row per video with an answers list.
"""

from __future__ import annotations

import argparse
import collections
import json
import statistics
from pathlib import Path
from typing import Any


REFERENCE_JUDGE_MODEL = "gpt-5.6"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not an object")
            rows.append(value)
    return rows


def rate(hit: int, total: int) -> float | None:
    return round(100.0 * hit / total, 4) if total else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-answers", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    contracts = read_jsonl(args.private_answers)
    if len(contracts) != 1000:
        raise ValueError(f"expected the OPC 1K private answer file, got {len(contracts)} videos")
    predictions = read_jsonl(args.predictions)
    by_video = {str(row.get("video_id")): row for row in predictions}
    if len(by_video) != len(predictions):
        raise ValueError("predictions contain duplicate video_id values")
    expected = {str(row["video_id"]) for row in contracts}
    if set(by_video) != expected:
        raise ValueError("prediction video IDs do not match the OPC 1K answer file")

    totals: collections.Counter[str] = collections.Counter()
    by_type: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    per_video = []
    for contract in contracts:
        video_id = str(contract["video_id"])
        prediction = by_video[video_id]
        if prediction.get("contract_sha256") != contract.get("contract_sha256"):
            raise ValueError(f"contract hash mismatch for {video_id}")
        answer_map = {
            str(item.get("question_id")): str(item.get("label") or "").upper()
            for item in prediction.get("answers", [])
        }
        counts: collections.Counter[str] = collections.Counter()
        for question in contract["questions"]:
            question_id = str(question["question_id"])
            label = answer_map.get(question_id, "")
            if label not in "ABCDE":
                outcome = "invalid"
            elif label == question["answer_key"]:
                outcome = "hit"
            elif label == "E":
                outcome = "not_mentioned"
            else:
                outcome = "counter"
            counts[outcome] += 1
            totals[outcome] += 1
            totals["questions"] += 1
            bucket = by_type[str(question["type"])]
            bucket[outcome] += 1
            bucket["questions"] += 1
        per_video.append({
            "video_id": video_id,
            "benchmark_index": contract["benchmark_index"],
            "question_count": len(contract["questions"]),
            "hit": counts["hit"],
            "counter": counts["counter"],
            "not_mentioned": counts["not_mentioned"],
            "invalid": counts["invalid"],
            "coverage": round(100.0 * counts["hit"] / len(contract["questions"]), 4),
        })

    summary = {
        "schema_version": "opc_1k_score_v1",
        "videos": len(per_video),
        "questions": totals["questions"],
        "primary_metric": "video_macro_coverage",
        "reference_judge_model": REFERENCE_JUDGE_MODEL,
        "video_macro_coverage": round(statistics.mean(row["coverage"] for row in per_video), 4),
        "question_micro_coverage": rate(totals["hit"], totals["questions"]),
        "counter_rate": rate(totals["counter"], totals["questions"]),
        "not_mentioned_rate": rate(totals["not_mentioned"], totals["questions"]),
        "invalid_rate": rate(totals["invalid"], totals["questions"]),
        "by_type": {
            key: {
                "questions": value["questions"],
                "coverage": rate(value["hit"], value["questions"]),
                "counter_rate": rate(value["counter"], value["questions"]),
                "not_mentioned_rate": rate(value["not_mentioned"], value["questions"]),
            }
            for key, value in sorted(by_type.items())
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (args.output_dir / "per_video.jsonl").open("w", encoding="utf-8") as handle:
        for row in per_video:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
