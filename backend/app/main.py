# Main application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import Base, engine
from .routes import router
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
ENV = os.getenv("ENVIRONMENT", "development")
# Secure CORS: Default to localhost for dev, but require explicit setup for prod
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Create tables on startup (ONLY in development)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if ENV == "development":
        logger.info("Development environment detected. Auto-creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        logger.info("Production environment detected. Relying on Alembic migrations.")
        
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="Rubiscape ML Pipeline Tracker",
    description="Track ML pipeline execution states with audit logging",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (Secured)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "environment": ENV, "service": "Rubiscape ML Pipeline Tracker"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Rubiscape ML Pipeline Tracker API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
