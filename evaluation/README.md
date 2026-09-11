# OmniFysics-Captioner Evaluation

This folder contains the public, model-specific caption-generation entrypoint
for the OPC benchmark. It submits videos to one OpenAI-compatible
OmniFysics-Captioner endpoint and writes resumable JSONL captions. It does not
contain private answers, judge credentials, other model endpoints, cluster
paths, or benchmark result files.

The public evaluation target is OPC-Bench Final 8K: the frozen 1,000-video,
8,000-question package used for detailed caption-to-QA evaluation. Public
questions and choices are included in `data/test.jsonl` and
`data/benchmark.public.jsonl`; gold answers are not released.

The script here is intentionally limited to the shared caption-generation
stage. Use the benchmark owner's private scoring package for gold answers and
judge evaluation.

## Quick Start

Download the public OPC evaluation videos and manifest:

    hf download Fysics-AI/OmniPhysics-Caption_benchmark \
      --repo-type dataset \
      --include "data/eval_manifest.jsonl" "media/eval/*" \
      --local-dir ./OPC-Bench

Start the model using the deployment instructions in `../inference`, then
generate one caption for each of the 1,000 evaluation videos:

    bash evaluation/run_caption_benchmark.sh \
      --manifest ./OPC-Bench/data/eval_manifest.jsonl \
      --data-root ./OPC-Bench \
      --output ./captions.jsonl \
      --endpoint <your-openai-compatible-endpoint> \
      --with-audio

Optional overrides are passed directly with --model, --workers, and
--max-tokens. The fixed media defaults are 2 FPS and 128 frames; override them
with --fps and --num-frames if the benchmark protocol requires another budget.
An API key can be supplied with --api-key-env when the endpoint requires one.

This step generates captions only; it does not run the private answer-key
scoring stage. The output contains only video_id, model, caption, and generation metadata.
Input paths and credentials are never written to the output.

## Answer Scoring

The public dataset deliberately excludes gold answers. If you have the private
OPC answer file, score A-E prediction rows offline:

    python evaluation/score_opc.py \
      --private-answers <private-benchmark-jsonl> \
      --predictions <model-predictions-jsonl> \
      --output-dir <score-output-directory>

The private file must contain the frozen OPC 1K contracts. Predictions must
contain video_id, matching contract_sha256, and one A-E label per question_id.
The previous formal OPC evaluation used gpt-5.6-luna as the reference Judge;
the offline scorer reports the primary Video-Macro Coverage and question/type
breakdowns without calling any API.

## Reproducibility

The default generation settings are deterministic: temperature 0, top_p 1,
two frames per second, up to 128 frames, and 4096 output tokens. The endpoint
and model are explicit command-line arguments so the same script can be used
with a local service or a private deployment without hard-coded infrastructure.
