from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.products import router as products_router
# Importaciones con nombres de carpetas que contienen guiones requieren una sintaxis especial
import importlib
# Using string literal for module with hyphen in directory name
describe_image_router = importlib.import_module("app.describe-image.router").router
# Using string literal for module with hyphen in directory name
generate_description_router = importlib.import_module("app.generate-description.router").router
text_to_speech_router = importlib.import_module("app.text-to-speech.router").router
upload_image_router = importlib.import_module("app.upload_image.router").router
upload_audio_router = importlib.import_module("app.upload_audio.router").router
from app.export import router as export_router
from app.settings import router as settings_router
from app.extract_web_content import router as extract_web_content_router
from app.config import settings
from pathlib import Path
import logging
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Product description generator",
    description="API for product management with AI capabilities",
    version="0.1.0"
)

# Custom exception handler to standardize error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": str(exc.detail),
            "detail": exc.detail
        }
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(settings_router.router, prefix=f"{settings.API_VERSION}/settings", tags=["settings"])
app.include_router(products_router.router, prefix=f"{settings.API_VERSION}/products", tags=["products"])
app.include_router(upload_image_router, prefix=f"{settings.API_VERSION}/upload-image", tags=["upload-image"])
app.include_router(upload_audio_router, prefix=f"{settings.API_VERSION}/upload-audio", tags=["upload-audio"])
app.include_router(extract_web_content_router.router, prefix=f"{settings.API_VERSION}/extract-webcontent", tags=["extract-webcontent"])
app.include_router(describe_image_router, prefix=f"{settings.API_VERSION}/describe-image", tags=["describe-image"])
app.include_router(generate_description_router, prefix=f"{settings.API_VERSION}/generate-description", tags=["generate-description"])
app.include_router(text_to_speech_router, prefix=f"{settings.API_VERSION}/text-to-speech", tags=["text-to-speech"])
app.include_router(export_router.router, prefix=f"{settings.API_VERSION}/export", tags=["export"])

# Mount static files directory
static_dir = Path("app/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
