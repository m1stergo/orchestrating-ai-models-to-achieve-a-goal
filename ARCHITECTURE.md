# AI Model Orchestration Architecture

## Overview

This document describes the architecture of the AI model orchestration system, which separates lightweight providers (OpenAI, Gemini) as in-process adapters within the backend core, and heavyweight providers (Qwen, Mistral) as dedicated GPU microservices with preloaded models, health checks, and concurrency controls.

## Architecture Components

### 1. Core Backend

The core backend is responsible for:
- Orchestrating calls to the appropriate AI model provider based on the task and availability
- Maintaining domain use cases (describe_image, generate_text) abstracted from provider details
- Hosting lightweight providers (OpenAI, Gemini) as in-process adapters
- Proxying requests to heavyweight providers (Qwen, Mistral) via their microservices

#### Key Components in Core Backend:

- **Base Adapters**: Abstract interfaces for image description and text generation
- **Lightweight Adapters**: OpenAI and Gemini adapters that call their respective SDKs directly
- **Heavyweight Adapters**: Qwen and Mistral adapters that call their respective microservices
- **Adapter Factory**: Manages all adapters and provides selection logic based on task and provider preference
- **Domain Services**: ImageDescriptionService and TextGenerationService that use the adapter factory to orchestrate calls

### 2. GPU Microservices

Dedicated microservices for heavyweight models that require GPU resources:

- **Qwen VL Microservice**: For image description tasks
- **Mistral Microservice**: For text generation tasks

#### Key Features of GPU Microservices:

- **Model Preloading**: Models are preloaded at startup using FastAPI lifespan context manager
- **Health Checks**: `/healthz` endpoint for readiness probes and `/health` for basic health checks
- **Warmup Endpoint**: `/warmup` endpoint for manual model loading if needed
- **Concurrency Control**: Semaphore to limit concurrent inference requests
- **Single Worker Deployment**: Designed to run with one worker per GPU

## Deployment Recommendations

### Core Backend

- **Resources**: Does not require GPU, can be deployed on CPU-only instances
- **Scaling**: Can be horizontally scaled as needed
- **Environment Variables**:
  - `OPENAI_API_KEY`, `OPENAI_TEXT_MODEL`, `OPENAI_VISION_MODEL`
  - `GEMINI_API_KEY`, `GEMINI_TEXT_MODEL`, `GEMINI_VISION_MODEL`
  - `QWEN_SERVICE_URL` (URL of Qwen GPU microservice)
  - `MISTRAL_SERVICE_URL` (URL of Mistral GPU microservice)

### GPU Microservices

- **Resources**: Requires GPU with sufficient VRAM for the model
- **Scaling**: Deploy one instance per GPU, with a single worker per instance
- **Readiness Probes**: Use the `/healthz` endpoint to ensure the model is loaded before sending traffic
- **Startup**: Allow sufficient time for model loading during startup
- **Environment Variables**:
  - Qwen: `MODEL_PATH`, `DEVICE` (cuda:0)
  - Mistral: `MODEL_PATH`, `DEVICE` (cuda:0)

## API Endpoints

### Core Backend

- `/v1/describe-image` - Image description endpoint that orchestrates calls to providers
- `/v1/generate-text` - Text generation endpoint that orchestrates calls to providers

### Qwen Microservice

- `/api/v1/describe-image` - Image description using Qwen VL model
- `/healthz` - Readiness probe endpoint
- `/warmup` - Manual model loading endpoint
- `/health` - Basic health check

### Mistral Microservice

- `/api/v1/generate-description` - Text generation using Mistral model
- `/healthz` - Readiness probe endpoint
- `/warmup` - Manual model loading endpoint
- `/health` - Basic health check

## Concurrency and Resource Management

- Each GPU microservice uses a semaphore to limit concurrent inference requests
- Default concurrency limit is set to 1 request at a time to prevent GPU OOM errors
- Adjust `MAX_CONCURRENT_INFERENCES` based on your GPU memory and model requirements

## Error Handling and Fallbacks

- The core backend's adapter factory implements fallback logic to try alternative providers if the preferred provider is unavailable
- Each adapter implements error handling and timeouts for robustness
- GPU microservices return appropriate error responses if the model fails to load or inference fails

## Monitoring Recommendations

- Add logging for inference time, VRAM usage, and errors
- Consider adding Prometheus metrics for request counts, latencies, and error rates
- Monitor GPU utilization and memory usage

## Future Enhancements

- Add external queue system for high-traffic scenarios
- Implement model versioning and A/B testing capabilities
- Add API Gateway or NGINX for routing, timeouts, and rate limiting
- Implement automatic scaling based on queue length and GPU utilization
