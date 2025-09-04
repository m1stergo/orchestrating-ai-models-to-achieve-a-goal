# Use PyTorch official image with CUDA 12.1 (lighter than nvidia/cuda devel)
FROM pytorch/pytorch:2.8.0-cuda12.9-cudnn9-runtime

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
from transformers import AutoTokenizer, AutoProcessor, Qwen2_5_VLForConditionalGeneration; \
model_name = 'Qwen/Qwen2-VL-2B-Instruct'; \
print('Pre-downloading model weights...'); \
print('Downloading tokenizer and processor...'); \
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True); \
processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True); \
print('Downloading model weights (this may take several minutes)...'); \
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_name, trust_remote_code=True); \
print('Model weights downloaded successfully!')"

# Create models directory with proper permissions
RUN mkdir -p /app/models && chmod 777 /app/models

# Set model cache directory
ENV MODEL_CACHE_DIR=/app/models
ENV HF_HUB_CACHE=/app/models

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x startup.sh

# Expose port
EXPOSE 8001

# Production command - use startup script
CMD ["./startup.sh"]
