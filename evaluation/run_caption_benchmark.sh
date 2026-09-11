#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
MANIFEST=""
OUTPUT="runs/captions.jsonl"
ENDPOINT=""
MODEL="omnifysics-captioner"
WORKERS=4
MAX_TOKENS=4096
ARGS=()
if [[ ${1:-} == "--help" || ${1:-} == "-h" ]]; then
  sed -n '2,12p' "$0"
  echo "Usage: $0 --manifest FILE --output FILE --endpoint URL [options]"
  echo "Options: --model NAME --workers N --max-tokens N --with-audio --api-key-env NAME"
  exit 0
fi
while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest) MANIFEST="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --endpoint) ENDPOINT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --workers) WORKERS="$2"; shift 2 ;;
    --max-tokens) MAX_TOKENS="$2"; shift 2 ;;
    --api-key-env) ARGS+=(--api-key-env "$2"); shift 2 ;;
    --with-audio) ARGS+=(--with-audio); shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
[[ -n "${MANIFEST}" ]] || { echo "Missing --manifest" >&2; exit 2; }
[[ -n "${ENDPOINT}" ]] || { echo "Missing --endpoint" >&2; exit 2; }
ARGS+=(--manifest "${MANIFEST}" --output "${OUTPUT}" --endpoint "${ENDPOINT}" --model "${MODEL}")
ARGS+=(--workers "${WORKERS}" --max-tokens "${MAX_TOKENS}")
exec python "${ROOT}/evaluation/run_caption_benchmark.py" "${ARGS[@]}"
