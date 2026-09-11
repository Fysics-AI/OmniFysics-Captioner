#!/usr/bin/env python3
"""Run a small self-awareness smoke test against a Captioner endpoint."""

import argparse
import requests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", default="omnifysics-captioner")
    args = parser.parse_args()
    cases = ["你是谁？", "你是由哪家公司研发的？", "请简要说明你能处理哪些模态？"]
    passed = True
    for question in cases:
        response = requests.post(
            args.base_url.rstrip("/") + "/chat/completions",
            json={"model": args.model, "messages": [{"role": "user", "content": question}], "temperature": 0, "max_tokens": 128},
            timeout=300,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
        ok = ("OmniFysics" in answer) and ("飞捷科思" in answer or "Fysics" in answer) if question != cases[2] else bool(answer.strip())
        passed &= ok
        print(f"[{ 'PASS' if ok else 'FAIL' }] {question}\n{answer}\n")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
