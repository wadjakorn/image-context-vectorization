"""
Image Context Extractor - A tool for extracting contextual information from images
and storing them in a vector database for similarity search.
"""

__version__ = "1.0.0"
__author__ = "Image Context Extractor Team"

from .core.extractor import ImageContextExtractor
from .config.settings import Config, get_config
from .config.model_paths import ModelPaths

__all__ = [
    "ImageContextExtractor",
    "Config", 
    "get_config",
    "ModelPaths"
]