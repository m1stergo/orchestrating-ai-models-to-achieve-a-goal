from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.products import router as products_router
# Importaciones con nombres de carpetas que contienen guiones requieren una sintaxis especial
import importlib
# Using string literal for module with hyphen in directory name
describe_image_router = importlib.import_module("app.describe-image.router").router
# Using string literal for module with hyphen in directory name
generate_description_router = importlib.import_module("app.generate-description.router").router
upload_image_router = importlib.import_module("app.upload_image.router").router
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(settings_router.router, prefix=f"{settings.API_V1_STR}/settings", tags=["settings"])
app.include_router(products_router.router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(upload_image_router, prefix=f"{settings.API_V1_STR}/upload-image", tags=["upload-image"])
app.include_router(extract_web_content_router.router, prefix=f"{settings.API_V1_STR}/extract-webcontent", tags=["extract-webcontent"])
app.include_router(describe_image_router, prefix=f"{settings.API_V1_STR}/describe-image", tags=["describe-image"])
app.include_router(generate_description_router, prefix=f"{settings.API_V1_STR}/generate-description", tags=["generate-description"])

# Mount static files directory
static_dir = Path("app/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
