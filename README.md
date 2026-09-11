---
license: other
library_name: transformers
base_model:
- Qwen/Qwen3-Omni-30B-A3B-Instruct
tags:
- audiovisual
- video
- captioner
- multimodal
- physical-reasoning
- physics
---

# OmniFysics-Captioner: Grounding Omni-Modal Understanding in the Physical World for Better Captioning

<p align="center">
  <a href="#paper">📄 Paper</a> •
  <a href="https://huggingface.co/datasets/Fysics-AI/OmniPhysics-Caption_benchmark">📊 OPC benchmark &amp; Dataset</a> •
  <a href="#model">🤗 Model</a> •
  <a href="#citation">📚 Citation</a>
</p>

---

## Introduction

Fine-grained perception of multimodal information is critical for advancing human-AI interaction. **OmniFysics-Captioner** is an omni-modal model for producing detailed, low-hallucination audiovisual captions grounded in the physical world. It describes not only what happens, but also which objects interact, how materials respond, and how states change over time.

We introduce **Daily-Physics 50K** for physics-rich caption supervision, **OmniFysics-Agent** for active multimodal evidence acquisition, and a **Physical Perception Model (PPM)** for object properties, contact, support, deformation, motion, and state changes. We further propose **OmniPhysCap (OPC)**, an omission-aware benchmark for evaluating whether generated captions retain physical and cross-modal evidence.

## Highlights

- **Physics-rich supervision:** Daily-Physics 50K contains approximately 50K video-caption pairs spanning six physical-event categories and 23 observable subcategories.
- **Active evidence acquisition:** OmniFysics-Agent coordinates audio, visual, and physical observers over localized time windows before caption synthesis.
- **Physical perception:** PPM provides object-centric evidence about properties, interactions, material responses, and state transitions.
- **Omission-aware evaluation:** OPC contains 1,000 held-out audiovisual clips and 8,000 questions, with an explicit `Not Mentioned` option for omitted evidence.

## Overview

The framework connects physics-rich data construction, active multimodal perception, and tool-free caption generation. Category-aware temporal retrieval identifies clips with observable physical processes. The Agent then gathers source-attributed evidence from localized intervals, and the end-to-end Captioner learns to produce detailed captions directly from audiovisual input.

<p align="center">
  <img src="fig/pipeline-overview.png" alt="OmniFysics-Agent pipeline" width="100%">
</p>

## Daily-Physics 50K

Daily-Physics 50K is constructed from heterogeneous audiovisual sources through category-aware temporal anchors, clip verification, deduplication, and quality screening. It covers brief contacts and collisions as well as longer state transitions and multi-stage physical events.

<p align="center">
  <img src="fig/daily-physics-overview.png" alt="Daily-Physics 50K overview" width="100%">
</p>

## OmniFysics-Agent

OmniFysics-Agent builds a coarse event timeline, identifies intervals that need closer inspection, and routes them to modality-specific observers. Audio and visual observations are complemented by PPM evidence about object properties, interactions, material responses, and likely outcomes. A finalizer aggregates the evidence into a temporally coherent caption.

<p align="center">
  <img src="fig/case-study.png" alt="Qualitative physical-perception case study" width="100%">
</p>

## OPC benchmark &amp; Dataset

OmniPhysCap (OPC) is a physics-aware and omission-aware benchmark for evaluating whether generated captions preserve physical and cross-modal evidence. It covers physical interactions, physical outcomes, visual information, audio, audiovisual alignment, temporal order, speech, and OCR. Each question includes a `Not Mentioned` option, allowing omitted evidence to be separated from contradictory evidence.

<p align="center">
  <img src="fig/opc-benchmark-results.png" alt="OPC benchmark results" width="360">
</p>

The benchmark and dataset are available on Hugging Face:

**[📊 Fysics-AI/OmniPhysics-Caption_benchmark](https://huggingface.co/datasets/Fysics-AI/OmniPhysics-Caption_benchmark)**

## PPM physical perception tool

The `PPM/` folder contains the merged two-epoch physical-perception model and
the minimal inference files needed to run it. It is an image-level tool for
evidence about objects, materials, contact and support, stability, likely
motion, forces, friction, and deformation.

The PPM artifact is released as a self-contained Hugging Face subdirectory:

**[🤗 Fysics-AI/OmniFysics-Captioner/PPM](https://huggingface.co/Fysics-AI/OmniFysics-Captioner/tree/main/PPM)**

Download the repository and point the PPM scripts to the local `PPM/` folder.
The PPM model card documents the validated vLLM configuration, input format,
limitations, and license status.

## Model

The captioner project and its PPM physical-perception tool are maintained in
this repository. The PPM weights are provided under `PPM/`, while the merged
Caption3 plus self-awareness checkpoint is provided at the repository root,
alongside `PPM/`. The `inference/` folder contains the matching deployment
and smoke-test entry points.

The root model uses the same Qwen3-Omni architecture and multimodal processor
as Caption3, and includes the merged self-awareness LoRA weights. It accepts
text, image, audio, and video inputs through the standard OpenAI-compatible
vLLM interface. The release includes model identifiers, supported input
formats, inference instructions, hardware requirements, and the applicable
model license.

### Inference code

Inference code is maintained in this GitHub repository rather than bundled
inside the Hugging Face model directory. Use `inference/serve_vllm.sh` to
start the model service, `inference/caption_infer.py` to send text, image,
audio, or video requests, and `inference/smoke_test.py` to verify a running
endpoint. The model files are downloaded from the Hugging Face repository
linked above.

```bash
MODEL_PATH=/path/to/OmniFysics-Captioner \
  bash inference/serve_vllm.sh
python inference/caption_infer.py --base-url http://127.0.0.1:8000/v1 \
  --video /path/to/video.mp4
python inference/smoke_test.py --base-url http://127.0.0.1:8000/v1
```

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

The root `LICENSE` currently reserves rights until the maintainers publish separate terms for code, data, benchmark annotations, and model weights. Source videos remain subject to the licenses of their original datasets.
