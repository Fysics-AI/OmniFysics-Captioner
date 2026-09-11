# OmniFysics-Captioner: Grounding Omni-Modal Understanding in the Physical World for Better Captioning

<p align="center">
  <a href="#paper">📄 Paper</a> •
  <a href="https://github.com/Fysics-AI/OmniFysics-Captioner">🌐 Project Page</a> •
  <a href="https://huggingface.co/datasets/Fysics-AI/OmniPhysics-Caption_benchmark">📊 OPC benchmark &amp; Dataset</a> •
  <a href="https://huggingface.co/Fysics-AI/OmniFysics-Captioner">🤗 Model</a> •
  <a href="#citation">📚 Citation</a>
</p>

---

## Introduction

Building omni-modal models with physical intelligence requires fine-grained supervision that captures physical evidence such as contact, support, deformation, and state transitions. **OmniFysics-Captioner** is an end-to-end, tool-free omni-modal Captioner that produces physics-aware audiovisual captions. It reads raw audio and video in a single forward pass and directly generates captions that describe not only what happens, but also which objects interact, how materials respond, and how states change over time.

**[🤗 Fysics-AI/OmniFysics-Captioner](https://huggingface.co/Fysics-AI/OmniFysics-Captioner)**

In addition, we also propose the following components:

- **📊 Dataset — Daily-Physics 50K:** approximately 50K physics-rich video–caption pairs spanning six physical-event categories and 23 observable subcategories, used to supervise the end-to-end model. A 1,000-video training subset is now available at [🔗 Fysics-AI/OmniPhysics-Caption_benchmark/tree/main/media/train](https://huggingface.co/datasets/Fysics-AI/OmniPhysics-Caption_benchmark/tree/main/media/train).
- **🕵️ Agent — OmniFysics-Agent:** an active-perception agent that first builds a coarse event timeline, then coordinates audio, visual, and physical-perception tools over localized time windows to collect spatiotemporally aligned and traceable cross-modal evidence. Within the Agent, a **physical perception model (PPM)** — fine-tuned on approximately 2M image-level samples — serves as a dedicated tool for perceiving physical cues such as material, contact, and deformation, and for extracting object-interaction and state-change cues. Available at [🔗 Fysics-AI/OmniFysics-Captioner/tree/main/PPM](https://huggingface.co/Fysics-AI/OmniFysics-Captioner/tree/main/PPM).
- **📈 Benchmark — OPC (OmniPhysCap):** a physics-aware, omission-aware benchmark with 1,000 audiovisual clips and 8,000 questions for evaluating whether generated captions retain physical events, object interactions, material responses, state transitions, and cross-modal evidence. Available at [🔗 Fysics-AI/OmniPhysics-Caption_benchmark](https://huggingface.co/datasets/Fysics-AI/OmniPhysics-Caption_benchmark).

## Contents

- [Overview](#overview)
- [Daily-Physics 50K](#daily-physics-50k)
- [OmniFysics-Agent](#omnifysics-agent)
  - [Tool: Physical Perception Model (PPM)](#tool-physical-perception-model-ppm)
    - [PPM Quick Start](#ppm-quick-start)
- [OPC benchmark](#opc-benchmark)
  - [Evaluation Quick Start](#evaluation-quick-start)
- [Model](#model)
  - [Inference code](#inference-code)
  - [Model Quick Start](#model-quick-start)
- [Paper](#paper)
- [Citation](#citation)
- [License](#license)

## Overview

The framework connects physics-rich data construction, active multimodal perception, and tool-free caption generation. Category-Aware Temporal Anchor Aggregation (CATA) discovers and segments clips with observable physical processes. The Agent then collects spatiotemporally aligned and traceable cross-modal evidence from localized intervals, and the end-to-end Captioner learns to produce detailed captions directly from audiovisual input.

<p align="center">
  <img src="fig/case-study.png" alt="Qualitative physical-perception case study" width="100%">
</p>

## Daily-Physics 50K

Daily-Physics 50K is constructed from heterogeneous audiovisual sources through category-aware temporal anchors, clip verification, deduplication, and quality screening. It covers both short-duration clips centered on localized physical interactions and longer videos containing extended physical dynamics, state transitions, and multi-stage processes.

<p align="center">
  <img src="fig/daily-physics-overview.png" alt="Daily-Physics 50K overview" width="100%">
</p>

A 1,000-video open subset of Daily-Physics 50K is available here:

**[🔗 Fysics-AI/OmniPhysics-Caption_benchmark/tree/main/media/train](https://huggingface.co/datasets/Fysics-AI/OmniPhysics-Caption_benchmark/tree/main/media/train)**

## OmniFysics-Agent

OmniFysics-Agent forms a global event timeline from a low-cost audiovisual proxy, locates local intervals that require further inspection, and dynamically orchestrates modality-specific tools. Each observation batch is written to Evidence Memory and drives the next Plan–Execute–Observe–Reflect round, progressively refining modality choice, temporal scope, and question focus. The acquired evidence is spatiotemporally aligned and traceable, and a finalizer organizes it into a temporally coherent caption.

<p align="center">
  <img src="fig/pipeline-overview.png" alt="OmniFysics-Agent pipeline" width="100%">
</p>

### Tool: Physical Perception Model (PPM)

Within OmniFysics-Agent, the PPM focuses on objects and physical phenomena in representative frames, perceiving physical cues such as material, contact, and deformation, and analyzing object interactions, state changes, and their potential outcomes. It is fine-tuned on approximately 2M image-level physical-perception samples to output object-centric, physical-aware evidence that complements the audio and visual tools.

The released PPM checkpoint is available on Hugging Face:

**[🤗 Fysics-AI/OmniFysics-Captioner/PPM](https://huggingface.co/Fysics-AI/OmniFysics-Captioner/tree/main/PPM)**

### PPM Quick Start

Start the PPM image-level service from a local clone of this repository:

    MODEL_PATH=<downloaded-model-directory>/PPM \
      bash inference/ppm/serve_vllm.sh

## OPC benchmark

OmniPhysCap (OPC) is a physics-aware, omission-aware benchmark designed to evaluate how well generated captions retain omni-modal information from audiovisual videos. It systematically assesses whether a caption recovers what happens, which objects interact, how materials respond, and what state or outcome follows. The benchmark contains 1,000 audiovisual clips and 8,000 questions spanning general semantics, temporal relations, audio, audiovisual alignment, and — with dedicated emphasis — physical interactions and outcomes. Each question includes an explicit *Not Mentioned* option, distinguishing omitted evidence from conflicting evidence.

<p align="center">
  <img src="fig/opc-benchmark-results.png" alt="OPC benchmark results" width="360">
</p>

The benchmark and dataset are available on Hugging Face:

**[📊 Fysics-AI/OmniPhysics-Caption_benchmark](https://huggingface.co/datasets/Fysics-AI/OmniPhysics-Caption_benchmark)**

The current release contains the OPC benchmark together with a 1,000-video training subset sampled from Daily-Physics 50K. The complete Daily-Physics 50K release will be linked here when available.

### Evaluation Quick Start

The public evaluation entrypoint generates captions for one OmniFysics-Captioner
endpoint. It does not include private answers, judge credentials, other model
endpoints, or machine-specific paths.

    bash evaluation/run_caption_benchmark.sh \
      --manifest <public-manifest-jsonl> \
      --output <captions-jsonl-output> \
      --endpoint <your-openai-compatible-endpoint> \
      --with-audio

## Model

### OmniFysics-Captioner

OmniFysics-Captioner is an end-to-end, tool-free omni-modal Captioner fine-tuned from Qwen3-Omni on Daily-Physics 50K. It reads raw audio and video in a single forward pass and directly generates physics-aware, detailed captions, amortizing the evidence-acquisition and organization capability of OmniFysics-Agent without requiring external tools at inference.

### Inference code

Inference code is maintained in this GitHub repository under inference/
rather than bundled inside the Hugging Face model directory. Use
inference/serve_vllm.sh to start the service, inference/caption_infer.py
for text, image, audio, or video requests, and inference/smoke_test.py to
verify a running endpoint.

    MODEL_PATH=<downloaded-model-directory> bash inference/serve_vllm.sh
    python inference/caption_infer.py --base-url <your-endpoint> --video <video-file>
    python inference/smoke_test.py --base-url <your-endpoint>

The model checkpoint is available on Hugging Face:

**[🤗 Fysics-AI/OmniFysics-Captioner](https://huggingface.co/Fysics-AI/OmniFysics-Captioner)**

### Model Quick Start

Download the merged checkpoint and start the OpenAI-compatible service:

    hf download Fysics-AI/OmniFysics-Captioner \
      --local-dir ./models/OmniFysics-Captioner
    MODEL_PATH=./models/OmniFysics-Captioner \
      bash inference/serve_vllm.sh

## Paper

Paper and supplementary material: **Coming soon**.

## Citation

```bibtex
@article{qiu2026omnifysicscaptioner,
  title   = {OmniFysics-Captioner: Grounding Omni-Modal Understanding in the Physical World for Better Captioning},
  author  = {Qiu, Kaixiang and Han, Minghao and Liu, Keliang and Liu, Yizhou and Han, Jinghang and Jiang, Yue and Wang, Shunli and Zhang, Lihua and Yang, Dingkang},
  journal = {arXiv preprint},
  year    = {2026}
}
```

## License

The content of this repository is released under the Apache License 2.0 with an additional **non-commercial** restriction: it may be used, reproduced, and distributed for research and educational purposes only. Any commercial use is prohibited without prior written permission from the maintainers. Source videos remain subject to the licenses of their original datasets.
