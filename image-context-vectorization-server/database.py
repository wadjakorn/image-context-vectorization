import chromadb
import json
import hashlib
import numpy as np
from typing import List, Dict, Any
import logging

from config import DatabaseConfig


class VectorDatabase:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        try:
            self.client = chromadb.PersistentClient(path=config.db_path)
            self.collection = self.client.get_or_create_collection(config.collection_name)
            self.logger.info(f"Connected to database at {config.db_path}")
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise

    def store_image_data(self, image_features: Dict[str, Any]) -> str:
        try:
            image_id = hashlib.md5(image_features['image_path'].encode()).hexdigest()
            
            metadata = {
                'image_path': image_features['image_path'],
                'caption': image_features['caption'],
                'filename': image_features['metadata']['filename'],
                'objects': json.dumps(image_features['objects']),
                'size': f"{image_features['metadata']['size'][0]}x{image_features['metadata']['size'][1]}",
                'format': image_features['metadata']['format']
            }
            
            self.collection.add(
                embeddings=[image_features['embedding'].tolist()],
                documents=[image_features['combined_text']],
                metadatas=[metadata],
                ids=[image_id]
            )
            
            self.logger.debug(f"Stored image data with ID: {image_id}")
            return image_id
        except Exception as e:
            self.logger.error(f"Error storing image data: {e}")
            raise

    def search_similar(self, query_embedding: np.ndarray, n_results: int = 5) -> List[Dict]:
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'distance': results['distances'][0][i],
                    'image_path': results['metadatas'][0][i]['image_path'],
                    'caption': results['metadatas'][0][i]['caption'],
                    'objects': json.loads(results['metadatas'][0][i]['objects'])
                }
                formatted_results.append(result)
            
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error searching database: {e}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        try:
            count = self.collection.count()
            return {
                'total_images': count,
                'collection_name': self.config.collection_name,
                'db_path': self.config.db_path
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            raise

    def image_exists(self, image_path: str) -> bool:
        """Check if an image has already been processed"""
        try:
            image_id = hashlib.md5(image_path.encode()).hexdigest()
            results = self.collection.get(ids=[image_id])
            return len(results['ids']) > 0
        except Exception as e:
            self.logger.error(f"Error checking if image exists: {e}")
            return False

    def get_processed_images(self) -> List[str]:
        """Get list of all processed image paths"""
        try:
            results = self.collection.get()
            if results['metadatas']:
                return [metadata['image_path'] for metadata in results['metadatas']]
            return []
        except Exception as e:
            self.logger.error(f"Error getting processed images: {e}")
            return []