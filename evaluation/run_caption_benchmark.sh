#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
MANIFEST="${MANIFEST:?Set MANIFEST to a public video manifest JSONL}"
OUTPUT="${OUTPUT:-runs/omnifysics_captioner/captions.jsonl}"
ENDPOINT="${ENDPOINT:?Set ENDPOINT to an OpenAI-compatible model endpoint}"
MODEL="${MODEL:-omnifysics-captioner}"
WORKERS="${WORKERS:-4}"
MAX_TOKENS="${MAX_TOKENS:-4096}"

ARGS=(
  --manifest "${MANIFEST}"
  --output "${OUTPUT}"
  --endpoint "${ENDPOINT}"
  --model "${MODEL}"
  --workers "${WORKERS}"
  --max-tokens "${MAX_TOKENS}"
)
if [[ -n "${API_KEY_ENV:-}" ]]; then
  ARGS+=(--api-key-env "${API_KEY_ENV}")
fi
if [[ -n "${WITH_AUDIO:-}" ]]; then
  ARGS+=(--with-audio)
fi
exec python "${ROOT}/evaluation/run_caption_benchmark.py" "${ARGS[@]}"
