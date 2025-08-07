# Use PyTorch official image with CUDA 12.1 (lighter than nvidia/cuda devel)
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

# Set working directory to /app
WORKDIR /app

# Install Poetry and dependencies in a single layer, no color or prompts
RUN pip install --upgrade pip \
    && pip install "poetry==1.8.2" \
    && poetry config virtualenvs.create false

# Copy Poetry files first for better build cache
COPY pyproject.toml poetry.lock* ./

# Install main dependencies without interaction or ANSI colors (PyTorch already present)
RUN poetry install --only=main --no-dev --no-interaction --no-ansi

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

# Production command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
