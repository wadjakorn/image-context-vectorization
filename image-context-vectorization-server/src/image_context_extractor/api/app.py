"""FastAPI application for Image Context Extractor."""

import logging
import os
from contextlib import asynccontextmanager

from image_context_extractor.api.dependencies import get_extractor

# Disable ChromaDB telemetry early to prevent capture() errors
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_CLIENT_DISABLE_TELEMETRY", "True")
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exception_handlers import http_exception_handler
import uvicorn

from .routes import (
    images_router,
    duplicates_router,
    directories_router,
    health_router,
    websocket_router,
)
from .models.responses import ErrorResponse
from ..config.settings import get_config
from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Image Context Extractor API...")
    
    # Initialize configuration
    try:
        config = get_config()
        logger.info("Configuration loaded successfully")
        
        # Optional: Pre-load models at startup (uncomment to enable)
        # from ..api.dependencies import get_extractor
        extractor = get_extractor()
        timings = extractor.model_manager.preload_all_models()
        logger.info(f"Models pre-loaded at startup in {timings['total']:.2f}s")
        
    except Exception as e:
        logger.warning(f"Failed to load configuration: {e}")
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Image Context Extractor API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Image Context Extractor API",
        description="API for extracting contextual information from images and performing similarity searches",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure as needed for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Exception handlers
    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        """Custom HTTP exception handler that preserves original status codes."""
        logger.info(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")
        
        error_response = ErrorResponse(
            error=exc.__class__.__name__,
            message=str(exc.detail),
            details={
                "status_code": exc.status_code,
                "method": request.method,
                "path": str(request.url.path)
            }
        )
        return JSONResponse(
            status_code=exc.status_code,  # Preserve the original status code
            content=error_response.dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """General exception handler."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        error_response = ErrorResponse(
            error=exc.__class__.__name__,
            message="Internal server error",
            details={"path": str(request.url)}
        )
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )
    
    # Include routers
    app.include_router(health_router)
    app.include_router(images_router)
    app.include_router(duplicates_router)
    app.include_router(directories_router)
    app.include_router(websocket_router)
    
    # Static files (for serving uploaded images, etc.)
    static_dir = "static"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Root endpoint
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint with basic information."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Image Context Extractor API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #333; }
                .endpoint { margin: 10px 0; }
                .method { font-weight: bold; color: #007ACC; }
                .path { font-family: monospace; background: #f5f5f5; padding: 2px 4px; }
                .description { color: #666; margin-left: 20px; }
            </style>
        </head>
        <body>
            <h1 class="header">Image Context Extractor API</h1>
            <p>Welcome to the Image Context Extractor API. This service provides endpoints for processing images, extracting contextual information, and performing similarity searches.</p>
            
            <h2>Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/docs</span>
                <div class="description">Interactive API documentation (Swagger UI)</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/redoc</span>
                <div class="description">Alternative API documentation (ReDoc)</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/v1/health</span>
                <div class="description">Health check and service status</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/v1/images/process</span>
                <div class="description">Process a single image</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/v1/images/upload</span>
                <div class="description">Upload and optionally process an image</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/v1/directories/process</span>
                <div class="description">Process all images in a directory</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/v1/images/</span>
                <div class="description">List all images or search for similar images using query parameter</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/v1/duplicates/check</span>
                <div class="description">Check for duplicate images</div>
            </div>
            
            <div class="endpoint">
                <span class="method">WebSocket</span> <span class="path">/ws</span>
                <div class="description">Real-time updates and notifications</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/v1/models/status</span>
                <div class="description">Check model loading status without loading models</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/v1/models/preload</span>
                <div class="description">Preload all models and get timing information</div>
            </div>
            
            <h2>Quick Start</h2>
            <ol>
                <li>Check service health: <code>GET /api/v1/health</code></li>
                <li>Upload an image: <code>POST /api/v1/images/upload</code></li>
                <li>List or search images: <code>GET /api/v1/images/?query=optional</code></li>
                <li>Check for duplicates: <code>POST /api/v1/duplicates/check</code></li>
            </ol>
            
            <p>For detailed documentation and interactive testing, visit <a href="/docs">/docs</a></p>
        </body>
        </html>
        """
    
    # API info endpoint
    @app.get("/api/v1/info")
    async def api_info():
        """Get API information and available endpoints."""
        return {
            "name": "Image Context Extractor API",
            "version": "1.0.0",
            "description": "API for extracting contextual information from images",
            "endpoints": {
                "health": "/api/v1/health",
                "models": "/api/v1/models/*",
                "images": "/api/v1/images/*",
                "duplicates": "/api/v1/duplicates/*",
                "directories": "/api/v1/directories/*",
                "websocket": "/ws",
                "docs": "/docs",
                "redoc": "/redoc"
            },
            "features": [
                "Image processing and context extraction",
                "Similarity search using text queries",
                "Duplicate detection and removal",
                "Directory batch processing",
                "Model loading management and timing",
                "Real-time WebSocket updates",
                "RESTful API with OpenAPI documentation"
            ]
        }
    
    return app


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info"
):
    """Run the FastAPI server."""
    # Setup logging
    setup_logging()
    
    logger.info(f"Starting Image Context Extractor API server on {host}:{port}")
    
    uvicorn.run(
        "image_context_extractor.api.app:create_app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        factory=True
    )


if __name__ == "__main__":
    run_server(reload=True)