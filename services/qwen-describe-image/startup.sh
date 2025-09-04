#!/bin/bash

# Startup script to handle model cache permissions and cleanup
set -e

echo "Starting Qwen describe-image service..."

# Ensure models directory exists with proper permissions
mkdir -p /app/models
chmod 777 /app/models

# Check if model exists in expected location or find it elsewhere
MODEL_EXPECTED_PATH="/app/models/models--Qwen--Qwen2-VL-2B-Instruct"
MODEL_FOUND=false

# Check expected location first
if [ -d "$MODEL_EXPECTED_PATH" ]; then
    echo "Model found in expected location: $MODEL_EXPECTED_PATH"
    MODEL_FOUND=true
else
    # Search for model in common HuggingFace cache locations
    echo "Searching for existing model in cache directories..."
    
    # Common HF cache locations
    SEARCH_PATHS=(
        "/app/models"
        "/root/.cache/huggingface"
        "/home/.cache/huggingface"
        "$HOME/.cache/huggingface"
    )
    
    for search_path in "${SEARCH_PATHS[@]}"; do
        if [ -d "$search_path" ]; then
            FOUND_MODEL=$(find "$search_path" -name "*Qwen*2*VL*2B*Instruct*" -type d 2>/dev/null | head -1)
            if [ ! -z "$FOUND_MODEL" ] && [ -d "$FOUND_MODEL" ]; then
                echo "Model found at: $FOUND_MODEL"
                echo "Moving model to expected location: $MODEL_EXPECTED_PATH"
                mkdir -p "$(dirname "$MODEL_EXPECTED_PATH")"
                mv "$FOUND_MODEL" "$MODEL_EXPECTED_PATH" || cp -r "$FOUND_MODEL" "$MODEL_EXPECTED_PATH"
                MODEL_FOUND=true
                break
            fi
        fi
    done
fi

# Try to download from S3 if configured and model still not found
if [ "$MODEL_FOUND" = false ] && [ ! -z "$S3_ENDPOINT_URL" ] && [ ! -z "$S3_BUCKET_NAME" ]; then
    echo "S3 storage configured. Attempting to download from S3..."
    python s3_sync.py download --local-dir /app/models --s3-prefix models/ && MODEL_FOUND=true || echo "S3 download failed"
fi

# Final check
if [ "$MODEL_FOUND" = false ]; then
    echo "Model not found locally or in S3. Will download from HuggingFace on first use."
fi

# Clean up any stale lock files from previous interrupted downloads
echo "Cleaning up any stale lock files..."
find /app/models -name "*.lock" -type f -delete 2>/dev/null || true
find /app/models -name ".tmp*" -type d -exec rm -rf {} + 2>/dev/null || true
find /app/models -name "tmp*" -type d -exec rm -rf {} + 2>/dev/null || true

# Clean up specific Hugging Face cache lock patterns
find /app/models -name "*.incomplete" -type f -delete 2>/dev/null || true
find /app/models -name ".locks" -type d -exec rm -rf {} + 2>/dev/null || true

# Fix permissions recursively
echo "Fixing cache directory permissions..."
find /app/models -type d -exec chmod 755 {} + 2>/dev/null || true
find /app/models -type f -exec chmod 644 {} + 2>/dev/null || true

# Set proper ownership if running as root
if [ "$(id -u)" = "0" ]; then
    chown -R root:root /app/models 2>/dev/null || true
fi

echo "Cache directory prepared. Starting application..."

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8001
