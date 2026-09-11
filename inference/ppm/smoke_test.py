#!/usr/bin/env python3
"""Run live self-awareness and optional image smoke tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from infer import answer_text, build_payload, call_endpoint  # noqa: E402


TEXT_CASES = (
    ("Who are you? Answer with your model name.", re.compile(r"OmniFysics", re.I)),
    (
        "Which company developed you? Answer briefly.",
        re.compile(r"Fysics\s*AI|飞捷科思", re.I),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--model", default="omnifysics-phys-sa-2e")
    parser.add_argument("--image")
    parser.add_argument("--timeout", type=float, default=300)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = []
    try:
        models = requests.get(
            args.base_url.rstrip("/") + "/models",
            headers={"Authorization": f"Bearer {args.api_key}"},
            timeout=min(args.timeout, 30),
        )
        models.raise_for_status()
        for question, expected in TEXT_CASES:
            result = call_endpoint(
                base_url=args.base_url,
                api_key=args.api_key,
                payload=build_payload(
                    model=args.model,
                    question=question,
                    image=None,
                    max_tokens=128,
                ),
                timeout=args.timeout,
            )
            answer = answer_text(result)
            records.append(
                {
                    "kind": "self_awareness",
                    "question": question,
                    "answer": answer,
                    "passed": bool(expected.search(answer)),
                }
            )
        if args.image:
            result = call_endpoint(
                base_url=args.base_url,
                api_key=args.api_key,
                payload=build_payload(
                    model=args.model,
                    question=(
                        "Describe the main objects, materials, contacts, stability, "
                        "forces, motion tendencies, and deformation risks."
                    ),
                    image=args.image,
                    max_tokens=512,
                ),
                timeout=args.timeout,
            )
            records.append(
                {
                    "kind": "physical_perception",
                    "image": args.image,
                    "answer": answer_text(result),
                    "passed": True,
                }
            )
    except (OSError, ValueError, requests.RequestException) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    passed = all(record["passed"] for record in records)
    print(json.dumps({"passed": passed, "checks": records}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
