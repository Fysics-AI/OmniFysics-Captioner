#!/usr/bin/env python3
"""Call an OpenAI-compatible OmniFysics endpoint with text and one image."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path
import sys
from typing import Any

import requests


DEFAULT_QUESTION = (
    "Analyze the visible physical scene. Identify the main objects and their "
    "approximate positions, likely materials, contact/support relationships, "
    "stability, likely motion and forces, friction or rigidity, deformation "
    "risks, and useful rough physical parameters. State uncertainty explicitly."
)


def image_url(value: str) -> str:
    if value.startswith(("http://", "https://", "data:")):
        return value
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"image not found: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if not mime.startswith("image/"):
        raise ValueError(f"not a recognized image file: {path}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def build_payload(
    *, model: str, question: str, image: str | None, max_tokens: int
) -> dict[str, Any]:
    if image:
        content: str | list[dict[str, Any]] = [
            {"type": "image_url", "image_url": {"url": image_url(image)}},
            {"type": "text", "text": question},
        ]
    else:
        content = question
    return {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0,
        "max_tokens": max_tokens,
    }


def call_endpoint(
    *, base_url: str, api_key: str, payload: dict[str, Any], timeout: float
) -> dict[str, Any]:
    response = requests.post(
        base_url.rstrip("/") + "/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("choices"):
        raise ValueError("endpoint response has no choices")
    return result


def answer_text(result: dict[str, Any]) -> str:
    answer = result["choices"][0].get("message", {}).get("content")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("endpoint returned an empty answer")
    return answer.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--model", default="omnifysics-phys-sa-2e")
    parser.add_argument("--image", help="Local image path, HTTP URL, or data URL")
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--json", action="store_true", help="Print the full response JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = build_payload(
            model=args.model,
            question=args.question,
            image=args.image,
            max_tokens=args.max_tokens,
        )
        result = call_endpoint(
            base_url=args.base_url,
            api_key=args.api_key,
            payload=payload,
            timeout=args.timeout,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else answer_text(result))
    except (OSError, ValueError, requests.RequestException) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
