#!/usr/bin/env python3
"""
Model management utilities for downloading and managing local models
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ModelDownloader:
    """Utility class for downloading and managing models"""
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
    def download_model(self, model_name: str, model_type: str, cache_dir: Optional[str] = None) -> str:
        """Download a model to local storage
        
        Args:
            model_name: Name of the model (e.g., "Salesforce/blip-image-captioning-base")
            model_type: Type of model ("blip", "clip", "sentence_transformer")
            cache_dir: Optional cache directory
            
        Returns:
            Path to the downloaded model
        """
        safe_name = model_name.replace("/", "_").replace("\\", "_")
        local_path = self.models_dir / model_type / safe_name
        
        if local_path.exists():
            logger.info(f"Model already exists at: {local_path}")
            return str(local_path)
        
        logger.info(f"Downloading {model_type} model: {model_name}")
        local_path.mkdir(parents=True, exist_ok=True)
        
        kwargs = {}
        if cache_dir:
            kwargs['cache_dir'] = cache_dir
            
        try:
            if model_type == "blip":
                processor = BlipProcessor.from_pretrained(model_name, **kwargs)
                model = BlipForConditionalGeneration.from_pretrained(model_name, **kwargs)
                
                processor.save_pretrained(local_path)
                model.save_pretrained(local_path)
                
            elif model_type == "clip":
                processor = CLIPProcessor.from_pretrained(model_name, **kwargs)
                model = CLIPModel.from_pretrained(model_name, **kwargs)
                
                processor.save_pretrained(local_path)
                model.save_pretrained(local_path)
                
            elif model_type == "sentence_transformer":
                model = SentenceTransformer(model_name, cache_folder=cache_dir)
                model.save(str(local_path))
                
            else:
                raise ValueError(f"Unknown model type: {model_type}")
                
            logger.info(f"Model downloaded to: {local_path}")
            return str(local_path)
            
        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {e}")
            # Clean up partial download
            if local_path.exists():
                shutil.rmtree(local_path)
            raise
    
    def download_all_default_models(self, cache_dir: Optional[str] = None) -> Dict[str, str]:
        """Download all default models used by the application
        
        Returns:
            Dictionary mapping model types to their local paths
        """
        models = {
            "blip": "Salesforce/blip-image-captioning-base",
            "clip": "openai/clip-vit-base-patch32", 
            "sentence_transformer": "all-MiniLM-L6-v2"
        }
        
        local_paths = {}
        for model_type, model_name in models.items():
            try:
                local_path = self.download_model(model_name, model_type, cache_dir)
                local_paths[model_type] = local_path
            except Exception as e:
                logger.error(f"Failed to download {model_type} model: {e}")
                
        return local_paths
    
    def list_local_models(self) -> Dict[str, list]:
        """List all locally stored models"""
        local_models = {}
        
        if not self.models_dir.exists():
            return local_models
            
        for model_type_dir in self.models_dir.iterdir():
            if model_type_dir.is_dir():
                model_type = model_type_dir.name
                models = [d.name for d in model_type_dir.iterdir() if d.is_dir()]
                local_models[model_type] = models
                
        return local_models
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about local models"""
        local_models = self.list_local_models()
        total_size = self._calculate_total_size()
        
        return {
            "models_directory": str(self.models_dir),
            "local_models": local_models,
            "total_size_mb": total_size / (1024 * 1024),
            "total_models": sum(len(models) for models in local_models.values())
        }
    
    def _calculate_total_size(self) -> int:
        """Calculate total size of all models in bytes"""
        total_size = 0
        if self.models_dir.exists():
            for path in self.models_dir.rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
        return total_size
    
    def clean_cache(self, model_type: Optional[str] = None):
        """Remove downloaded models to free up space"""
        if model_type:
            model_dir = self.models_dir / model_type
            if model_dir.exists():
                shutil.rmtree(model_dir)
                logger.info(f"Cleaned {model_type} models")
        else:
            if self.models_dir.exists():
                shutil.rmtree(self.models_dir)
                logger.info("Cleaned all models")


def main():
    """CLI interface for model management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Model management utility")
    parser.add_argument("--download-all", action="store_true", 
                       help="Download all default models")
    parser.add_argument("--list", action="store_true",
                       help="List local models")
    parser.add_argument("--info", action="store_true",
                       help="Show model information")
    parser.add_argument("--clean", type=str, nargs="?", const="all",
                       help="Clean models (specify type or 'all')")
    parser.add_argument("--models-dir", type=str, default="./models",
                       help="Models directory")
    parser.add_argument("--cache-dir", type=str,
                       help="Cache directory")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    downloader = ModelDownloader(args.models_dir)
    
    if args.download_all:
        print("Downloading all default models...")
        paths = downloader.download_all_default_models(args.cache_dir)
        print("Downloaded models:")
        for model_type, path in paths.items():
            print(f"  {model_type}: {path}")
    
    elif args.list:
        models = downloader.list_local_models()
        print("Local models:")
        for model_type, model_list in models.items():
            print(f"  {model_type}: {model_list}")
    
    elif args.info:
        info = downloader.get_model_info()
        print(f"Models directory: {info['models_directory']}")
        print(f"Total models: {info['total_models']}")
        print(f"Total size: {info['total_size_mb']:.2f} MB")
        print("Local models:")
        for model_type, models in info['local_models'].items():
            print(f"  {model_type}: {len(models)} models")
    
    elif args.clean:
        if args.clean == "all":
            downloader.clean_cache()
            print("Cleaned all models")
        else:
            downloader.clean_cache(args.clean)
            print(f"Cleaned {args.clean} models")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()