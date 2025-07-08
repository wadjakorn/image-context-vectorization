"""Pydantic models for API requests."""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from pathlib import Path
import os


class ProcessImageRequest(BaseModel):
    """Request model for processing a single image."""
    image_path: str = Field(..., description="Path to the image file")
    force_reprocess: bool = Field(False, description="Force reprocessing even if already processed")
    
    @validator('image_path')
    def validate_image_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Image file not found: {v}")
        return v


class ProcessDirectoryRequest(BaseModel):
    """Request model for processing a directory of images."""
    directory_path: str = Field(..., description="Path to the directory containing images")
    force_reprocess: bool = Field(False, description="Force reprocessing even if already processed")
    recursive: bool = Field(False, description="Process subdirectories recursively")
    
    @validator('directory_path')
    def validate_directory_path(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Directory not found: {v}")
        if not os.path.isdir(v):
            raise ValueError(f"Path is not a directory: {v}")
        return v


class SearchRequest(BaseModel):
    """Request model for searching similar images."""
    query: str = Field(..., description="Search query", min_length=1)
    n_results: int = Field(5, description="Number of results to return", ge=1, le=100)
    include_metadata: bool = Field(True, description="Include image metadata in results")
    min_score: Optional[float] = Field(None, description="Minimum similarity score", ge=0.0, le=1.0)


class DuplicateCheckRequest(BaseModel):
    """Request model for checking duplicates."""
    image_path: Optional[str] = Field(None, description="Path to specific image to check")
    directory_path: Optional[str] = Field(None, description="Directory to scan for duplicates")
    similarity_threshold: float = Field(0.95, description="Similarity threshold for duplicates", ge=0.0, le=1.0)
    
    @validator('similarity_threshold')
    def validate_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        return v
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.image_path and not self.directory_path:
            raise ValueError("Either image_path or directory_path must be provided")


class UploadImageRequest(BaseModel):
    """Request model for image upload."""
    process_immediately: bool = Field(True, description="Process image immediately after upload")
    overwrite: bool = Field(False, description="Overwrite existing file if it exists")


class ConfigUpdateRequest(BaseModel):
    """Request model for updating configuration."""
    device: Optional[str] = Field(None, description="Processing device (cpu/cuda)")
    max_caption_length: Optional[int] = Field(None, description="Maximum caption length", ge=10, le=500)
    object_confidence_threshold: Optional[float] = Field(None, description="Object detection threshold", ge=0.0, le=1.0)
    
    class Config:
        extra = "forbid"  # Prevent additional fields