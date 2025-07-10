import chromadb
from sentence_transformers import SentenceTransformer
import logging
import time
import torch


class CustomSentenceTransformerEmbeddingFunction(chromadb.EmbeddingFunction):
    """
    Custom ChromaDB embedding function that uses SentenceTransformer models.
    This ensures consistency between storage and search operations.
    """
    
    def __init__(self, model_name: str, device: str = "cpu", cache_folder: str = None):
        self.model_name = model_name
        self.device = device
        self.cache_folder = cache_folder
        self.logger = logging.getLogger(__name__)
        self._model = None
        
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the SentenceTransformer model."""
        if self._model is None:
            self.logger.info(f"🔄 Loading SentenceTransformer model: {self.model_name}")
            start_time = time.time()
            
            kwargs = {}
            if self.cache_folder:
                kwargs['cache_folder'] = self.cache_folder
            
            # Add modern SentenceTransformer parameters for better memory management
            model_kwargs = {
                'torch_dtype': torch.float32,  # Explicitly avoid auto dtype that can cause meta tensors
                'low_cpu_mem_usage': True,     # Better memory management
            }
            kwargs['model_kwargs'] = model_kwargs
            
            # Load model with multiple fallback strategies
            try:
                # Strategy 1: Load with optimized parameters
                self._model = SentenceTransformer(self.model_name, **kwargs)
                
                # Move to device after loading if not CPU
                if self.device != "cpu":
                    self.logger.info(f"🔄 Moving SentenceTransformer to {self.device}")
                    device_start = time.time()
                    
                    # Check if model has meta tensors
                    has_meta_tensors = any(
                        param.device.type == 'meta' 
                        for param in self._model.parameters()
                    )
                    
                    if has_meta_tensors:
                        self.logger.info("🔍 Detected meta tensors, using to_empty() method")
                        # Use to_empty() for meta tensors
                        try:
                            self._model = self._model.to_empty(device=self.device)
                        except AttributeError:
                            # Fallback if to_empty() is not available
                            self.logger.warning("⚠️ to_empty() not available, trying alternative approach")
                            # Try loading directly with device parameter
                            self._model = SentenceTransformer(self.model_name, device=self.device, **kwargs)
                    else:
                        # Use standard to() method for non-meta tensors
                        self._model = self._model.to(self.device)
                    
                    device_time = time.time() - device_start
                    self.logger.info(f"✅ SentenceTransformer moved to {self.device} in {device_time:.2f} seconds")
                    
            except Exception as e:
                self.logger.error(f"❌ Failed to load SentenceTransformer: {e}")
                # Fallback strategy 2: Load with device parameter directly
                if self.device != "cpu":
                    self.logger.warning(f"🔄 Trying direct device loading for {self.device}")
                    try:
                        # Remove model_kwargs that might cause issues
                        simple_kwargs = {k: v for k, v in kwargs.items() if k != 'model_kwargs'}
                        self._model = SentenceTransformer(self.model_name, device=self.device, **simple_kwargs)
                    except Exception as device_e:
                        self.logger.error(f"❌ Direct device loading failed: {device_e}")
                        # Fallback strategy 3: CPU fallback
                        self.logger.warning(f"🔄 Falling back to CPU for SentenceTransformer")
                        try:
                            simple_kwargs = {k: v for k, v in kwargs.items() if k != 'model_kwargs'}
                            self._model = SentenceTransformer(self.model_name, device="cpu", **simple_kwargs)
                            self.device = "cpu"  # Update device to reflect actual device
                        except Exception as fallback_e:
                            self.logger.error(f"❌ CPU fallback also failed: {fallback_e}")
                            raise fallback_e
                else:
                    # Fallback strategy 4: Minimal loading for CPU
                    self.logger.warning("🔄 Trying minimal CPU loading")
                    try:
                        minimal_kwargs = {}
                        if self.cache_folder:
                            minimal_kwargs['cache_folder'] = self.cache_folder
                        self._model = SentenceTransformer(self.model_name, **minimal_kwargs)
                    except Exception as minimal_e:
                        self.logger.error(f"❌ Minimal loading failed: {minimal_e}")
                        raise minimal_e
            
            load_time = time.time() - start_time
            self.logger.info(f"✅ SentenceTransformer loaded in {load_time:.2f} seconds")
            
        return self._model
    
    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        """
        Create embeddings for the given documents.
        
        Args:
            input: List of text documents to embed
            
        Returns:
            List of embeddings as lists of floats
        """
        try:
            # Encode the input documents
            embeddings = self.model.encode(input, convert_to_numpy=True)
            
            # Convert to list format expected by ChromaDB
            if len(embeddings.shape) == 1:
                # Single embedding
                return embeddings.tolist()
            else:
                # Multiple embeddings
                return embeddings.tolist()
                
        except Exception as e:
            self.logger.error(f"Error creating embeddings: {e}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._model is not None
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        info = {
            'model_name': self.model_name,
            'device': self.device,
            'cache_folder': self.cache_folder,
            'loaded': self.is_loaded()
        }
        
        # Add dimension info if model is loaded
        if self.is_loaded():
            info['dimension'] = self.get_dimension()
        
        return info
    
    def get_dimension(self) -> int:
        """Get the embedding dimension of the model."""
        # This will trigger model loading if not already loaded
        temp_embedding = self.model.encode(["test"], convert_to_numpy=True)
        return temp_embedding.shape[-1]