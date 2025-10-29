from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from app.api.routes import csv_routes, schema_routes, database_routes, health_routes
from app.config import settings


# Create necessary directories
UPLOAD_DIR = Path("uploads")
DB_DIR = Path("databases")
UPLOAD_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    print("Starting up Data Query Backend...")
    yield
    # Shutdown
    print("Shutting down Data Query Backend...")


app = FastAPI(
    title="Data Query Backend API",
    description="Backend API for CSV upload, schema generation, and database creation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_routes.router)
app.include_router(csv_routes.router)
app.include_router(schema_routes.router)
app.include_router(database_routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
