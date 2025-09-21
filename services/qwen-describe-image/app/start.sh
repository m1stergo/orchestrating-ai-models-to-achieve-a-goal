#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] RunPod Serverless worker starting..."

# set environment variables
export HF_HOME="/runpod-volume/huggingface"
export HF_HUB_CACHE="/runpod-volume/huggingface"
export TRANSFORMERS_CACHE="/runpod-volume/huggingface"
export TORCH_HOME="/runpod-volume/torch"
export TMPDIR="/runpod-volume/tmp"
export MODELS_DIR="/runpod-volume/models"
export PYTHONUNBUFFERED=1
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.8"

# Ensure dirs exist (if volume is mounted, these live on the volume)
mkdir -p "$HF_HOME" "$TRANSFORMERS_CACHE" "$TORCH_HOME" "$TMPDIR" /runpod-volume/models /runpod-volume/offload || true

# Quick diagnostics
( df -hT /runpod-volume || true )
( du -h --max-depth=1 "$HF_HOME" 2>/dev/null | sort -h || true )

# Start RunPod handler
exec python -m app.rp_handler