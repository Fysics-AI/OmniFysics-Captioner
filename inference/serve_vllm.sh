#!/usr/bin/env bash
set -euo pipefail
: "${MODEL_PATH:?Set MODEL_PATH to the downloaded Hugging Face model directory}"
PYTHON_BIN="${PYTHON_BIN:-python}"
TOKENIZER_PATH="${TOKENIZER_PATH:-${MODEL_PATH}}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-omnifysics-captioner}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
TP="${TP:-4}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-65536}"
MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS:-65536}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-1}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
test -s "${MODEL_PATH}/model.safetensors.index.json" || { echo "Missing model index" >&2; exit 2; }
test -s "${TOKENIZER_PATH}/tokenizer.json" || { echo "Missing tokenizer" >&2; exit 2; }
export PYTHONNOUSERSITE=1
exec "${PYTHON_BIN}" -m vllm.entrypoints.cli.main serve "${MODEL_PATH}" \
  --host "${HOST}" --port "${PORT}" --tokenizer "${TOKENIZER_PATH}" \
  --served-model-name "${SERVED_MODEL_NAME}" --trust-remote-code --dtype bfloat16 \
  --tensor-parallel-size "${TP}" --enable-expert-parallel \
  --max-model-len "${MAX_MODEL_LEN}" --max-num-batched-tokens "${MAX_NUM_BATCHED_TOKENS}" \
  --max-num-seqs "${MAX_NUM_SEQS}" --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
  --limit-mm-per-prompt '{"image":1,"video":1,"audio":1}' \
  --chat-template-content-format openai --reasoning-parser qwen3 \
  --generation-config vllm --disable-custom-all-reduce
