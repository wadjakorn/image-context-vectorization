"""API routes for Image Context Extractor."""

from .images import router as images_router
from .duplicates import router as duplicates_router
from .directories import router as directories_router
from .health import router as health_router
from .websocket import router as websocket_router

__all__ = [
    "images_router",
    "duplicates_router",
    "directories_router",
    "health_router",
    "websocket_router",
]