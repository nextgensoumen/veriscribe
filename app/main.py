from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.routers import upload, summarize
from app.services.summarizer import SummarizerService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: We preload the model so the first request is fast
    print("Loading ML model into memory...")
    try:
        SummarizerService()
        print(f"✅ Model {settings.MODEL_NAME} loaded and ready!")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Allow CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(summarize.router, prefix="/api", tags=["Summarize"])

# Mount static files (the frontend)
# We ensure the static directory exists just in case
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the single-page application index.html"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Frontend not built yet. API is running."}

@app.get("/api/health")
async def health_check():
    """Check if the backend and mode are running."""
    # Check if model has been loaded
    model_loaded = SummarizerService._instance is not None
    return {
        "status": "online",
        "model_loaded": model_loaded,
        "model_name": settings.MODEL_NAME,
        "app": settings.APP_NAME
    }
