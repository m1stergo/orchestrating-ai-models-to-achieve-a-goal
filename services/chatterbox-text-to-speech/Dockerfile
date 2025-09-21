FROM pytorch/pytorch:2.8.0-cuda12.9-cudnn9-runtime

# Install system dependencies and build tools needed for pkuseg
RUN apt-get update && \
    apt-get install -y --no-install-recommends bash ca-certificates build-essential g++ && \
    rm -rf /var/lib/apt/lists/*

# Useful defaults (can be overridden in RunPod UI)
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/runpod-volume/huggingface \
    HF_HUB_CACHE=/runpod-volume/huggingface \
    TRANSFORMERS_CACHE=/runpod-volume/huggingface \
    TORCH_HOME=/runpod-volume/torch \
    TMPDIR=/runpod-volume/tmp \
    MODELS_DIR=/runpod-volume/models \
    PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.8"

# Create runtime dirs (works even if volume not mounted yet)
RUN mkdir -p /runpod-volume/huggingface /runpod-volume/models /runpod-volume/tmp /runpod-volume/offload /runpod-volume/torch

WORKDIR /app

# Copy requirements file first for better layer caching
COPY requirements.txt ./

# Install dependencies via pip (PyTorch already included in base image)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure start script is executable
RUN chmod +x app/start.sh

# Run the RunPod serverless handler
CMD ["./app/start.sh"]
