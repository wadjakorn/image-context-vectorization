"""API routes for health checks and system status."""

import time
import logging
# import psutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from ..models.responses import HealthResponse, DatabaseStats, ConfigResponse
from ..dependencies import get_extractor_lazy
from ... import __version__

router = APIRouter(prefix="/api/v1", tags=["health"])
logger = logging.getLogger(__name__)

# Track service start time
service_start_time = time.time()




@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Get service health status - lightweight check without heavy model loading."""
    try:
        uptime = time.time() - service_start_time
        
        # Simple availability check without loading models
        return HealthResponse(
            status="healthy",
            version=__version__,
            database_connected=True,  # Will be checked on actual usage
            models_loaded=False,  # Models load on demand
            uptime=uptime,
            stats=None
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            version=__version__,
            database_connected=False,
            models_loaded=False,
            uptime=time.time() - service_start_time,
            stats=None
        )


@router.get("/status")
async def get_system_status():
    """Get detailed system status information."""
    try:
        # System information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
            },
            "service": {
                "uptime_seconds": time.time() - service_start_time,
                "version": __version__,
                "start_time": datetime.fromtimestamp(service_start_time).isoformat(),
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/config", response_model=ConfigResponse)
async def get_configuration(extractor_instance = Depends(get_extractor_lazy)):
    """Get current configuration settings."""
    try:
        config = extractor_instance.config
        
        # Check which models are loaded
        models_loaded = {}
        try:
            models_loaded["blip"] = extractor_instance.model_manager._blip_model is not None
            models_loaded["clip"] = extractor_instance.model_manager._clip_model is not None
            models_loaded["sentence_transformer"] = extractor_instance.model_manager._sentence_transformer is not None
        except Exception as e:
            logger.warning(f"Error checking model status: {e}")
            models_loaded = {"blip": False, "clip": False, "sentence_transformer": False}
        
        return ConfigResponse(
            device=config.model.device,
            max_caption_length=config.processing.max_caption_length,
            object_confidence_threshold=config.processing.object_confidence_threshold,
            supported_formats=config.processing.supported_formats,
            models_loaded=models_loaded
        )
        
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(extractor_instance = Depends(get_extractor_lazy)):
    """Get application metrics."""
    try:
        stats = extractor_instance.get_stats()
        processed_images = extractor_instance.get_processed_images()
        
        # Calculate some basic metrics
        total_size = 0
        valid_images = 0
        
        for image_path in processed_images[:50]:  # Sample for performance
            try:
                import os
                if os.path.exists(image_path):
                    total_size += os.path.getsize(image_path)
                    valid_images += 1
            except Exception:
                continue
        
        avg_size = total_size / valid_images if valid_images > 0 else 0
        
        return {
            "database": {
                "total_images": stats['total_images'],
                "collection_name": stats['collection_name'],
                "estimated_avg_file_size_mb": avg_size / (1024 * 1024) if avg_size > 0 else 0,
                "estimated_total_size_mb": (avg_size * stats['total_images']) / (1024 * 1024) if avg_size > 0 else 0,
            },
            "processing": {
                "valid_images_sampled": valid_images,
                "sample_size": min(50, len(processed_images)),
            },
            "system": {
                "uptime_seconds": time.time() - service_start_time,
                "memory_usage_mb": psutil.Process().memory_info().rss / (1024 * 1024),
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/models/status")
async def get_model_status(extractor_instance = Depends(get_extractor_lazy)):
    """Get current model loading status without triggering loads."""
    try:
        status = extractor_instance.model_manager.get_model_status()
        info = extractor_instance.model_manager.get_model_info()
        return {
            "models": status,
            "model_info": info,
            "device": extractor_instance.config.model.device,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/models/preload")
async def preload_models(extractor_instance = Depends(get_extractor_lazy)):
    """Preload all models and return timing information."""
    try:
        logger.info("Starting model preloading via API request")
        timings = extractor_instance.model_manager.preload_all_models()
        
        return {
            "success": True,
            "timings": timings,
            "device": extractor_instance.config.model.device,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error preloading models: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }