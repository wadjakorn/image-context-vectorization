"""Pydantic models for API responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ImageInfo(BaseModel):
    """Model for image information."""
    id: str = Field(..., description="Unique image ID")
    path: str = Field(..., description="Image file path")
    filename: str = Field(..., description="Image filename")
    size: tuple[int, int] = Field(..., description="Image dimensions (width, height)")
    file_size: int = Field(..., description="File size in bytes")
    format: str = Field(..., description="Image format")
    caption: Optional[str] = Field(None, description="Generated caption")
    objects: List[str] = Field(default_factory=list, description="Detected objects")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")
    score: Optional[float] = Field(None, description="Similarity score (search mode only)")
    distance: Optional[float] = Field(None, description="Similarity distance (search mode only)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProcessImageResponse(BaseModel):
    """Response model for image processing."""
    success: bool = Field(..., description="Whether processing was successful")
    image_id: Optional[str] = Field(None, description="Generated image ID")
    message: str = Field(..., description="Status message")
    image_info: Optional[ImageInfo] = Field(None, description="Processed image information")
    processing_time: float = Field(..., description="Processing time in seconds")
    was_duplicate: bool = Field(False, description="Whether image was already processed")


class ProcessDirectoryResponse(BaseModel):
    """Response model for directory processing."""
    success: bool = Field(..., description="Whether processing was successful")
    total_files: int = Field(..., description="Total image files found")
    processed: int = Field(..., description="Number of images processed")
    skipped: int = Field(..., description="Number of images skipped")
    failed: int = Field(..., description="Number of failed images")
    processed_ids: List[str] = Field(default_factory=list, description="IDs of processed images")
    failed_files: List[str] = Field(default_factory=list, description="List of failed file paths")
    processing_time: float = Field(..., description="Total processing time in seconds")
    message: str = Field(..., description="Status message")


class SearchResult(BaseModel):
    """Model for search result item."""
    id: str = Field(..., description="Image ID")
    image_path: str = Field(..., description="Image file path")
    caption: str = Field(..., description="Image caption")
    objects: List[str] = Field(..., description="Detected objects")
    distance: float = Field(..., description="Similarity distance (lower = more similar)")
    score: float = Field(..., description="Similarity score (higher = more similar)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchResponse(BaseModel):
    """Response model for search requests."""
    success: bool = Field(..., description="Whether search was successful")
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of results found")
    results: List[SearchResult] = Field(..., description="Search results")
    search_time: float = Field(..., description="Search time in seconds")
    message: str = Field(..., description="Status message")


class DuplicateGroup(BaseModel):
    """Model for a group of duplicate images."""
    representative_id: str = Field(..., description="ID of the representative image")
    duplicate_ids: List[str] = Field(..., description="IDs of duplicate images")
    similarity_scores: List[float] = Field(..., description="Similarity scores")
    paths: List[str] = Field(..., description="File paths of all images in group")


class DuplicateCheckResponse(BaseModel):
    """Response model for duplicate checking."""
    success: bool = Field(..., description="Whether check was successful")
    total_images: int = Field(..., description="Total images checked")
    duplicate_groups: List[DuplicateGroup] = Field(..., description="Groups of duplicate images")
    total_duplicates: int = Field(..., description="Total number of duplicate images found")
    check_time: float = Field(..., description="Check time in seconds")
    message: str = Field(..., description="Status message")


class DatabaseStats(BaseModel):
    """Model for database statistics."""
    total_images: int = Field(..., description="Total number of images in database")
    collection_name: str = Field(..., description="Database collection name")
    db_path: str = Field(..., description="Database file path")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    database_connected: bool = Field(..., description="Database connection status")
    models_loaded: bool = Field(..., description="AI models loading status")
    uptime: float = Field(..., description="Service uptime in seconds")
    stats: Optional[DatabaseStats] = Field(None, description="Database statistics")


class UploadImageResponse(BaseModel):
    """Response model for image upload."""
    success: bool = Field(..., description="Whether upload was successful")
    filename: str = Field(..., description="Uploaded filename")
    file_path: str = Field(..., description="Saved file path")
    file_size: int = Field(..., description="File size in bytes")
    image_id: Optional[str] = Field(None, description="Generated image ID if processed")
    message: str = Field(..., description="Status message")


class TaskStatus(BaseModel):
    """Model for background task status."""
    task_id: str = Field(..., description="Unique task ID")
    status: ProcessingStatus = Field(..., description="Current task status")
    progress: float = Field(..., description="Progress percentage (0-100)")
    message: str = Field(..., description="Current status message")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConfigResponse(BaseModel):
    """Response model for configuration."""
    device: str = Field(..., description="Current processing device")
    max_caption_length: int = Field(..., description="Maximum caption length")
    object_confidence_threshold: float = Field(..., description="Object detection threshold")
    supported_formats: List[str] = Field(..., description="Supported image formats")
    models_loaded: Dict[str, bool] = Field(..., description="Status of loaded models")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }