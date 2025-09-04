FROM pytorch/pytorch:2.8.0-cuda12.9-cudnn9-runtime

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends bash ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file first for better layer caching
COPY requirements.txt ./

# Install dependencies via pip (PyTorch already included in base image)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure start script is executable
RUN chmod +x src/start.sh

# Run the RunPod serverless handler
CMD ["./src/start.sh"]
