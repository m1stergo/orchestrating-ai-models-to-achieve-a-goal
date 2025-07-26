from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.products import router as products_router
from app.extract_web_content import router as extract_site_content_router
from app.describe_image import router as describe_image_router
from app.generate_description import router as generate_description_router
from app.upload_image import router as upload_image_router
from app.config import settings
from pathlib import Path

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
app.include_router(extract_site_content_router.router, prefix=f"{settings.API_V1_STR}/extract-site-content", tags=["extract-site-content"])
app.include_router(describe_image_router.router, prefix=f"{settings.API_V1_STR}/describe-image", tags=["describe-image"])
app.include_router(generate_description_router.router, prefix=f"{settings.API_V1_STR}/generate-description", tags=["generate-description"])
app.include_router(upload_image_router.router, prefix=f"{settings.API_V1_STR}/upload-image", tags=["upload-image"])

# Mount static files directory
static_dir = Path("app/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
