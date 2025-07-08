"""API routes for directory processing operations."""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends

from ..models.requests import ProcessDirectoryRequest
from ..models.responses import ProcessDirectoryResponse, TaskStatus, ProcessingStatus
from ..dependencies import get_extractor_lazy
from ...core.extractor import ImageContextExtractor


router = APIRouter(prefix="/api/v1/directories", tags=["directories"])
logger = logging.getLogger(__name__)

# Background task storage (in production, use Redis or similar)
background_tasks: Dict[str, Dict[str, Any]] = {}




def process_directory_background(
    task_id: str,
    request: ProcessDirectoryRequest,
    extractor: ImageContextExtractor
):
    """Background task for processing directory."""
    try:
        # Update task status
        background_tasks[task_id]["status"] = ProcessingStatus.PROCESSING
        background_tasks[task_id]["message"] = "Starting directory scan..."
        
        start_time = time.time()
        
        # Get all image files
        image_files = extractor.image_processor.get_image_files(request.directory_path)
        
        if request.recursive:
            # Add recursive scanning
            for root, dirs, files in os.walk(request.directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if extractor.image_processor.is_supported_format(file_path):
                        if file_path not in image_files:
                            image_files.append(file_path)
        
        total_files = len(image_files)
        background_tasks[task_id]["total_files"] = total_files
        background_tasks[task_id]["message"] = f"Found {total_files} image files"
        
        processed_ids = []
        skipped_count = 0
        failed_files = []
        
        for i, image_path in enumerate(image_files):
            try:
                # Update progress
                progress = (i / total_files) * 100
                background_tasks[task_id]["progress"] = progress
                background_tasks[task_id]["message"] = f"Processing {os.path.basename(image_path)} ({i+1}/{total_files})"
                
                # Check if already processed
                if not request.force_reprocess and extractor.database.image_exists(image_path):
                    skipped_count += 1
                    continue
                
                # Process image
                image_id = extractor.process_image(image_path, request.force_reprocess)
                processed_ids.append(image_id)
                
            except Exception as e:
                logger.error(f"Failed to process {image_path}: {e}")
                failed_files.append(image_path)
                continue
        
        processing_time = time.time() - start_time
        
        # Update final status
        background_tasks[task_id]["status"] = ProcessingStatus.COMPLETED
        background_tasks[task_id]["progress"] = 100
        background_tasks[task_id]["processing_time"] = processing_time
        background_tasks[task_id]["result"] = {
            "total_files": total_files,
            "processed": len(processed_ids),
            "skipped": skipped_count,
            "failed": len(failed_files),
            "processed_ids": processed_ids,
            "failed_files": failed_files,
            "processing_time": processing_time
        }
        background_tasks[task_id]["message"] = f"Completed: {len(processed_ids)} processed, {skipped_count} skipped, {len(failed_files)} failed"
        
    except Exception as e:
        logger.error(f"Error in background directory processing: {e}")
        background_tasks[task_id]["status"] = ProcessingStatus.FAILED
        background_tasks[task_id]["error"] = str(e)
        background_tasks[task_id]["message"] = f"Failed: {str(e)}"


@router.post("/process", response_model=ProcessDirectoryResponse)
async def process_directory(
    request: ProcessDirectoryRequest,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Process all images in a directory synchronously."""
    try:
        start_time = time.time()
        
        # Get image files
        image_files = extractor_instance.image_processor.get_image_files(request.directory_path)
        
        if request.recursive:
            # Add recursive scanning
            for root, dirs, files in os.walk(request.directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if extractor_instance.image_processor.is_supported_format(file_path):
                        if file_path not in image_files:
                            image_files.append(file_path)
        
        # Process directory
        result = extractor_instance.process_directory(
            request.directory_path,
            force_reprocess=request.force_reprocess
        )
        
        processing_time = time.time() - start_time
        
        return ProcessDirectoryResponse(
            success=True,
            total_files=result['total_files'],
            processed=result['processed'],
            skipped=result['skipped'],
            failed=result['failed'],
            processed_ids=result['processed_ids'],
            failed_files=[],  # Not tracked in current implementation
            processing_time=processing_time,
            message=f"Directory processed: {result['processed']} images processed"
        )
        
    except Exception as e:
        logger.error(f"Error processing directory {request.directory_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-async")
async def process_directory_async(
    request: ProcessDirectoryRequest,
    background_tasks: BackgroundTasks,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Process all images in a directory asynchronously."""
    try:
        import uuid
        from datetime import datetime
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        background_tasks_store = globals()['background_tasks']
        background_tasks_store[task_id] = {
            "task_id": task_id,
            "status": ProcessingStatus.PENDING,
            "progress": 0.0,
            "message": "Task queued",
            "result": None,
            "error": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "total_files": 0
        }
        
        # Add background task
        background_tasks.add_task(
            process_directory_background,
            task_id,
            request,
            extractor_instance
        )
        
        return {
            "task_id": task_id,
            "status": "queued",
            "message": "Directory processing started in background"
        }
        
    except Exception as e:
        logger.error(f"Error starting async directory processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan")
async def scan_directory(
    directory_path: str,
    recursive: bool = False,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Scan a directory for image files without processing them."""
    try:
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=404, detail="Directory not found")
        
        if not os.path.isdir(directory_path):
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        # Get image files
        image_files = extractor_instance.image_processor.get_image_files(directory_path)
        
        if recursive:
            # Add recursive scanning
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if extractor_instance.image_processor.is_supported_format(file_path):
                        if file_path not in image_files:
                            image_files.append(file_path)
        
        # Categorize files
        already_processed = []
        new_files = []
        
        for image_path in image_files:
            if extractor_instance.is_image_processed(image_path):
                already_processed.append(image_path)
            else:
                new_files.append(image_path)
        
        return {
            "directory_path": directory_path,
            "recursive": recursive,
            "total_files": len(image_files),
            "already_processed": len(already_processed),
            "new_files": len(new_files),
            "new_file_paths": new_files[:50],  # Limit response size
            "supported_formats": extractor_instance.config.processing.supported_formats
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error scanning directory {directory_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of a background processing task."""
    try:
        if task_id not in background_tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = background_tasks[task_id]
        
        return TaskStatus(
            task_id=task_id,
            status=task_data["status"],
            progress=task_data.get("progress", 0.0),
            message=task_data.get("message", ""),
            result=task_data.get("result"),
            error=task_data.get("error"),
            created_at=task_data["created_at"],
            updated_at=task_data.get("updated_at", task_data["created_at"])
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def list_tasks(limit: int = 50, status_filter: str = None):
    """List background processing tasks."""
    try:
        tasks = []
        
        for task_id, task_data in list(background_tasks.items())[-limit:]:
            if status_filter and task_data["status"] != status_filter:
                continue
                
            tasks.append({
                "task_id": task_id,
                "status": task_data["status"],
                "progress": task_data.get("progress", 0.0),
                "message": task_data.get("message", ""),
                "created_at": task_data["created_at"],
                "total_files": task_data.get("total_files", 0)
            })
        
        return {
            "tasks": tasks,
            "total": len(background_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))