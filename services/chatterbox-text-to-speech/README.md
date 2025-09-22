# Chatterbox Text-to-Speech Service

Text-to-speech conversion service using the Resemble AI Chatterbox model. This service converts text into realistic speech audio and supports voice cloning.

## 📋 Description

The service uses the Chatterbox TTS model from Resemble AI, a cutting-edge text-to-speech model that generates high-quality, natural-sounding speech. The service exposes a REST API that accepts text input and returns URLs to generated audio files.

## 🔄 API

### Main Endpoint: `/api/v1/run`

**Method**: POST

**Request Body**:
```json
{
  "text": "Text to convert to speech",
  "voice_url": "https://example.com/voice-sample.wav" (optional)
}
```

**Successful Response**:
```json
{
  "id": "uuid",
  "status": "COMPLETED",
  "output": {
    "status": "COMPLETED",
    "message": "Audio generated successfully.",
    "data": "https://storage-url.com/audio/generated-audio.wav"
  }
}
```

### Status Endpoint: `/api/v1/status/{id}`

**Method**: GET

**Response**:
```json
{
  "id": "uuid",
  "status": "COMPLETED",
  "output": {
    "status": "COMPLETED",
    "message": "Audio generated successfully.",
    "data": "https://storage-url.com/audio/generated-audio.wav"
  }
}
```

## 🧠 Internal Operation

The service follows these steps to generate speech:

1. Processes the input text for speech synthesis
2. If a voice URL is provided, downloads the audio sample for voice cloning
3. Generates speech using the Chatterbox TTS model
4. Saves the audio output to a WAV file
5. Uploads the file to MinIO storage
6. Returns the URL to the generated audio

The service uses PyTorch with GPU acceleration for fast inference and is designed to run in environments with CUDA-capable GPUs.

## 🎙️ Voice Cloning

The service supports voice cloning by providing an audio sample URL in the `voice_url` parameter. The model will attempt to synthesize speech that sounds similar to the provided sample. For best results:

- Provide a clear audio sample of 5-15 seconds
- Ensure the sample has minimal background noise
- Use WAV format for the sample audio

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
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# For CUDA development (if you have compatible GPU):
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 5. Copy .env.example to .env and configure MinIO
cp .env.example .env

# 6. Run service
python main.py
```

### Deactivate environment
```bash
deactivate
```

## 🚀 Production (RunPod)

The Dockerfile is optimized for RunPod deployment:
- Uses PyTorch base image with CUDA support
- Automatic GPU detection with fallback to CPU
- MinIO integration for audio storage
- Optimized for serverless operation
