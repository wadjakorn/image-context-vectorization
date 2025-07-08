#!/usr/bin/env python3
"""
Model paths configuration and management
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any
import logging


@dataclass
class ModelPaths:
    """Configuration for model file paths"""
    
    # Base directories
    models_base_dir: str = "./models"
    cache_base_dir: str = "./model_cache"
    
    # BLIP model paths
    blip_model_dir: Optional[str] = None
    blip_processor_path: Optional[str] = None
    blip_model_path: Optional[str] = None
    
    # CLIP model paths
    clip_model_dir: Optional[str] = None
    clip_processor_path: Optional[str] = None
    clip_model_path: Optional[str] = None
    
    # Sentence Transformer paths
    sentence_transformer_dir: Optional[str] = None
    sentence_transformer_model_path: Optional[str] = None
    
    # HuggingFace cache paths
    hf_cache_dir: Optional[str] = None
    transformers_cache: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default paths if not provided"""
        base_dir = Path(self.models_base_dir)
        
        if self.blip_model_dir is None:
            self.blip_model_dir = str(base_dir / "blip" / "Salesforce_blip-image-captioning-base")
        
        if self.clip_model_dir is None:
            self.clip_model_dir = str(base_dir / "clip" / "openai_clip-vit-base-patch32")
        
        if self.sentence_transformer_dir is None:
            self.sentence_transformer_dir = str(base_dir / "sentence_transformer" / "all-MiniLM-L6-v2")
        
        if self.hf_cache_dir is None:
            self.hf_cache_dir = str(Path(self.cache_base_dir) / "huggingface")
        
        if self.transformers_cache is None:
            self.transformers_cache = str(Path(self.cache_base_dir) / "transformers")
    
    def get_blip_paths(self) -> Dict[str, str]:
        """Get BLIP model paths"""
        return {
            "model_dir": self.blip_model_dir,
            "processor": self.blip_processor_path or os.path.join(self.blip_model_dir, "processor"),
            "model": self.blip_model_path or os.path.join(self.blip_model_dir, "model")
        }
    
    def get_clip_paths(self) -> Dict[str, str]:
        """Get CLIP model paths"""
        return {
            "model_dir": self.clip_model_dir,
            "processor": self.clip_processor_path or os.path.join(self.clip_model_dir, "processor"),
            "model": self.clip_model_path or os.path.join(self.clip_model_dir, "model")
        }
    
    def get_sentence_transformer_paths(self) -> Dict[str, str]:
        """Get Sentence Transformer paths"""
        return {
            "model_dir": self.sentence_transformer_dir,
            "model": self.sentence_transformer_model_path or self.sentence_transformer_dir
        }
    
    def get_cache_paths(self) -> Dict[str, str]:
        """Get cache directory paths"""
        return {
            "hf_cache": self.hf_cache_dir,
            "transformers_cache": self.transformers_cache,
            "base_cache": self.cache_base_dir
        }
    
    def create_directories(self):
        """Create all necessary directories"""
        paths_to_create = [
            self.models_base_dir,
            self.cache_base_dir,
            self.blip_model_dir,
            self.clip_model_dir,
            self.sentence_transformer_dir,
            self.hf_cache_dir,
            self.transformers_cache
        ]
        
        for path in paths_to_create:
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)
    
    def validate_paths(self) -> Dict[str, bool]:
        """Validate that model paths exist"""
        validation = {}
        
        # Check model directories
        validation["blip_exists"] = os.path.exists(self.blip_model_dir) if self.blip_model_dir else False
        validation["clip_exists"] = os.path.exists(self.clip_model_dir) if self.clip_model_dir else False
        validation["sentence_transformer_exists"] = os.path.exists(self.sentence_transformer_dir) if self.sentence_transformer_dir else False
        
        # Check cache directories
        validation["cache_base_exists"] = os.path.exists(self.cache_base_dir)
        validation["hf_cache_exists"] = os.path.exists(self.hf_cache_dir) if self.hf_cache_dir else False
        
        return validation
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about models and their sizes"""
        info = {
            "paths": asdict(self),
            "validation": self.validate_paths(),
            "sizes": {}
        }
        
        # Calculate sizes
        for model_type, model_dir in [
            ("blip", self.blip_model_dir),
            ("clip", self.clip_model_dir),
            ("sentence_transformer", self.sentence_transformer_dir)
        ]:
            if model_dir and os.path.exists(model_dir):
                size = self._calculate_directory_size(model_dir)
                info["sizes"][model_type] = {
                    "bytes": size,
                    "mb": round(size / (1024 * 1024), 2),
                    "gb": round(size / (1024 * 1024 * 1024), 3)
                }
            else:
                info["sizes"][model_type] = {"bytes": 0, "mb": 0, "gb": 0}
        
        return info
    
    def _calculate_directory_size(self, directory: str) -> int:
        """Calculate total size of a directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def save_config(self, config_path: str = "model_paths.json"):
        """Save model paths configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load_config(cls, config_path: str = "model_paths.json") -> 'ModelPaths':
        """Load model paths configuration from JSON file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    @classmethod
    def from_env(cls) -> 'ModelPaths':
        """Create ModelPaths from environment variables"""
        return cls(
            models_base_dir=os.getenv('MODELS_BASE_DIR', './models'),
            cache_base_dir=os.getenv('CACHE_BASE_DIR', './model_cache'),
            
            blip_model_dir=os.getenv('BLIP_MODEL_DIR'),
            blip_processor_path=os.getenv('BLIP_PROCESSOR_PATH'),
            blip_model_path=os.getenv('BLIP_MODEL_PATH'),
            
            clip_model_dir=os.getenv('CLIP_MODEL_DIR'),
            clip_processor_path=os.getenv('CLIP_PROCESSOR_PATH'),
            clip_model_path=os.getenv('CLIP_MODEL_PATH'),
            
            sentence_transformer_dir=os.getenv('SENTENCE_TRANSFORMER_DIR'),
            sentence_transformer_model_path=os.getenv('SENTENCE_TRANSFORMER_MODEL_PATH'),
            
            hf_cache_dir=os.getenv('HF_CACHE_DIR'),
            transformers_cache=os.getenv('TRANSFORMERS_CACHE')
        )


