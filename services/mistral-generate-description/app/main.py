"""Main application module for AI microservice.

This module initializes the FastAPI application for the AI microservice,
sets up logging, CORS middleware, and includes the API router.

The application is designed to be run as a standalone service or 
as part of a RunPod serverless deployment.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
import colorlog

# Configure logging with timestamps and colors for better readability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set up module logger with color formatting
logger = logging.getLogger(__name__)
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

# Import the API router after logging is configured
from app.router import router

# Create the FastAPI application with metadata from settings
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# Configure Cross-Origin Resource Sharing (CORS)
# In production, restrict origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"]   # Allow all headers
)

# Include API router with version prefix
# Note: The tag should be updated to match the specific service
app.include_router(router, prefix="/api/v1", tags=["generate_description"])


# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting service on port {settings.PORT}")
    # Run with a single worker for AI model inference to avoid memory issues
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, workers=1)
