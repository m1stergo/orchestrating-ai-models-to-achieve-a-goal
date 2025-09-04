# Qwen Describe Image Service

Image description service using the Qwen/Qwen2-VL-2B-Instruct model.

## 🏠 Development

### Local Setup (Poetry - Recommended)

```bash
# 1. copy .env.example to .env
cp .env.example .env

# 2. Install dependencies
poetry install

# 3. Download model (first time)
python download_model.py

# 4. Run service
poetry run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Local Setup With Docker
```bash
# Build and run
docker-compose up --build

# Only first time - download model
docker-compose --profile setup run model-downloader
```

## 🚀 Production

### Storage Strategy

**Development/Testing:**
- Local volume: `./models`
- Auto download model on first start

### RunPod Deployment

1. **Pre-requisitos:**
   - Upload model to Network Volume
   - Or use auto download on first start

2. **Deploy:**
   ```bash
   # Use docker-compose.prod.yml
   docker-compose -f docker-compose.prod.yml up
   ```

3. **Environment variables:**
   ```bash
   MODEL_CACHE_DIR=/workspace/models
   HF_HUB_CACHE=/workspace/models
   ```