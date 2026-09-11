#!/usr/bin/env python3
"""Generate captions for a local video manifest through one model endpoint."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

import requests


PROMPT = (
    "Describe the audiovisual video in detail. Include the chronological "
    "events, visible objects and text, sounds and speech, interactions, "
    "materials, motion, and physical changes. Keep visual and audio evidence "
    "aligned and state uncertainty when needed."
)


def media_uri(path: Path) -> str:
    return path.expanduser().resolve().as_uri()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def endpoint_url(value: str) -> str:
    value = value.rstrip("/")
    if value.endswith("/chat/completions"):
        return value
    return value + "/chat/completions" if value.endswith("/v1") else value + "/v1/chat/completions"


def extract_audio(video: Path, directory: Path) -> Path:
    audio = directory / "audio.wav"
    command = [
        "ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(video),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(audio),
    ]
    subprocess.run(command, check=True)
    return audio


def request_caption(
    row: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    api_key: str | None,
    with_audio: bool,
    max_tokens: int,
) -> dict[str, Any]:
    video_id = str(row.get("video_id") or row.get("id") or row.get("uuid") or "")
    video_value = row.get("video_path") or row.get("path")
    if not video_id or not video_value:
        raise ValueError("manifest rows require video_id and video_path")
    video = Path(str(video_value)).expanduser()
    if not video.is_file():
        raise FileNotFoundError(video)
    content: list[dict[str, Any]] = [
        {"type": "video_url", "video_url": {"url": media_uri(video)}},
        {"type": "text", "text": PROMPT},
    ]
    with tempfile.TemporaryDirectory(prefix="omnifysics_caption_") as temp_dir:
        audio = extract_audio(video, Path(temp_dir)) if with_audio else None
        if audio is not None:
            content.insert(1, {"type": "audio_url", "audio_url": {"url": media_uri(audio)}})
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0,
            "top_p": 1,
            "max_tokens": max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        response = requests.post(endpoint_url(endpoint), json=payload, headers=headers, timeout=1800)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
    return {
        "video_id": video_id,
        "model": model,
        "caption": str(answer).strip(),
        "video_sha256": sha256_file(video),
        "settings": {"temperature": 0, "top_p": 1, "max_tokens": max_tokens, "with_audio": with_audio},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--model", default="omnifysics-captioner")
    parser.add_argument("--api-key-env")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--with-audio", action="store_true")
    args = parser.parse_args()
    api_key = os.environ.get(args.api_key_env) if args.api_key_env else None
    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if args.output.exists():
        for line in args.output.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                existing[item["video_id"]] = item
    pending = [row for row in rows if str(row.get("video_id") or row.get("id") or row.get("uuid")) not in existing]
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        jobs = {
            pool.submit(
                request_caption, row, endpoint=args.endpoint, model=args.model,
                api_key=api_key, with_audio=args.with_audio, max_tokens=args.max_tokens
            ): row
            for row in pending
        }
        for future in concurrent.futures.as_completed(jobs):
            row = jobs[future]
            try:
                item = future.result()
                existing[item["video_id"]] = item
            except Exception as exc:
                failures.append({"video_id": row.get("video_id") or row.get("id") or row.get("uuid"), "error": str(exc)})
            args.output.write_text(
                "".join(json.dumps(existing[key], ensure_ascii=False) + "\n" for key in sorted(existing)),
                encoding="utf-8",
            )
    summary = args.output.with_suffix(".summary.json")
    summary.write_text(json.dumps({"completed": len(existing), "failed": len(failures), "failures": failures}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
