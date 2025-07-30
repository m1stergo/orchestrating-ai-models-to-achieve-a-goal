from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.products import router as products_router
from app.upload_image import router as upload_image_router
from app.services import router as services_router
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
    title=settings.PROJECT_NAME,
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
app.include_router(products_router.router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])
app.include_router(upload_image_router.router, prefix=f"{settings.API_V1_STR}/upload-image", tags=["upload-image"])
app.include_router(services_router.router, prefix=f"{settings.API_V1_STR}/services", tags=["services"])

# Mount static files directory
static_dir = Path("app/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
