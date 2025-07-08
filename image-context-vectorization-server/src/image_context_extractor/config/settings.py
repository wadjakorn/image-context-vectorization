import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv
from .model_paths import ModelPaths

# Disable ChromaDB telemetry early to prevent capture() errors
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_CLIENT_DISABLE_TELEMETRY", "True")


@dataclass
class ModelConfig:
    blip_model_name: str = "Salesforce/blip-image-captioning-base"
    clip_model_name: str = "openai/clip-vit-base-patch32"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    device: str = "cpu"
    
    # Local model paths (override remote models if provided)
    local_blip_model_path: Optional[str] = None
    local_clip_model_path: Optional[str] = None
    local_sentence_transformer_path: Optional[str] = None
    
    # Cache directory for downloaded models
    cache_dir: Optional[str] = None
    
    # Model loading options
    use_local_files_only: bool = False  # Force use of local files only
    trust_remote_code: bool = False      # Allow remote code execution
    
    # Model paths configuration
    model_paths: Optional[ModelPaths] = None
    
    def __post_init__(self):
        """Initialize model paths if not provided"""
        if self.model_paths is None:
            self.model_paths = ModelPaths()
        
        # Update local paths from model_paths if not explicitly set
        if self.local_blip_model_path is None and self.model_paths.blip_model_dir:
            if os.path.exists(self.model_paths.blip_model_dir):
                self.local_blip_model_path = self.model_paths.blip_model_dir
        
        if self.local_clip_model_path is None and self.model_paths.clip_model_dir:
            if os.path.exists(self.model_paths.clip_model_dir):
                self.local_clip_model_path = self.model_paths.clip_model_dir
        
        if self.local_sentence_transformer_path is None and self.model_paths.sentence_transformer_dir:
            if os.path.exists(self.model_paths.sentence_transformer_dir):
                self.local_sentence_transformer_path = self.model_paths.sentence_transformer_dir
        
        # Update cache_dir from model_paths if not set
        if self.cache_dir is None and self.model_paths.hf_cache_dir:
            self.cache_dir = self.model_paths.hf_cache_dir
    
    @classmethod
    def from_env(cls) -> 'ModelConfig':
        """Create ModelConfig from environment variables"""
        # Load model paths from environment
        model_paths = ModelPaths.from_env()
        
        return cls(
            blip_model_name=os.getenv('BLIP_MODEL_NAME', 'Salesforce/blip-image-captioning-base'),
            clip_model_name=os.getenv('CLIP_MODEL_NAME', 'openai/clip-vit-base-patch32'),
            sentence_transformer_model=os.getenv('SENTENCE_TRANSFORMER_MODEL', 'all-MiniLM-L6-v2'),
            device=os.getenv('DEVICE', 'cpu'),
            local_blip_model_path=os.getenv('LOCAL_BLIP_MODEL_PATH'),
            local_clip_model_path=os.getenv('LOCAL_CLIP_MODEL_PATH'),
            local_sentence_transformer_path=os.getenv('LOCAL_SENTENCE_TRANSFORMER_PATH'),
            cache_dir=os.getenv('CACHE_DIR'),
            use_local_files_only=os.getenv('USE_LOCAL_FILES_ONLY', 'false').lower() == 'true',
            trust_remote_code=os.getenv('TRUST_REMOTE_CODE', 'false').lower() == 'true',
            model_paths=model_paths
        )


@dataclass
class DatabaseConfig:
    db_path: str = "./image_vector_db"
    collection_name: str = "image_contexts"
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create DatabaseConfig from environment variables"""
        return cls(
            db_path=os.getenv('DB_PATH', './image_vector_db'),
            collection_name=os.getenv('COLLECTION_NAME', 'image_contexts')
        )


@dataclass
class ProcessingConfig:
    max_caption_length: int = 100
    num_beams: int = 5
    temperature: float = 0.7
    repetition_penalty: float = 1.2
    object_confidence_threshold: float = 0.1
    object_categories: List[str] = None
    supported_formats: List[str] = None

    def __post_init__(self):
        if self.object_categories is None:
            self.object_categories = [
                "person", "car", "dog", "cat", "tree", "building", "sky", "water",
                "food", "animal", "vehicle", "furniture", "electronics", "clothing"
            ]
        
        if self.supported_formats is None:
            self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']
    
    @classmethod
    def from_env(cls) -> 'ProcessingConfig':
        """Create ProcessingConfig from environment variables"""
        # Parse object categories from comma-separated string
        object_categories = None
        if os.getenv('OBJECT_CATEGORIES'):
            object_categories = [cat.strip() for cat in os.getenv('OBJECT_CATEGORIES').split(',')]
        
        # Parse supported formats from comma-separated string
        supported_formats = None
        if os.getenv('SUPPORTED_FORMATS'):
            supported_formats = [fmt.strip() for fmt in os.getenv('SUPPORTED_FORMATS').split(',')]
        
        return cls(
            max_caption_length=int(os.getenv('MAX_CAPTION_LENGTH', '100')),
            num_beams=int(os.getenv('NUM_BEAMS', '5')),
            temperature=float(os.getenv('TEMPERATURE', '0.7')),
            repetition_penalty=float(os.getenv('REPETITION_PENALTY', '1.2')),
            object_confidence_threshold=float(os.getenv('OBJECT_CONFIDENCE_THRESHOLD', '0.1')),
            object_categories=object_categories,
            supported_formats=supported_formats
        )


@dataclass
class Config:
    model: ModelConfig = None
    database: DatabaseConfig = None
    processing: ProcessingConfig = None

    def __post_init__(self):
        if self.model is None:
            self.model = ModelConfig()
        if self.database is None:
            self.database = DatabaseConfig()
        if self.processing is None:
            self.processing = ProcessingConfig()
    
    @classmethod
    def from_env(cls, env_file: str = '.env') -> 'Config':
        """Create Config from environment variables and .env file"""
        # Load .env file if it exists
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        return cls(
            model=ModelConfig.from_env(),
            database=DatabaseConfig.from_env(),
            processing=ProcessingConfig.from_env()
        )
    
    @classmethod
    def from_env_with_overrides(cls, env_file: str = '.env', **overrides) -> 'Config':
        """Create Config from environment with manual overrides"""
        config = cls.from_env(env_file)
        
        # Apply overrides
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                # Check if it's a nested attribute (e.g., model.device)
                if '.' in key:
                    obj_name, attr_name = key.split('.', 1)
                    if hasattr(config, obj_name):
                        obj = getattr(config, obj_name)
                        if hasattr(obj, attr_name):
                            setattr(obj, attr_name, value)
        
        return config


def get_config(env_file: str = '.env', **overrides) -> Config:
    """Convenience function to get configuration"""
    if overrides:
        return Config.from_env_with_overrides(env_file, **overrides)
    return Config.from_env(env_file)