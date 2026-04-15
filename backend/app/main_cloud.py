# Main application entry point - Cloud Ready Version
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import Base, engine
from .routes import router
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
logger.info(f"Starting Rubiscape ML Pipeline Tracker in {ENVIRONMENT} mode")

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    yield
    # Shutdown
    logger.info("Closing database connections...")
    await engine.dispose()

app = FastAPI(
    title="Rubiscape ML Pipeline Tracker",
    description="Track ML pipeline execution states with audit logging",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
# In development, allow all origins. In production, be more restrictive.
if ENVIRONMENT == "development":
    cors_origins = ["*"]
    logger.warning("CORS: Allowing all origins (development mode)")
else:
    # In production, get allowed origins from environment variable
    allowed_origins_str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000"
    )
    cors_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
    logger.info(f"CORS: Allowing specific origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Health check middleware (for load balancers)
@app.get("/health")
async def health_check():
    """Health check endpoint - required by Cloud Run"""
    logger.debug("Health check requested")
    return {
        "status": "ok",
        "service": "Rubiscape ML Pipeline Tracker",
        "environment": ENVIRONMENT
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint - for startup probes"""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return {"ready": True}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"ready": False, "error": str(e)}, 503

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Rubiscape ML Pipeline Tracker API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "environment": ENVIRONMENT
    }

# Include routes
app.include_router(router, prefix="/api/v1")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for logging"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "message": str(exc) if ENVIRONMENT == "development" else "An error occurred"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete")
    logger.info(f"Allowed CORS origins: {cors_origins}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
