from fastapi import FastAPI

from backend.app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API do aplicativo DriverTrack.",
)


@app.get("/")
def root():
    return {
        "application": settings.app_name,
        "message": "DriverTrack API está funcionando!",
        "environment": settings.app_env,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": settings.app_name,
    }
