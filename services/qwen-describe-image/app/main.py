from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import shared globals
from app.shared import model_instance, model_loaded

# Import router after shared globals to avoid circular imports
from app.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to preload the model at startup.
    This ensures the model is loaded only once when the server starts.
    """
    global model_instance, model_loaded
    
    # Load model at startup
    logger.info("Starting model preloading...")
    try:
        await model_instance.is_loaded()
        model_loaded = True
        logger.info("Model preloaded successfully")
    except Exception as e:
        logger.error(f"Failed to preload model: {str(e)}")
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down, performing cleanup...")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add root health check for Docker
@app.get("/health")
async def health_check():
    """
    Root health check endpoint for Docker.
    Docker health check only needs HTTP 200 response.
    """
    from app.service import get_service_status
    status_info = get_service_status()
    
    # For Docker health check, we only care if the service responds
    # Return 200 if model is ready, let Docker handle the rest
    if status_info["status"] == "ready":
        return {"status": "ok"}
    else:
        # Return 503 Service Unavailable if model is still loading
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service not ready")

# Include router
app.include_router(router, prefix="/api/v1", tags=["describe-image"])


if __name__ == "__main__":
    import uvicorn
    # Important: Use only 1 worker per GPU
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, workers=1)
