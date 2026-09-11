# OmniFysics-Captioner Evaluation

This folder contains the public, model-specific caption-generation entrypoint
for the OPC benchmark. It submits videos to one OpenAI-compatible
OmniFysics-Captioner endpoint and writes resumable JSONL captions. It does not
contain private answers, judge credentials, other model endpoints, cluster
paths, or benchmark result files.

The local project has two related benchmark references:

- OPC-Bench Final 8K: the frozen 1,000-video, 8,000-question package used for
  detailed caption-to-QA evaluation.
- Caption Benchmark Suite: the broader unified protocol covering DREAM-1K,
  Daily-Omni, WorldSense, and Video-MME.

The script here is intentionally limited to the shared caption-generation
stage. Use the benchmark owner's private scoring package for gold answers and
judge evaluation.

## Quick Start

Prepare a manifest with one JSON object per line:

    {"video_id": "clip_0001", "video_path": "<video-file-path>"}

Start the model using the deployment instructions in ../inference, then run:

    bash evaluation/run_caption_benchmark.sh \
      --manifest <public-manifest-jsonl> \
      --output <captions-jsonl-output> \
      --endpoint <your-openai-compatible-endpoint> \
      --with-audio

Optional overrides are passed directly with --model, --workers, and
--max-tokens. An API key can be supplied with --api-key-env when the endpoint
requires one.

The output contains only video_id, model, caption, and generation metadata.
Input paths and credentials are never written to the output.

## Reproducibility

The default generation settings are deterministic: temperature 0, top_p 1,
two frames per second, up to 128 frames, and 4096 output tokens. The endpoint
and model are explicit command-line arguments so the same script can be used
with a local service or a private deployment without hard-coded infrastructure.
