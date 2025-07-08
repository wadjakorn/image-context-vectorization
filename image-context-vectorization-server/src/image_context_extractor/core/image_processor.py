import os
from PIL import Image
from typing import Dict, Any, List
import logging

from ..config.settings import ProcessingConfig


class ImageProcessor:
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def is_supported_format(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.config.supported_formats

    def load_image(self, image_path: str) -> Image.Image:
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            if not self.is_supported_format(image_path):
                raise ValueError(f"Unsupported image format: {image_path}")
            
            image = Image.open(image_path).convert('RGB')
            self.logger.debug(f"Loaded image: {image_path}")
            return image
        except Exception as e:
            self.logger.error(f"Error loading image {image_path}: {e}")
            raise

    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        try:
            image = Image.open(image_path)
            
            metadata = {
                'filename': os.path.basename(image_path),
                'size': image.size,
                'format': image.format,
                'mode': image.mode,
                'file_size': os.path.getsize(image_path)
            }
            
            return metadata
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {image_path}: {e}")
            raise

    def get_image_files(self, directory: str) -> List[str]:
        try:
            if not os.path.exists(directory):
                raise FileNotFoundError(f"Directory not found: {directory}")
            
            image_files = []
            for filename in os.listdir(directory):
                if self.is_supported_format(filename):
                    full_path = os.path.join(directory, filename)
                    image_files.append(full_path)
            
            self.logger.info(f"Found {len(image_files)} image files in {directory}")
            return image_files
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            raise