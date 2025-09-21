# PyTorch 2.6 + CUDA 12.6 + cuDNN 9 (tag válido)
FROM pytorch/pytorch:2.6.0-cuda12.6-cudnn9-runtime

# Build tools (pkuseg y cías)
RUN apt-get update && \
    apt-get install -y --no-install-recommends bash ca-certificates build-essential g++ && \
    rm -rf /var/lib/apt/lists/*

# Defaults (ajustables en RunPod)
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/runpod-volume/huggingface \
    HF_HUB_CACHE=/runpod-volume/huggingface \
    TRANSFORMERS_CACHE=/runpod-volume/huggingface \
    TORCH_HOME=/runpod-volume/torch \
    TMPDIR=/runpod-volume/tmp \
    MODELS_DIR=/runpod-volume/models
    # Nota: si tu app usa Pydantic Settings con extra=forbid,
    # NO declares PYTORCH_CUDA_ALLOC_CONF aquí o añadí el campo a tu Settings.
    # PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.8"

# Dirs de runtime (ok incluso si el volume todavía no monta)
RUN mkdir -p /runpod-volume/huggingface /runpod-volume/models /runpod-volume/tmp /runpod-volume/offload /runpod-volume/torch

WORKDIR /app

# Cache friendly: copiar requirements primero
COPY requirements.txt .

# Asegurar matriz correcta de PyTorch 2.6 antes del resto
# torch==2.6.0  ↔  torchvision==0.21.0  ↔  torchaudio==2.6.0
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "torch==2.6.0" "torchvision==0.21.0" "torchaudio==2.6.0" && \
    pip install --no-cache-dir -r requirements.txt

# Verificación rápida
RUN python - <<'PY'
import torch, torchvision, torchaudio
print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("torchvision:", torchvision.__version__)
print("torchaudio:", torchaudio.__version__)
PY

# Copiar código
COPY . .

# Permisos de start
RUN chmod +x app/start.sh

# Entrypoint
CMD ["./app/start.sh"]
