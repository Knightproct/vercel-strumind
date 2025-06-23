"""
StruMind Backend - Main FastAPI Application Entry Point
Production-ready structural engineering SaaS backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routes import (
    auth, projects, models, analysis, design, 
    detailing, bim, materials, sections, loads
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting StruMind Backend...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down StruMind Backend...")

# Initialize FastAPI application
app = FastAPI(
    title="StruMind API",
    description="Advanced Structural Engineering SaaS Backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(models.router, prefix="/api/models", tags=["Structural Models"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(design.router, prefix="/api/design", tags=["Design"])
app.include_router(detailing.router, prefix="/api/detailing", tags=["Detailing"])
app.include_router(bim.router, prefix="/api/bim", tags=["BIM"])
app.include_router(materials.router, prefix="/api/materials", tags=["Materials"])
app.include_router(sections.router, prefix="/api/sections", tags=["Sections"])
app.include_router(loads.router, prefix="/api/loads", tags=["Loads"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StruMind Structural Engineering API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "strumind-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
