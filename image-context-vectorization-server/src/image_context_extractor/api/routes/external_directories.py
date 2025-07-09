"""
API routes for external directories management.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ...config.settings import get_config
from ...utils.directory_validator import DirectoryValidator, DirectoryInfo
from ...core.extractor import ImageContextExtractor

router = APIRouter()

class ExternalDirectoryResponse(BaseModel):
    """Response model for external directory information"""
    id: str
    path: str
    name: str
    accessible: bool
    exists: bool
    readable: bool
    last_checked: str
    image_count: Optional[int] = None
    supported_image_count: Optional[int] = None
    error_message: Optional[str] = None

class ExternalDirectoriesListResponse(BaseModel):
    """Response model for external directories list"""
    external_directories: List[ExternalDirectoryResponse]

class DirectoryScanResponse(BaseModel):
    """Response model for directory scan results"""
    directory_id: str
    path: str
    total_files: int
    image_files: List[str]
    scan_time: str

class DirectoryProcessingResponse(BaseModel):
    """Response model for directory processing results"""
    directory_id: str
    path: str
    total_files: int
    processed_files: int
    failed_files: int
    processing_time: str
    task_id: Optional[str] = None

# Global variable to track processing tasks
processing_tasks: Dict[str, Dict[str, Any]] = {}

def _directory_info_to_response(directory_info: DirectoryInfo) -> ExternalDirectoryResponse:
    """Convert DirectoryInfo to ExternalDirectoryResponse"""
    return ExternalDirectoryResponse(
        id=directory_info.id,
        path=directory_info.path,
        name=directory_info.name,
        accessible=directory_info.accessible,
        exists=directory_info.exists,
        readable=directory_info.readable,
        last_checked=directory_info.last_checked,
        image_count=directory_info.image_count,
        supported_image_count=directory_info.supported_image_count,
        error_message=directory_info.error_message
    )

@router.get("/external", response_model=ExternalDirectoriesListResponse)
async def list_external_directories():
    """
    List all configured external directories with their status.
    """
    try:
        # Get configuration
        config = get_config()
        external_dirs = config.directory.external_directories
        
        if not external_dirs:
            return ExternalDirectoriesListResponse(external_directories=[])
        
        # Validate directories
        validator = DirectoryValidator(config.processing.supported_formats)
        directory_infos = validator.validate_directories(external_dirs)
        
        # Convert to response format
        response_dirs = [_directory_info_to_response(info) for info in directory_infos]
        
        return ExternalDirectoriesListResponse(external_directories=response_dirs)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing external directories: {str(e)}")

@router.get("/external/{directory_id}", response_model=ExternalDirectoryResponse)
async def get_external_directory(directory_id: str):
    """
    Get information about a specific external directory.
    """
    try:
        # Get configuration
        config = get_config()
        external_dirs = config.directory.external_directories
        
        if not external_dirs:
            raise HTTPException(status_code=404, detail="No external directories configured")
        
        # Validate directories and find the requested one
        validator = DirectoryValidator(config.processing.supported_formats)
        directory_infos = validator.validate_directories(external_dirs)
        
        # Find directory by ID
        target_info = None
        for info in directory_infos:
            if info.id == directory_id:
                target_info = info
                break
        
        if not target_info:
            raise HTTPException(status_code=404, detail=f"External directory with ID '{directory_id}' not found")
        
        return _directory_info_to_response(target_info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting external directory: {str(e)}")

@router.post("/scan-external/{directory_id}", response_model=DirectoryScanResponse)
async def scan_external_directory(directory_id: str):
    """
    Scan a specific external directory for image files.
    """
    try:
        # Get configuration
        config = get_config()
        external_dirs = config.directory.external_directories
        
        if not external_dirs:
            raise HTTPException(status_code=404, detail="No external directories configured")
        
        # Validate directories and find the requested one
        validator = DirectoryValidator(config.processing.supported_formats)
        directory_infos = validator.validate_directories(external_dirs)
        
        # Find directory by ID
        target_info = None
        for info in directory_infos:
            if info.id == directory_id:
                target_info = info
                break
        
        if not target_info:
            raise HTTPException(status_code=404, detail=f"External directory with ID '{directory_id}' not found")
        
        if not target_info.accessible:
            raise HTTPException(status_code=403, detail=f"Directory is not accessible: {target_info.error_message}")
        
        # Scan directory for image files
        image_files = validator.scan_directory_safe(
            target_info.path,
            recursive=config.directory.external_dir_recursive,
            max_depth=config.directory.external_dir_max_depth,
            follow_symlinks=config.directory.external_dir_follow_symlinks
        )
        
        from datetime import datetime
        
        return DirectoryScanResponse(
            directory_id=directory_id,
            path=target_info.path,
            total_files=len(image_files),
            image_files=image_files,
            scan_time=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning external directory: {str(e)}")

async def _process_directory_task(directory_id: str, directory_path: str, image_files: List[str]):
    """Background task for processing directory images"""
    import asyncio
    from datetime import datetime
    
    try:
        # Update task status
        processing_tasks[directory_id] = {
            "status": "processing",
            "total_files": len(image_files),
            "processed_files": 0,
            "failed_files": 0,
            "start_time": datetime.now().isoformat(),
            "path": directory_path
        }
        
        # Get configuration and initialize extractor
        config = get_config()
        extractor = ImageContextExtractor(config)
        
        processed_count = 0
        failed_count = 0
        
        # Process each image file
        for i, image_file in enumerate(image_files):
            try:
                # Check if already processed to avoid duplicates
                if not extractor.is_image_processed(image_file):
                    # Run the synchronous processing in a thread pool
                    await asyncio.get_event_loop().run_in_executor(
                        None, extractor.process_image, image_file
                    )
                processed_count += 1
                
                # Update progress
                processing_tasks[directory_id]["processed_files"] = processed_count
                
                # Yield control back to event loop every 5 images or every image if < 10 total
                if i % 5 == 0 or len(image_files) < 10:
                    await asyncio.sleep(0.01)  # Small delay to prevent blocking
                
            except Exception as e:
                failed_count += 1
                processing_tasks[directory_id]["failed_files"] = failed_count
                print(f"Error processing {image_file}: {str(e)}")
                # Continue processing other files
        
        # Update final status
        processing_tasks[directory_id].update({
            "status": "completed",
            "processed_files": processed_count,
            "failed_files": failed_count,
            "end_time": datetime.now().isoformat()
        })
        
    except Exception as e:
        # Update error status
        processing_tasks[directory_id] = {
            "status": "error",
            "error_message": str(e),
            "end_time": datetime.now().isoformat()
        }

@router.post("/process-external/{directory_id}", response_model=DirectoryProcessingResponse)
async def process_external_directory(directory_id: str):
    """
    Process images in a specific external directory.
    """
    try:
        # Get configuration
        config = get_config()
        external_dirs = config.directory.external_directories
        
        if not external_dirs:
            raise HTTPException(status_code=404, detail="No external directories configured")
        
        # Validate directories and find the requested one
        validator = DirectoryValidator(config.processing.supported_formats)
        directory_infos = validator.validate_directories(external_dirs)
        
        # Find directory by ID
        target_info = None
        for info in directory_infos:
            if info.id == directory_id:
                target_info = info
                break
        
        if not target_info:
            raise HTTPException(status_code=404, detail=f"External directory with ID '{directory_id}' not found")
        
        if not target_info.accessible:
            raise HTTPException(status_code=403, detail=f"Directory is not accessible: {target_info.error_message}")
        
        # Check if already processing
        if directory_id in processing_tasks and processing_tasks[directory_id].get("status") == "processing":
            raise HTTPException(status_code=409, detail="Directory is already being processed")
        
        # Scan directory for image files
        image_files = validator.scan_directory_safe(
            target_info.path,
            recursive=config.directory.external_dir_recursive,
            max_depth=config.directory.external_dir_max_depth,
            follow_symlinks=config.directory.external_dir_follow_symlinks
        )
        
        if not image_files:
            raise HTTPException(status_code=404, detail="No supported image files found in directory")
        
        # Start background processing task
        import asyncio
        asyncio.create_task(_process_directory_task(directory_id, target_info.path, image_files))
        
        from datetime import datetime
        
        return DirectoryProcessingResponse(
            directory_id=directory_id,
            path=target_info.path,
            total_files=len(image_files),
            processed_files=0,
            failed_files=0,
            processing_time=datetime.now().isoformat(),
            task_id=directory_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing external directory: {str(e)}")

@router.get("/processing-status/{directory_id}")
async def get_processing_status(directory_id: str):
    """
    Get the processing status of a directory.
    """
    if directory_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Processing task not found")
    
    return processing_tasks[directory_id]

@router.get("/processing-status")
async def get_all_processing_status():
    """
    Get the processing status of all directories.
    """
    return {"processing_tasks": processing_tasks}