class ModelPathsManager:
    """Manager for model paths operations"""
    
    def __init__(self, model_paths: ModelPaths = None):
        self.model_paths = model_paths or ModelPaths()
        self.logger = logging.getLogger(__name__)
    
    def setup_environment_variables(self):
        """Set up environment variables for HuggingFace and other libraries"""
        cache_paths = self.model_paths.get_cache_paths()
        
        # Set HuggingFace cache directories
        if cache_paths["hf_cache"]:
            os.environ['HF_HOME'] = cache_paths["hf_cache"]
            os.environ['HUGGINGFACE_HUB_CACHE'] = cache_paths["hf_cache"]
        
        if cache_paths["transformers_cache"]:
            os.environ['TRANSFORMERS_CACHE'] = cache_paths["transformers_cache"]
        
        self.logger.info("Environment variables set for model caching")
    
    def create_model_structure(self):
        """Create the complete model directory structure"""
        self.model_paths.create_directories()
        
        # Create additional subdirectories for better organization
        subdirs = [
            "blip/processors",
            "blip/models", 
            "clip/processors",
            "clip/models",
            "sentence_transformer/models",
            "temp",
            "downloads"
        ]
        
        base_dir = Path(self.model_paths.models_base_dir)
        for subdir in subdirs:
            (base_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Model directory structure created at {self.model_paths.models_base_dir}")
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all models"""
        return self.model_paths.get_model_info()
    
    def cleanup_cache(self, older_than_days: int = 30):
        """Clean up old cache files"""
        import time
        
        cache_dirs = [
            self.model_paths.hf_cache_dir,
            self.model_paths.transformers_cache,
            os.path.join(self.model_paths.cache_base_dir, "temp")
        ]
        
        cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
        cleaned_files = 0
        
        for cache_dir in cache_dirs:
            if cache_dir and os.path.exists(cache_dir):
                for root, dirs, files in os.walk(cache_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.getctime(file_path) < cutoff_time:
                            try:
                                os.remove(file_path)
                                cleaned_files += 1
                            except OSError:
                                pass
        
        self.logger.info(f"Cleaned {cleaned_files} old cache files")
        return cleaned_files


def get_default_model_paths() -> ModelPaths:
    """Get default model paths configuration"""
    return ModelPaths()


def get_model_paths_from_env() -> ModelPaths:
    """Get model paths from environment variables"""
    return ModelPaths.from_env()


def main():
    """CLI interface for model paths management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Model paths management")
    parser.add_argument("--init", action="store_true", help="Initialize model directory structure")
    parser.add_argument("--status", action="store_true", help="Show model status")
    parser.add_argument("--save-config", type=str, help="Save config to file")
    parser.add_argument("--load-config", type=str, help="Load config from file")
    parser.add_argument("--cleanup", type=int, nargs="?", const=30, help="Clean up cache (days old)")
    parser.add_argument("--env", action="store_true", help="Use environment variables")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Load model paths
    if args.load_config:
        model_paths = ModelPaths.load_config(args.load_config)
    elif args.env:
        model_paths = ModelPaths.from_env()
    else:
        model_paths = ModelPaths()
    
    manager = ModelPathsManager(model_paths)
    
    if args.init:
        manager.create_model_structure()
        manager.setup_environment_variables()
        print("✓ Model directory structure initialized")
    
    if args.status:
        status = manager.get_model_status()
        print("Model Paths Status:")
        print(f"Base directory: {status['paths']['models_base_dir']}")
        print(f"Cache directory: {status['paths']['cache_base_dir']}")
        print("\nModel existence:")
        for model, exists in status['validation'].items():
            print(f"  {model}: {'✓' if exists else '✗'}")
        print("\nModel sizes:")
        for model, size_info in status['sizes'].items():
            print(f"  {model}: {size_info['mb']} MB")
    
    if args.save_config:
        model_paths.save_config(args.save_config)
        print(f"✓ Configuration saved to {args.save_config}")
    
    if args.cleanup is not None:
        cleaned = manager.cleanup_cache(args.cleanup)
        print(f"✓ Cleaned {cleaned} cache files older than {args.cleanup} days")


if __name__ == "__main__":
    main()