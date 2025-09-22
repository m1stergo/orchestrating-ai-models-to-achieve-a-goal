# Backend Documentation

## Overview

This backend application is part of the "Orchestrating AI Models to Achieve a Goal" project. It serves as the core API server that orchestrates various AI models and services to process product data, generate descriptions, convert text to speech, and more. The backend is built using FastAPI with a modular architecture that follows clean code principles.

## Key Features

- Product management (CRUD operations)
- Image upload and processing
- Image description using Qwen-VL model
- Text generation for product descriptions using OpenAI, Mistral, or Gemini models
- Text-to-speech conversion using Chatterbox TTS
- Web content extraction
- User settings management
- File storage with local filesystem or MinIO object storage
- Comprehensive error handling and logging

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
backend/
├── alembic/             # Database migration scripts
├── app/
│   ├── features/        # Feature modules (vertical slices)
│   │   ├── describe_image/
│   │   ├── extract_web_content/
│   │   ├── generate_description/
│   │   ├── products/
│   │   ├── settings/
│   │   ├── text_to_speech/
│   │   ├── upload_audio/
│   │   └── upload_image/
│   ├── shared/          # Shared utilities and components
│   │   ├── adapter.py
│   │   ├── api_adapter.py
│   │   ├── minio_client.py
│   │   └── utils.py
│   ├── static/          # Static files (images, audio, exports)
│   ├── config.py        # Application configuration
│   ├── database.py      # Database connection setup
│   ├── exceptions.py    # Custom exceptions
│   └── main.py          # FastAPI application entry point
├── alembic.ini          # Alembic configuration for migrations
├── create_tables.py     # Utility script to create database tables
├── requirements.txt     # Python dependencies
└── .env.example         # Example environment variables
```

## Design Patterns

The backend implements several design patterns:

1. **Adapter Pattern**: Used for integrating different AI services (OpenAI, Gemini, Mistral)
2. **Factory Pattern**: Used for creating the appropriate adapter based on configuration
3. **Vertical Slice Architecture**: Features are organized into self-contained modules

## Configuration

The application is configured through environment variables, which can be set in a `.env` file. An example configuration is provided in `.env.example`. Key configuration groups include:

- **API settings**: Version, project name, base URL
- **Database settings**: Connection parameters for PostgreSQL
- **Storage settings**: File paths for images, audio, and exports
- **API keys**: For external services like OpenAI, Gemini
- **MinIO settings**: For object storage configuration
- **Service URLs**: For microservices like image description, text generation, and TTS

## Dependencies

Major dependencies include:

- FastAPI: Web framework
- SQLAlchemy: ORM for database operations
- Pydantic: Data validation and settings management
- Alembic: Database migrations
- MinIO: Object storage client
- Various AI client libraries (OpenAI, Google Generative AI)

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and configure your settings

4. Set up the database:
   ```bash
   python create_tables.py
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

The API follows a RESTful design with a flat URL structure. All endpoints are prefixed with `/api/v1/`. Main endpoints include:

- `/api/v1/products`: Product management
- `/api/v1/upload-image`: Image upload
- `/api/v1/describe-image`: Image description generation
- `/api/v1/generate-description`: Product description generation
- `/api/v1/text-to-speech`: Convert text to audio
- `/api/v1/upload-audio`: Audio file upload
- `/api/v1/extract-webcontent`: Extract content from web URLs
- `/api/v1/settings`: User settings management

## Database

The application uses PostgreSQL with SQLAlchemy as the ORM. Database migrations are managed using Alembic. The main entities include:

- Products
- Settings
- Users (if applicable)

## External Service Integration

The backend integrates with several external services:

1. **OpenAI API**: For generating text and processing images
2. **Gemini API**: Alternative for text and image processing
3. **Qwen-VL**: For image description (via microservice)
4. **Mistral**: For text generation (via microservice)
5. **Chatterbox**: For text-to-speech conversion (via microservice)

## Testing

The application is designed to be testable, with services and repositories that can be easily mocked. Tests can be added in a separate `tests` directory.

## Deployment

The application can be deployed using Docker. A `Dockerfile` is provided for containerization. For production deployment, consider using a proper WSGI server like Gunicorn behind a reverse proxy like Nginx.

## Security Considerations

- Always use environment variables for sensitive information like API keys and database credentials
- CORS is configured to accept all origins in development but should be restricted in production
- Input validation is performed using Pydantic schemas
- Error handling provides informative messages without leaking internal details
