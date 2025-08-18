from app.main import app

if __name__ == "__main__":
    import uvicorn
    import argparse
    from app.config import settings
    
    parser = argparse.ArgumentParser(description='Run Chatterbox TTS Service')
    parser.add_argument('--port', type=int, default=settings.PORT, help=f'Port to run the service on (default: {settings.PORT})')
    parser.add_argument('--host', type=str, default="0.0.0.0", help='Host to bind to (default: 0.0.0.0)')
    args = parser.parse_args()
    
    # Important: Use only 1 worker per GPU
    uvicorn.run(app, host=args.host, port=args.port, workers=1)
