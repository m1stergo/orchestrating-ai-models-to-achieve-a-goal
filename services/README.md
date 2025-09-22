# AI Microservices Documentation

This directory contains AI microservices that provide specialized capabilities for the project. Each service is designed to run independently and communicate with the main backend through a REST API.

## General Structure

Each microservice follows a similar structure:

```
service-name/
├── app/                   # Main service code
│   ├── config.py          # Service-specific configuration
│   ├── handler.py         # AI model-specific implementation
│   ├── shared.py          # Shared instances (handler singleton)
│   ├── main.py            # FastAPI entry point (copied from shared)
│   ├── router.py          # API routes (copied from shared)
│   └── rp_handler.py      # RunPod serverless handler (copied from shared)
├── .env.example           # Environment variables example
├── Dockerfile             # Docker image configuration
├── requirements.txt       # Python dependencies
└── README.md              # Service-specific documentation
```

## Available Services

### 1. qwen-describe-image

This service uses the Qwen Vision-Language model to generate detailed descriptions of images. It receives an image URL and returns a textual description of its content.

**Main endpoint:** `/api/v1/run`

**Parameters:**
- `image_url`: URL of the image to describe
- `prompt` (optional): Custom instruction to guide the generation

### 2. mistral-generate-description

This service uses the Mistral model to generate product descriptions based on image descriptions. It can generate titles, descriptions, keywords, and suggested categories.

**Main endpoint:** `/api/v1/run`

**Parameters:**
- `image_description`: Description of the product image
- `prompt` (optional): Custom instruction to guide the generation

### 3. chatterbox-text-to-speech

This service uses the ChatterboxTTS model to convert text into realistic audio. It supports multiple voices and voice cloning with a sample audio.

**Main endpoint:** `/api/v1/run`

**Parameters:**
- `text`: Text to convert to audio
- `voice` (optional): Name of the voice to use
- `audio_prompt_url` (optional): URL of an audio file to clone the voice

## Shared Architecture

The services share a common architecture based on files in the `shared/` directory:

### Key Components

1. **InferenceHandler (common.py)**
   - Abstract class defining the interface for model handlers
   - Provides common methods for model loading and status verification
   - Each service implements a specific subclass for its model

2. **RunPodSimulator (common.py)**
   - Simulates the behavior of the RunPod serverless environment
   - Handles asynchronous jobs in separate threads
   - Provides job status tracking

3. **Router (router.py)**
   - Defines the REST API endpoints
   - Converts HTTP requests to model handler calls
   - Provides endpoints for execution and status checking

4. **RunPod Handler (rp_handler.py)**
   - Entry point for RunPod serverless deployments
   - Converts RunPod events to model handler requests

## Design Patterns Used

1. **Singleton Pattern**
   - Each service has a single instance of the model loaded in memory
   - Implemented through the `shared.py` module

2. **Adapter Pattern**
   - `InferenceHandler` defines a common interface for different AI models
   - Each service implements a specific adapter for its model

3. **Factory Pattern**
   - The model loading system acts as an abstract factory
   - Creates specific model instances based on configuration

4. **Asynchronous Processing**
   - Inference jobs are handled asynchronously
   - Allows multiple concurrent requests without blocking

## Execution and Deployment

### Local Execution

Each service can be run locally with:

```bash
cd service-name
pip install -r requirements.txt
python main.py
```

### Docker Execution

```bash
cd service-name
docker build -t service-name .
docker run -p 8001:8001 service-name
```

### RunPod Deployment

1. Build the Docker image and push it to a registry
2. Create a pod in RunPod using the image
3. Configure environment variables according to `.env.example`

## Integrations

- **S3/MinIO**: For model storage and download
- **Main Backend**: Integration through REST API
- **GPU Acceleration**: All services use GPU acceleration for inference

## Considerations for New Services

When creating a new service:

1. Copy the files from the `shared/` directory to the `app/` directory of the new service
2. Implement a subclass of `InferenceHandler` for the specific model
3. Create a `shared.py` file that instantiates the handler
4. Configure `config.py` with service-specific parameters
5. Update `Dockerfile` and `requirements.txt` with necessary dependencies
