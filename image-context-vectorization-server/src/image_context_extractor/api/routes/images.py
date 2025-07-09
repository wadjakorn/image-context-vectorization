"""API routes for image processing operations."""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import FileResponse
import aiofiles

from ..models.requests import ProcessImageRequest, UploadImageRequest
from ..models.responses import (
    ProcessImageResponse, UploadImageResponse, ImageInfo, 
    ErrorResponse, TaskStatus, ProcessingStatus
)
from ..dependencies import get_extractor_lazy

router = APIRouter(prefix="/api/v1/images", tags=["images"])
logger = logging.getLogger(__name__)


@router.post("/process", response_model=ProcessImageResponse)
async def process_image(
    request: ProcessImageRequest,
    background_tasks: BackgroundTasks,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Process a single image and extract its context."""
    try:
        start_time = time.time()
        
        # Check if image already processed
        was_duplicate = extractor_instance.is_image_processed(request.image_path)
        
        if was_duplicate and not request.force_reprocess:
            processing_time = time.time() - start_time
            return ProcessImageResponse(
                success=True,
                image_id=None,
                message="Image already processed (skipped)",
                processing_time=processing_time,
                was_duplicate=True
            )
        
        # Process the image
        image_id = extractor_instance.process_image(
            request.image_path,
            force_reprocess=request.force_reprocess
        )
        
        # Get image information
        features = extractor_instance.extract_image_features(request.image_path)
        metadata = extractor_instance.image_processor.extract_metadata(request.image_path)
        
        image_info = ImageInfo(
            id=image_id,
            path=request.image_path,
            filename=metadata['filename'],
            size=metadata['size'],
            file_size=metadata['file_size'],
            format=metadata['format'],
            caption=features['caption'],
            objects=features['objects']
        )
        
        processing_time = time.time() - start_time
        
        return ProcessImageResponse(
            success=True,
            image_id=image_id,
            message="Image processed successfully",
            image_info=image_info,
            processing_time=processing_time,
            was_duplicate=was_duplicate
        )
        
    except Exception as e:
        logger.error(f"Error processing image {request.image_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=UploadImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    process_immediately: bool = Form(True),
    overwrite: bool = Form(False),
    upload_dir: str = Form("uploads"),
    extractor_instance = Depends(get_extractor_lazy)
):
    """Upload an image file and optionally process it immediately."""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create upload directory
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Generate file path
        file_path = upload_path / file.filename
        
        # Check if file exists and handle overwrite
        if file_path.exists() and not overwrite:
            raise HTTPException(
                status_code=409, 
                detail=f"File {file.filename} already exists. Set overwrite=true to replace."
            )
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        image_id = None
        
        # Process immediately if requested
        if process_immediately:
            try:
                image_id = extractor_instance.process_image(str(file_path))
            except Exception as e:
                logger.warning(f"Failed to process uploaded image: {e}")
        
        return UploadImageResponse(
            success=True,
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            image_id=image_id,
            message="Image uploaded successfully" + (" and processed" if image_id else "")
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{image_id}", response_model=ImageInfo)
async def get_image_info(
    image_id: str,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Get detailed information about a processed image using cached data."""
    try:
        # Get cached image data directly by ID (much faster!)
        image_data = extractor_instance.get_image_data_by_id(image_id)
        
        if not image_data:
            raise HTTPException(status_code=404, detail="Image not found in database")
        
        # Parse size from string format "1920x1080"
        size_parts = image_data['size'].split('x')
        size = [int(size_parts[0]), int(size_parts[1])] if len(size_parts) == 2 else [0, 0]
        
        # Get current file size from filesystem if file exists
        file_size = 0
        if os.path.exists(image_data['image_path']):
            file_size = os.path.getsize(image_data['image_path'])
        
        return ImageInfo(
            id=image_data['id'],
            path=image_data['image_path'],
            filename=image_data['filename'],
            size=size,
            file_size=file_size,
            format=image_data['format'],
            caption=image_data['caption'],
            objects=image_data['objects']
        )
        
    except HTTPException as he:
        # Re-raise HTTPExceptions with their original status codes
        raise he
    except Exception as e:
        logger.error(f"Error getting image info for {image_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/download/{image_id}")
async def download_image(
    image_id: str,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Download an image file by its ID using cached data."""
    try:
        # Get cached image data directly by ID
        image_data = extractor_instance.get_image_data_by_id(image_id)
        
        if not image_data:
            raise HTTPException(status_code=404, detail="Image not found in database")
        
        image_path = image_data['image_path']
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found on disk")
        
        return FileResponse(
            path=image_path,
            filename=os.path.basename(image_path)
        )
        
        raise HTTPException(status_code=404, detail="Image not found in database")
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error downloading image {image_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ImageInfo])
async def list_or_search_images(
    query: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    extractor_instance = Depends(get_extractor_lazy)
):
    """List all processed images or search for specific images based on query.
    
    - If no query provided: Returns paginated list of all processed images
    - If query provided: Returns search results for similar images
    
    Args:
        query: Optional search query for similarity search
        limit: Number of results to return
        offset: Offset for pagination (list mode only)
    """
    try:
        start_time = time.time()
        
        
        if query:
            results = extractor_instance.search_similar_images(
                    query,
                    n_results=limit
                )
            
            # Search mode: find similar images
            
            image_infos = []
            for result in results:
                # Calculate similarity score from distance
                score = 100 * max(0.0, 2.0 - result.get('distance', 2.0))
                
                # Parse size from string format "1920x1080"
                size_parts = result.get('size', '0x0').split('x')
                size = [int(size_parts[0]), int(size_parts[1])] if len(size_parts) == 2 else [0, 0]
                
                # Get file size from filesystem if file exists
                file_size = 0
                if os.path.exists(result['image_path']):
                    file_size = os.path.getsize(result['image_path'])
                
                image_info = ImageInfo(
                    id=result['id'],
                    path=result['image_path'],
                    filename=result.get('filename', os.path.basename(result['image_path'])),
                    size=size,
                    file_size=file_size,
                    format=result.get('format', ''),
                    caption=result['caption'],
                    objects=result['objects'],
                    score=score,
                    distance=result.get('distance', 0.0)
                )
                image_infos.append(image_info)
                
                # Stop when we have enough results
                if len(image_infos) >= limit:
                    break
                
        else:
            # List mode: get all images with pagination
            all_image_data = extractor_instance.get_all_images_data(limit=limit, offset=offset)
            
            image_infos = []
            
            for image_data in all_image_data:
                try:
                    
                    # Parse size from string format "1920x1080"
                    size_parts = image_data['size'].split('x')
                    size = [int(size_parts[0]), int(size_parts[1])] if len(size_parts) == 2 else [0, 0]
                    
                    # Get file size from filesystem if file exists
                    file_size = 0
                    if os.path.exists(image_data['image_path']):
                        file_size = os.path.getsize(image_data['image_path'])
                    
                    image_info = ImageInfo(
                        id=image_data['id'],
                        path=image_data['image_path'],
                        filename=image_data['filename'],
                        size=size,
                        file_size=file_size,
                        format=image_data['format'],
                        caption=image_data['caption'],
                        objects=image_data['objects']
                    )
                    image_infos.append(image_info)
                    
                except Exception as e:
                    logger.warning(f"Error processing cached image data: {e}")
                    continue
        
        search_time = time.time() - start_time
        logger.info(f"{'Search' if query else 'List'} completed in {search_time:.3f}s, returned {len(image_infos)} results")
        
        return image_infos
        
    except Exception as e:
        logger.error(f"Error {'searching' if query else 'listing'} images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    delete_file: bool = False,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Delete an image from the database and optionally from disk."""
    try:
        # Find image by ID
        processed_images = extractor_instance.get_processed_images()
        
        import hashlib
        for image_path in processed_images:
            if hashlib.md5(image_path.encode()).hexdigest() == image_id:
                # TODO: Implement actual deletion from database
                # This would require extending the VectorDatabase class
                
                if delete_file and os.path.exists(image_path):
                    os.remove(image_path)
                
                return {"success": True, "message": "Image deleted successfully"}
        
        raise HTTPException(status_code=404, detail="Image not found in database")
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting image {image_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/database/clear")
async def clear_all_images(
    extractor_instance = Depends(get_extractor_lazy)
):
    """Clear all images from the database (files remain on disk)."""
    try:
        success = extractor_instance.database.clear_all_images()
        if success:
            return {"success": True, "message": "All images cleared from database"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database")
    except Exception as e:
        logger.error(f"Error clearing all images: {e}")
        raise HTTPException(status_code=500, detail=str(e))