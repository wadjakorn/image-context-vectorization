# NOTE: os import removed as it's not used
import chromadb
import json
import hashlib
import numpy as np
from typing import List, Dict, Any
import logging

from ..config.settings import DatabaseConfig, ModelConfig
from ..utils.chromadb_utils import setup_chromadb
from .embedding_function import CustomSentenceTransformerEmbeddingFunction

# Ensure ChromaDB telemetry is disabled
setup_chromadb()


class VectorDatabase:
    def __init__(self, config: DatabaseConfig, model_config: ModelConfig = None):
        self.config = config
        self.model_config = model_config
        self.logger = logging.getLogger(__name__)
        
        try:
            self.client = chromadb.PersistentClient(path=config.db_path)
            
            # Create custom embedding function if model config is provided
            if model_config:
                model_path = model_config.local_sentence_transformer_path or model_config.sentence_transformer_model
                embedding_function = CustomSentenceTransformerEmbeddingFunction(
                    model_name=model_path,
                    device=model_config.device,
                    cache_folder=model_config.cache_dir
                )
                self.collection = self.client.get_or_create_collection(
                    name=config.collection_name,
                    embedding_function=embedding_function
                )
                self.logger.info(f"Created collection with custom embedding function: {model_path}")
            else:
                # Fallback to default embedding function (for backward compatibility)
                self.collection = self.client.get_or_create_collection(config.collection_name)
                self.logger.warning("Using default embedding function - consider providing model_config")
            
            self.logger.info(f"Connected to database at {config.db_path}")
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise

    def _safe_get_embedding(self, embeddings, index=0):
        """
        Safely extract embedding from ChromaDB results.
        
        Fixes: "The truth value of an array with more than one element is ambiguous"
        This error occurs when trying to use boolean logic directly on numpy arrays.
        """
        if embeddings is None:
            return None
        if not isinstance(embeddings, list):
            return None
        if len(embeddings) <= index:
            return None
        
        embedding = embeddings[index]
        if embedding is None:
            return None
            
        try:
            return np.array(embedding)
        except Exception as e:
            self.logger.warning(f"Error converting embedding to numpy array: {e}")
            return None

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
            
            # ChromaDB will automatically generate embeddings from documents using our custom embedding function
            self.collection.add(
                documents=[image_features['combined_text']],
                metadatas=[metadata],
                ids=[image_id]
            )
            
            self.logger.debug(f"Stored image data with ID: {image_id}")
            return image_id
        except Exception as e:
            self.logger.error(f"Error storing image data: {e}")
            raise

    def search_similar(self, query_text: str, n_results: int = 5) -> List[Dict]:
        try:
            # ChromaDB will automatically generate embeddings from query_texts using our custom embedding function
            results = self.collection.query(
                query_texts=[query_text],
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

    def get_image_data(self, image_path: str) -> Dict[str, Any]:
        """Get stored image data by path"""
        try:
            image_id = hashlib.md5(image_path.encode()).hexdigest()
            results = self.collection.get(ids=[image_id], include=['metadatas', 'documents', 'embeddings'])
            
            if not results['ids'] or len(results['ids']) == 0:
                return None
                
            metadata = results['metadatas'][0]
            document = results['documents'][0]
            embedding = self._safe_get_embedding(results.get('embeddings'), 0)
            
            # Parse objects from JSON string
            objects = json.loads(metadata.get('objects', '[]'))
            
            return {
                'id': results['ids'][0],
                'image_path': metadata['image_path'],
                'caption': metadata['caption'],
                'filename': metadata['filename'],
                'size': metadata['size'],
                'format': metadata['format'],
                'objects': objects,
                'combined_text': document,
                'embedding': embedding
            }
        except Exception as e:
            self.logger.error(f"Error getting image data for {image_path}: {e}")
            return None

    def get_image_data_by_id(self, image_id: str) -> Dict[str, Any]:
        """Get stored image data by ID"""
        try:
            results = self.collection.get(ids=[image_id], include=['metadatas', 'documents', 'embeddings'])
            
            if not results['ids'] or len(results['ids']) == 0:
                return None
                
            metadata = results['metadatas'][0]
            document = results['documents'][0]
            embedding = self._safe_get_embedding(results.get('embeddings'), 0)
            
            # Parse objects from JSON string
            objects = json.loads(metadata.get('objects', '[]'))
            
            return {
                'id': results['ids'][0],
                'image_path': metadata['image_path'],
                'caption': metadata['caption'],
                'filename': metadata['filename'],
                'size': metadata['size'],
                'format': metadata['format'],
                'objects': objects,
                'combined_text': document,
                'embedding': embedding
            }
        except Exception as e:
            self.logger.error(f"Error getting image data for ID {image_id}: {e}")
            return None

    def get_all_image_data(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all stored image data with pagination"""
        try:
            # ChromaDB doesn't have built-in pagination, so we get all and slice
            results = self.collection.get(include=['metadatas', 'documents', 'embeddings'])
            
            if not results['ids']:
                return []
            
            image_data_list = []
            total_items = len(results['ids'])
            
            # Apply offset and limit
            start_idx = offset
            end_idx = start_idx + limit if limit else total_items
            end_idx = min(end_idx, total_items)
            
            for i in range(start_idx, end_idx):
                metadata = results['metadatas'][i]
                document = results['documents'][i]
                embedding = self._safe_get_embedding(results.get('embeddings'), i)
                
                # Parse objects from JSON string
                objects = json.loads(metadata.get('objects', '[]'))
                
                image_data = {
                    'id': results['ids'][i],
                    'image_path': metadata['image_path'],
                    'caption': metadata['caption'],
                    'filename': metadata['filename'],
                    'size': metadata['size'],
                    'format': metadata['format'],
                    'objects': objects,
                    'combined_text': document,
                    'embedding': embedding
                }
                image_data_list.append(image_data)
            
            return image_data_list
        except Exception as e:
            self.logger.error(f"Error getting all image data: {e}")
            return []

    def clear_all_images(self) -> bool:
        """Clear all images from the database collection"""
        try:
            # Get all document IDs
            results = self.collection.get()
            if results['ids']:
                # Delete all documents
                self.collection.delete(ids=results['ids'])
                self.logger.info(f"Cleared {len(results['ids'])} images from database")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing database: {e}")
            return False