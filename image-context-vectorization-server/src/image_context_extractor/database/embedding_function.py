import chromadb
from sentence_transformers import SentenceTransformer
import logging
import time


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
            
            kwargs = {'device': self.device}
            if self.cache_folder:
                kwargs['cache_folder'] = self.cache_folder
                
            self._model = SentenceTransformer(self.model_name, **kwargs)
            
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
        return {
            'model_name': self.model_name,
            'device': self.device,
            'cache_folder': self.cache_folder,
            'loaded': self.is_loaded()
        }