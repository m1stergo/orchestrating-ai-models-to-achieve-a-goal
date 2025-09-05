# Qwen Describe Image Service

Image description service using the Qwen/Qwen2-VL-2B-Instruct model.

## 🏠 Development

### Local Setup
Create virtual environment and install dependencies using venv.

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install PyTorch manually (not included in requirements.txt)
# For CPU-only development:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# For CUDA development (if you have compatible GPU):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 5. Copy .env.example to .env
cp .env.example .env

# 6. Run service
python main.py
```

### Deactivate environment
```bash
deactivate
```

### PyTorch Dependencies

**Important:** PyTorch and torchvision are commented out in `requirements.txt` because:

- **Docker/RunPod**: Uses PyTorch 2.8.0 + CUDA 12.9 from base image `pytorch/pytorch:2.8.0-cuda12.9-cudnn9-runtime`
- **Local Development**: Requires manual installation to choose CPU vs CUDA version

This ensures Docker uses the optimized PyTorch with correct CUDA version while allowing flexibility for local development.

## 🚀 Production (RunPod)

The Dockerfile is optimized for RunPod deployment:
- Uses PyTorch base image with CUDA 12.9 support
- Automatic GPU detection and fallback to CPU
- No additional PyTorch installation needed