# OmniFysics-Captioner Inference

The model weights are hosted at the Fysics-AI/OmniFysics-Captioner Hugging Face repository. This folder contains the OpenAI-compatible vLLM launcher, request client, and smoke test for the merged Caption3 plus self-awareness model.

The launcher expects the downloaded Hugging Face model directory in MODEL_PATH. It uses tensor parallelism 4 by default because Qwen3-Omni's audio encoder has 20 attention heads and TP4 is compatible while TP8 is not.

    MODEL_PATH=/path/to/OmniFysics-Captioner bash inference/serve_vllm.sh
    python inference/caption_infer.py --base-url http://127.0.0.1:8000/v1 --video /path/to/video.mp4
    python inference/smoke_test.py --base-url http://127.0.0.1:8000/v1

Install requests for the client and a compatible vLLM/Qwen3-Omni runtime for the server. The server accepts OpenAI-compatible image, video, and audio content blocks.
