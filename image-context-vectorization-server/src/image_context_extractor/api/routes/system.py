"""
System-level API routes for model compatibility and database management
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ...config.settings import get_config
from ...database.vector_db import VectorDatabase

router = APIRouter(prefix="/api/v1/system", tags=["system"])
logger = logging.getLogger(__name__)


def get_vector_db():
    """Dependency to get VectorDatabase instance"""
    config = get_config()
    return VectorDatabase(config.database, config.model)


@router.get("/model-compatibility")
async def check_model_compatibility() -> Dict[str, Any]:
    """
    Check if current model configuration is compatible with existing database.
    This endpoint is used by the frontend to determine if a blocking modal should be shown.
    """
    try:
        config = get_config()
        
        # Use the standalone compatibility checker
        if not config.model:
            return {
                "compatible": True,
                "message": "No model configuration provided",
                "requires_clearing": False
            }
        
        # Import the compatibility checker
        from ...database.compatibility_checker import DatabaseCompatibilityChecker
        
        # Check compatibility without initializing collections
        checker = DatabaseCompatibilityChecker(config.database, config.model)
        compatibility_status = checker.check_compatibility()
        
        return {
            "compatible": compatibility_status["compatible"],
            "message": compatibility_status["message"],
            "requires_clearing": not compatibility_status["compatible"],
            "current_model": compatibility_status.get("current_model"),
            "new_model": compatibility_status.get("new_model"),
            "reason": compatibility_status.get("reason")
        }
        
    except Exception as e:
        logger.error(f"Error checking model compatibility: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking compatibility: {str(e)}")


@router.post("/clear-database")
async def clear_database_and_restart() -> Dict[str, Any]:
    """
    Clear the entire database and recreate it with the current model configuration.
    This is called when the user confirms they want to clear the database due to model incompatibility.
    """
    try:
        config = get_config()
        
        # Use the compatibility checker to clear the database
        from ...database.compatibility_checker import DatabaseCompatibilityChecker
        checker = DatabaseCompatibilityChecker(config.database, config.model)
        
        # Clear the existing collection
        success = checker.clear_collection()
        
        if success:
            # Get new model info
            if config.model and checker.embedding_function:
                model_info = checker.embedding_function.get_model_info()
                new_model = {
                    "name": model_info['model_name'],
                    "dimension": model_info.get('dimension')
                }
            else:
                new_model = None
            
            return {
                "success": True,
                "message": "Database cleared and reset successfully",
                "new_model": new_model
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database")
            
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")


@router.get("/health")
async def system_health() -> Dict[str, Any]:
    """
    Get overall system health including model compatibility status
    """
    try:
        # Check model compatibility
        compatibility_result = await check_model_compatibility()
        
        config = get_config()
        
        return {
            "status": "healthy" if compatibility_result["compatible"] else "incompatible_model",
            "model_compatibility": compatibility_result,
            "database_path": config.database.db_path,
            "collection_name": config.database.collection_name,
            "current_model": config.model.sentence_transformer_model if config.model else None
        }
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {
            "status": "error",
            "error": str(e)
        }