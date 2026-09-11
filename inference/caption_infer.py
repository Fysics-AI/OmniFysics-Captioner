#!/usr/bin/env python3
"""Send a text, image, audio, or video request to a Captioner endpoint."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import requests


def media_url(value: str) -> str:
    if value.startswith(("http://", "https://", "data:", "file:")):
        return value
    return Path(value).expanduser().resolve().as_uri()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", default="omnifysics-captioner")
    parser.add_argument("--video")
    parser.add_argument("--audio")
    parser.add_argument("--image")
    parser.add_argument("--question", default="Describe the scene, objects, interactions, motion, and physical changes in detail.")
    parser.add_argument("--max-tokens", type=int, default=1024)
    args = parser.parse_args()
    content = []
    for key, kind in (("image", "image_url"), ("video", "video_url"), ("audio", "audio_url")):
        value = getattr(args, key)
        if value:
            content.append({"type": kind, kind: {"url": media_url(value)}})
    content.append({"type": "text", "text": args.question})
    payload = {"model": args.model, "messages": [{"role": "user", "content": content}], "temperature": 0, "max_tokens": args.max_tokens}
    try:
        response = requests.post(args.base_url.rstrip("/") + "/chat/completions", json=payload, timeout=900)
        response.raise_for_status()
        print(response.json()["choices"][0]["message"]["content"])
    except (OSError, KeyError, requests.RequestException, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
