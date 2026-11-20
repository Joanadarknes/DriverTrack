from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import settings
from backend.app.db.session import engine
from backend.app.api.v1.router import api_router


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API do aplicativo DriverTrack.",
)


app.include_router(api_router, prefix=settings.api_v1_prefix)


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


@app.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            postgis_version = connection.execute(
                text("SELECT PostGIS_Full_Version()")
            ).scalar()

        return {
            "status": "healthy",
            "database": "connected",
            "postgis": postgis_version,
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível conectar ao banco de dados.",
        )
