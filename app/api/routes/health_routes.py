"""Health check and status routes"""
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Data Query Backend API",
        "version": "0.1.0",
        "endpoints": {
            "upload_csv": "/api/upload-csv",
            "generate_schema": "/api/generate-schema",
            "create_database": "/api/create-database",
            "health": "/health",
        },
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
