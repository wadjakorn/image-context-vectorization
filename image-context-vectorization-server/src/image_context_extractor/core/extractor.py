# NOTE: os import removed as it's not used
import logging
from typing import List, Dict, Any
# from PIL import Image

from ..config.settings import Config
from ..models.model_manager import ModelManager
from ..database.vector_db import VectorDatabase
from .image_processor import ImageProcessor


class ImageContextExtractor:
    def __init__(self, config: Config = None, skip_compatibility_check: bool = False):
        if config is None:
            config = Config()
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.model_manager = ModelManager(config.model)
        
        # Initialize database with optional compatibility check skip
        try:
            self.database = VectorDatabase(config.database, config.model, skip_compatibility_check=skip_compatibility_check)
        except Exception as e:
            if skip_compatibility_check:
                # In API dependency mode, create a degraded database instance
                self.logger.warning(f"Database initialization failed, creating degraded instance: {e}")
                self.database = None
            else:
                raise e
        
        self.image_processor = ImageProcessor(config.processing)
        
    def extract_image_features(self, image_path: str) -> Dict[str, Any]:
        """Extract various features from an image"""
        try:
            image = self.image_processor.load_image(image_path)
            
            caption = self.model_manager.generate_caption(
                image, 
                self.config.processing.max_caption_length, 
                self.config.processing.num_beams,
                self.config.processing.temperature,
                self.config.processing.repetition_penalty
            )
            
            clip_features = self.model_manager.extract_clip_features(image)
            
            metadata = self.image_processor.extract_metadata(image_path)
            
            objects = self.model_manager.detect_objects(
                image, 
                self.config.processing.object_categories, 
                self.config.processing.object_confidence_threshold
            )
            
            combined_text = f"{caption}. Objects: {', '.join(objects)}"
            # NOTE: Embedding creation removed - now handled by ChromaDB embedding function
            
            return {
                'image_path': image_path,
                'caption': caption,
                'clip_features': clip_features,
                'metadata': metadata,
                'objects': objects,
                'combined_text': combined_text
                # NOTE: 'embedding' field removed - now handled by ChromaDB embedding function
            }
        except Exception as e:
            self.logger.error(f"Error extracting features from {image_path}: {e}")
            raise
    
    def store_in_vector_db(self, image_features: Dict[str, Any]) -> str:
        """Store image features in vector database"""
        try:
            return self.database.store_image_data(image_features)
        except Exception as e:
            self.logger.error(f"Error storing image data: {e}")
            raise
    
    def process_image(self, image_path: str, force_reprocess: bool = False) -> str:
        """Complete pipeline: extract features and store in vector DB"""
        try:
            # Check if image already exists
            if not force_reprocess and self.database.image_exists(image_path):
                self.logger.info(f"Image already processed, skipping: {image_path}")
                import hashlib
                return hashlib.md5(image_path.encode()).hexdigest()
            
            self.logger.info(f"Processing image: {image_path}")
            
            features = self.extract_image_features(image_path)
            image_id = self.store_in_vector_db(features)
            
            self.logger.info(f"Successfully processed image {image_path} with ID: {image_id}")
            self.logger.debug(f"Caption: {features['caption']}")
            self.logger.debug(f"Objects: {features['objects']}")
            
            return image_id
        except Exception as e:
            self.logger.error(f"Failed to process image {image_path}: {e}")
            raise
    
    def search_similar_images(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar images using text query"""
        try:
            # NOTE: Embedding creation removed - ChromaDB handles embedding generation from query text
            results = self.database.search_similar(query, n_results)
            
            self.logger.info(f"Found {len(results)} similar images for query: '{query}'")
            return results
        except Exception as e:
            self.logger.error(f"Error searching for similar images: {e}")
            raise
    
    def process_directory(self, directory_path: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """Process all images in a directory"""
        try:
            image_files = self.image_processor.get_image_files(directory_path)
            processed_ids = []
            skipped_count = 0
            
            self.logger.info(f"Found {len(image_files)} image files in directory")
            
            for image_path in image_files:
                try:
                    if not force_reprocess and self.database.image_exists(image_path):
                        self.logger.debug(f"Skipping already processed image: {image_path}")
                        skipped_count += 1
                        continue
                    
                    image_id = self.process_image(image_path, force_reprocess)
                    processed_ids.append(image_id)
                except Exception as e:
                    self.logger.error(f"Failed to process {image_path}: {e}")
                    continue
            
            result = {
                'total_files': len(image_files),
                'processed': len(processed_ids),
                'skipped': skipped_count,
                'failed': len(image_files) - len(processed_ids) - skipped_count,
                'processed_ids': processed_ids
            }
            
            self.logger.info(f"Directory processing complete: {result['processed']} processed, {result['skipped']} skipped, {result['failed']} failed")
            return result
        except Exception as e:
            self.logger.error(f"Error processing directory {directory_path}: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if self.database is None:
            return {
                'total_images': 0,
                'collection_name': 'unavailable',
                'db_path': 'unavailable',
                'error': 'Database not available due to compatibility issues'
            }
        return self.database.get_collection_stats()
    
    def get_processed_images(self) -> List[str]:
        """Get list of all processed image paths"""
        if self.database is None:
            return []
        return self.database.get_processed_images()
    
    def is_image_processed(self, image_path: str) -> bool:
        """Check if an image has been processed"""
        if self.database is None:
            return False
        return self.database.image_exists(image_path)

    def get_image_data(self, image_path: str) -> Dict[str, Any]:
        """Get cached image data from database without re-processing"""
        if self.database is None:
            return None
        return self.database.get_image_data(image_path)

    def get_image_data_by_id(self, image_id: str) -> Dict[str, Any]:
        """Get cached image data by ID from database"""
        if self.database is None:
            return None
        return self.database.get_image_data_by_id(image_id)

    def get_all_images_data(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all processed images data with pagination"""
        if self.database is None:
            return []
        return self.database.get_all_image_data(limit, offset)
    
    def process_external_directory(self, directory_path: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """Process all images in an external directory using the directory validator"""
        try:
            from ..utils.directory_validator import DirectoryValidator
            
            # Initialize validator with supported formats
            validator = DirectoryValidator(self.config.processing.supported_formats)
            
            # Validate directory first
            dir_info = validator.validate_directory(directory_path)
            
            if not dir_info.accessible:
                raise ValueError(f"Directory is not accessible: {dir_info.error_message}")
            
            # Scan directory for image files
            image_files = validator.scan_directory_safe(
                directory_path,
                recursive=self.config.directory.external_dir_recursive,
                max_depth=self.config.directory.external_dir_max_depth,
                follow_symlinks=self.config.directory.external_dir_follow_symlinks
            )
            
            processed_ids = []
            skipped_count = 0
            failed_count = 0
            
            self.logger.info(f"Found {len(image_files)} image files in external directory: {directory_path}")
            
            for image_path in image_files:
                try:
                    if not force_reprocess and self.database.image_exists(image_path):
                        self.logger.debug(f"Skipping already processed image: {image_path}")
                        skipped_count += 1
                        continue
                    
                    image_id = self.process_image(image_path, force_reprocess)
                    processed_ids.append(image_id)
                except Exception as e:
                    self.logger.error(f"Failed to process {image_path}: {e}")
                    failed_count += 1
                    continue
            
            result = {
                'directory_path': directory_path,
                'directory_id': dir_info.id,
                'total_files': len(image_files),
                'processed': len(processed_ids),
                'skipped': skipped_count,
                'failed': failed_count,
                'processed_ids': processed_ids
            }
            
            self.logger.info(f"External directory processing complete: {result['processed']} processed, {result['skipped']} skipped, {result['failed']} failed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing external directory {directory_path}: {e}")
            raise

    def get_or_extract_image_features(self, image_path: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """Get image features from database or extract if not cached"""
        if not force_reprocess:
            cached_data = self.get_image_data(image_path)
            if cached_data:
                self.logger.debug(f"Using cached data for: {image_path}")
                return cached_data
        
        # Extract features if not cached or forced
        self.logger.info(f"Extracting features for: {image_path}")
        return self.extract_image_features(image_path)