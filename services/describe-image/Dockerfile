# Use PyTorch official image with CUDA 12.1 (much lighter than nvidia/cuda devel)
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
# Install requirements (PyTorch already included in base image)
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download model weights (CPU-only, no GPU needed during build)
RUN python -c "\
import os; \
os.environ['HF_HUB_CACHE'] = '/app/models'; \
from transformers import AutoTokenizer, AutoProcessor; \
model_name = 'Qwen/Qwen2.5-VL-3B-Instruct'; \
print('Pre-downloading model weights...'); \
tokenizer = AutoTokenizer.from_pretrained(model_name); \
processor = AutoProcessor.from_pretrained(model_name); \
print('Model weights downloaded successfully!')"

# Set model cache directory
ENV MODEL_CACHE_DIR=/app/models
ENV HF_HUB_CACHE=/app/models

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
