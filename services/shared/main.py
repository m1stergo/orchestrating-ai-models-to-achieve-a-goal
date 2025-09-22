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

# Configure root logger with timestamps and colors for better readability
# Get the root logger - this will affect all loggers in the application
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Remove any existing handlers to avoid duplicate logs
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

# Add a colored stream handler to the root logger
color_handler = colorlog.StreamHandler()
color_handler.setFormatter(colorlog.ColoredFormatter(
    '%(asctime)s - %(log_color)s%(levelname)s%(reset)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
root_logger.addHandler(color_handler)

# Set up module logger
logger = logging.getLogger(__name__)

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
