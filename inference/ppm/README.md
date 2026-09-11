# PPM Inference

PPM is the image-level physical-perception model released under the PPM
subdirectory of the Hugging Face model repository. These scripts are kept
under inference/ppm to distinguish them from the end-to-end Captioner
inference entrypoints in the parent directory.

Download the model repository, then start the PPM service:

    MODEL_PATH=<downloaded-model-directory>/PPM \
      bash inference/ppm/serve_vllm.sh

Call the OpenAI-compatible endpoint with one image:

    python inference/ppm/infer.py \
      --base-url <your-endpoint> \
      --image <image-file>

Run the PPM smoke test:

    python inference/ppm/smoke_test.py \
      --base-url <your-endpoint>
