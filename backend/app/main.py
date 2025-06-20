from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.products import router as products_router
from app.config import settings

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
app.include_router(products_router.router, prefix=settings.API_V1_STR)
