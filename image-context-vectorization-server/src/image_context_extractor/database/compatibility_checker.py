"""
Database compatibility checker that reads metadata without initializing collections
"""
import chromadb
import logging
from typing import Dict, Any, Optional

from ..config.settings import DatabaseConfig, ModelConfig
from ..utils.chromadb_utils import setup_chromadb
from .embedding_function import CustomSentenceTransformerEmbeddingFunction


class DatabaseCompatibilityChecker:
    """
    Checks model compatibility with existing database without initializing collections.
    This prevents overwriting metadata before compatibility can be verified.
    """
    
    def __init__(self, db_config: DatabaseConfig, model_config: ModelConfig):
        self.db_config = db_config
        self.model_config = model_config
        self.logger = logging.getLogger(__name__)
        
        # Setup ChromaDB without telemetry
        setup_chromadb()
        
        # Create client but don't initialize collections yet
        self.client = chromadb.PersistentClient(path=db_config.db_path)
        
        # Create embedding function to get current model info
        if model_config:
            model_path = model_config.local_sentence_transformer_path or model_config.sentence_transformer_model
            self.embedding_function = CustomSentenceTransformerEmbeddingFunction(
                model_name=model_path,
                device=model_config.device,
                cache_folder=model_config.cache_dir
            )
        else:
            self.embedding_function = None
    
    def check_compatibility(self) -> Dict[str, Any]:
        """
        Check if current model configuration is compatible with existing database.
        This method reads existing metadata without modifying it.
        """
        try:
            # Check if collection already exists
            existing_collections = self.client.list_collections()
            collection_exists = any(col.name == self.db_config.collection_name for col in existing_collections)
            
            if not collection_exists:
                # No existing collection, so no compatibility issues
                new_model_info = None
                if self.embedding_function:
                    model_info = self.embedding_function.get_model_info()
                    if 'dimension' not in model_info or model_info['dimension'] is None:
                        model_info['dimension'] = self.embedding_function.get_dimension()
                    new_model_info = {
                        'name': model_info['model_name'],
                        'dimension': model_info['dimension']
                    }
                
                return {
                    'compatible': True,
                    'message': 'New collection will be created',
                    'current_model': None,
                    'new_model': new_model_info,
                    'reason': 'no_existing_collection'
                }
            
            if not self.embedding_function:
                # No model config provided, can't check compatibility
                return {
                    'compatible': True,
                    'message': 'No model configuration provided',
                    'current_model': None,
                    'new_model': None,
                    'reason': 'no_model_config'
                }
            
            # Get existing collection metadata WITHOUT initializing it
            try:
                existing_collection = self.client.get_collection(self.db_config.collection_name)
                existing_metadata = existing_collection.metadata or {}
            except Exception as e:
                self.logger.warning(f"Could not read existing collection metadata: {e}")
                # Collection exists but can't read metadata - assume incompatible
                current_model_info = self.embedding_function.get_model_info()
                return {
                    'compatible': False,
                    'message': 'Existing collection has no readable metadata. Database clearing required.',
                    'current_model': None,
                    'new_model': {
                        'name': current_model_info['model_name'],
                        'dimension': current_model_info.get('dimension')
                    },
                    'reason': 'unreadable_metadata'
                }
            
            # Get current model information (this will load the model to get dimensions)
            current_model_info = self.embedding_function.get_model_info()
            # Ensure we have dimension info
            if 'dimension' not in current_model_info or current_model_info['dimension'] is None:
                current_model_info['dimension'] = self.embedding_function.get_dimension()
            
            stored_model_name = existing_metadata.get('model_name')
            stored_dimension = existing_metadata.get('model_dimension')
            
            # Check model name compatibility
            if stored_model_name and stored_model_name != current_model_info['model_name']:
                return {
                    'compatible': False,
                    'message': f'Model changed: {stored_model_name} → {current_model_info["model_name"]}',
                    'current_model': {
                        'name': stored_model_name,
                        'dimension': stored_dimension
                    },
                    'new_model': {
                        'name': current_model_info['model_name'],
                        'dimension': current_model_info.get('dimension')
                    },
                    'reason': 'model_name_mismatch'
                }
            
            # Check dimension compatibility
            current_dimension = current_model_info.get('dimension')
            if (not stored_dimension) or (not current_dimension) or stored_dimension != current_dimension:
                return {
                    'compatible': False,
                    'message': f'Embedding dimension changed: {stored_dimension} → {current_dimension}',
                    'current_model': {
                        'name': stored_model_name,
                        'dimension': stored_dimension
                    },
                    'new_model': {
                        'name': current_model_info['model_name'],
                        'dimension': current_dimension
                    },
                    'reason': 'dimension_mismatch'
                }
            
            # Models are compatible
            return {
                'compatible': True,
                'message': 'Models are compatible',
                'current_model': {
                    'name': stored_model_name,
                    'dimension': stored_dimension
                },
                'new_model': {
                    'name': current_model_info['model_name'],
                    'dimension': current_dimension
                },
                'reason': 'compatible'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking model compatibility: {e}")
            return {
                'compatible': False,
                'message': f'Error checking compatibility: {str(e)}',
                'current_model': None,
                'new_model': None,
                'reason': 'check_error'
            }
    
    def clear_collection(self) -> bool:
        """
        Clear the existing collection completely.
        This is a destructive operation that removes all data.
        """
        try:
            self.client.delete_collection(self.db_config.collection_name)
            self.logger.info(f"Deleted collection: {self.db_config.collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting collection: {e}")
            return False
    
    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """
        Get basic information about the collection without initializing it.
        """
        try:
            existing_collections = self.client.list_collections()
            collection_exists = any(col.name == self.db_config.collection_name for col in existing_collections)
            
            if not collection_exists:
                return None
            
            existing_collection = self.client.get_collection(self.db_config.collection_name)
            return {
                'name': existing_collection.name,
                'count': existing_collection.count(),
                'metadata': existing_collection.metadata or {}
            }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {e}")
            return None


def check_database_compatibility(db_config: DatabaseConfig, model_config: ModelConfig) -> Dict[str, Any]:
    """
    Convenience function to check database compatibility without creating a checker instance.
    """
    checker = DatabaseCompatibilityChecker(db_config, model_config)
    return checker.check_compatibility()