# Backend Directory Structure

This document explains the organization of the backend codebase, following the principles of Vertical Slice Architecture.

## Root Structure

```
backend/
├── alembic/                # Database migration scripts
├── app/                    # Main application code
├── docs/                   # Documentation files
├── alembic.ini             # Alembic configuration for database migrations
├── create_tables.py        # Utility script to create database tables
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── .env.example            # Example environment variables
```

## Application Structure (`app/`)

The `app/` directory contains the main application code, organized by features (vertical slices):

```
app/
├── features/              # Feature modules (vertical slices)
│   ├── describe_image/    # Image description generation
│   ├── extract_web_content/ # Web content extraction
│   ├── generate_description/ # Product description generation
│   ├── products/          # Product CRUD operations
│   ├── settings/          # User settings management
│   ├── text_to_speech/    # Text-to-speech conversion
│   ├── upload_audio/      # Audio file uploads
│   └── upload_image/      # Image file uploads
├── shared/                # Shared components and utilities
│   ├── adapter.py         # Base adapter interface
│   ├── api_adapter.py     # API integration adapter
│   ├── minio_client.py    # MinIO storage client
│   └── utils.py           # General utilities
├── static/                # Static files (served by FastAPI)
│   ├── images/            # Uploaded images
│   ├── audio/             # Generated audio files
│   └── exports/           # Export files (ZIP)
├── __init__.py            # Package initialization
├── config.py              # Application configuration
├── database.py            # Database connection setup
├── exceptions.py          # Custom exceptions
└── main.py                # FastAPI application setup
```

## Feature Module Structure

Each feature module follows a similar structure:

```
feature_name/
├── __init__.py            # Package initialization
├── router.py              # API endpoints
├── schemas.py             # Pydantic models for request/response
├── service.py             # Business logic
├── models.py              # Database models (if needed)
└── shared/                # Feature-specific shared code (if needed)
    └── utils.py           # Feature-specific utilities
```

## Alembic Migrations (`alembic/`)

```
alembic/
├── versions/              # Migration script files
├── env.py                 # Alembic environment configuration
├── README                 # Alembic documentation
└── script.py.mako         # Template for migration scripts
```

## Feature-Specific Documentation

### `describe_image/`

API for image description generation. Connects to multiple vision models including:
- OpenAI vision models
- Google Gemini
- Qwen-VL (via microservice)

### `extract_web_content/`

Extracts content from web URLs, providing structured data from product pages.

### `generate_description/`

Generates product descriptions from image descriptions using LLMs:
- OpenAI GPT models
- Google Gemini
- Mistral (via microservice)

### `products/`

CRUD operations for product management.

### `settings/`

User settings management including default model preferences and custom prompts.

### `text_to_speech/`

Converts text to speech using Chatterbox TTS (via microservice).

### `upload_audio/`

Handles audio file uploads with MIME type validation.

### `upload_image/`

Handles image file uploads with MIME type validation.

## Shared Components

### `adapter.py`

Base adapter interface for integrating AI models.

### `api_adapter.py`

Base adapter for external API services.

### `minio_client.py`

Client for MinIO object storage.

### `utils.py`

General utilities used across features.
