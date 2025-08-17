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

# Include router
app.include_router(router, prefix="/api/v1", tags=["describe-image"])

@app.get("/healthz")
async def readiness_check():
    """
    Readiness probe endpoint that checks if the model is loaded.
    Used by Kubernetes/RunPod to determine if the pod is ready to serve requests.
    """
    global model_loaded
    return {
        "status": "ready" if model_loaded else "loading",
        "loaded": model_loaded,
        "service": "describe-image"
    }

@app.get("/warmup")
async def warmup():
    """
    Endpoint to trigger model loading if not already loaded.
    Useful for manual warmup after deployment.
    """
    global model_instance, model_loaded
    
    if model_loaded:
        return {"status": "already_loaded"}
    
    try:
        await model_instance.is_loaded()
        model_loaded = True
        return {"status": "loaded_successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Important: Use only 1 worker per GPU
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, workers=1)
