FROM nvidia/cuda:11.8-devel-ubuntu22.04

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    python3.11-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for python and pip
RUN ln -s /usr/bin/python3.11 /usr/bin/python && \
    ln -s /usr/bin/pip3.11 /usr/bin/pip

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
# Install PyTorch with CUDA support (default to cu118 for broader compatibility)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# Install other requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
