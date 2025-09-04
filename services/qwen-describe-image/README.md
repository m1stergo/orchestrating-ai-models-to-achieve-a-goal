# Qwen Describe Image Service

Image description service using the Qwen/Qwen2-VL-2B-Instruct model.

## 🏠 Development

### Local Setup (Poetry - Recommended)

Fast and simple development using Poetry virtual environment:

```bash
# Copy environment configuration
cp env.example .env

# Install dependencies
poetry install

# Run the service with auto-reload
poetry run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**For Blackwell GPUs (RTX 50 series):**
```bash
poetry run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

## 🚀 Production (RunPod)

## RunPod Deployment

RunPod will build the image directly from your repository using `Dockerfile.prod`.

### Setup Steps

1. **Connect your repository** to RunPod (GitHub/GitLab)
2. **Create Network Volume** (10GB) for model persistence  
3. **Deploy pod** with:
   - **Dockerfile**: `Dockerfile.prod`
   - **Volume mount**: `/workspace/models`
   - **Environment variables**:
     ```bash
     MODEL_CACHE_DIR=/workspace/models
     HF_HUB_CACHE=/workspace/models
     ```