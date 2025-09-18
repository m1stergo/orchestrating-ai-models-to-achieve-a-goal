FROM runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04


# Install system dependencies and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file first for better layer caching
COPY requirements.txt ./

# Install dependencies via pip (PyTorch already included in base image)
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from chatterbox.tts import ChatterboxTTS; model = ChatterboxTTS.from_pretrained(device='cuda')"

# Copy application code
COPY . .

# Ensure start script is executable
RUN chmod +x app/start.sh

# Run the RunPod serverless handler
CMD ["./app/start.sh"]
