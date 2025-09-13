from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    # Important: Use only 1 worker per GPU
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT, workers=1)
