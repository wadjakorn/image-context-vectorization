#!/usr/bin/env python3
"""
Example usage of model paths configuration
"""
import os
import logging
from main import ImageContextExtractor, setup_logging
from config import Config, ModelConfig
from model_paths import ModelPaths, ModelPathsManager


def example_basic_model_paths():
    """Basic model paths configuration"""
    print("Basic Model Paths Configuration")
    print("=" * 50)
    
    # Create model paths configuration
    model_paths = ModelPaths(
        models_base_dir="./my_models",
        cache_base_dir="./my_cache"
    )
    
    print(f"✓ Models base directory: {model_paths.models_base_dir}")
    print(f"✓ Cache base directory: {model_paths.cache_base_dir}")
    print(f"✓ BLIP model directory: {model_paths.blip_model_dir}")
    print(f"✓ CLIP model directory: {model_paths.clip_model_dir}")
    print(f"✓ Sentence Transformer directory: {model_paths.sentence_transformer_dir}")


def example_custom_model_paths():
    """Custom model paths configuration"""
    print("\n" + "=" * 50)
    print("Custom Model Paths Configuration")
    print("=" * 50)
    
    # Create custom model paths
    model_paths = ModelPaths(
        models_base_dir="/custom/models",
        cache_base_dir="/custom/cache",
        blip_model_dir="/custom/models/blip/custom_blip",
        clip_model_dir="/custom/models/clip/custom_clip",
        sentence_transformer_dir="/custom/models/st/custom_st",
        hf_cache_dir="/custom/cache/hf",
        transformers_cache="/custom/cache/transformers"
    )
    
    # Show all paths
    print("BLIP paths:")
    blip_paths = model_paths.get_blip_paths()
    for key, path in blip_paths.items():
        print(f"  {key}: {path}")
    
    print("\nCLIP paths:")
    clip_paths = model_paths.get_clip_paths()
    for key, path in clip_paths.items():
        print(f"  {key}: {path}")
    
    print("\nSentence Transformer paths:")
    st_paths = model_paths.get_sentence_transformer_paths()
    for key, path in st_paths.items():
        print(f"  {key}: {path}")
    
    print("\nCache paths:")
    cache_paths = model_paths.get_cache_paths()
    for key, path in cache_paths.items():
        print(f"  {key}: {path}")


def example_model_paths_manager():
    """Using ModelPathsManager for operations"""
    print("\n" + "=" * 50)
    print("Model Paths Manager Example")
    print("=" * 50)
    
    # Setup logging
    setup_logging(level=logging.INFO)
    
    # Create model paths and manager
    model_paths = ModelPaths()
    manager = ModelPathsManager(model_paths)
    
    # Create directory structure
    print("Creating model directory structure...")
    manager.create_model_structure()
    
    # Setup environment variables for HuggingFace
    print("Setting up environment variables...")
    manager.setup_environment_variables()
    
    # Get model status
    print("\nModel status:")
    status = manager.get_model_status()
    
    print(f"Base directory: {status['paths']['models_base_dir']}")
    print("Model validation:")
    for model, exists in status['validation'].items():
        print(f"  {model}: {'✓ Exists' if exists else '✗ Missing'}")
    
    print("Model sizes:")
    for model, size_info in status['sizes'].items():
        if size_info['mb'] > 0:
            print(f"  {model}: {size_info['mb']} MB")
        else:
            print(f"  {model}: Not downloaded")


def example_env_model_paths():
    """Model paths from environment variables"""
    print("\n" + "=" * 50)
    print("Environment Model Paths Example")
    print("=" * 50)
    
    # Set environment variables
    os.environ['MODELS_BASE_DIR'] = './env_models'
    os.environ['CACHE_BASE_DIR'] = './env_cache'
    os.environ['BLIP_MODEL_DIR'] = './env_models/custom_blip'
    os.environ['HF_CACHE_DIR'] = './env_cache/hf_custom'
    
    # Load from environment
    model_paths = ModelPaths.from_env()
    
    print(f"✓ Models base (from env): {model_paths.models_base_dir}")
    print(f"✓ Cache base (from env): {model_paths.cache_base_dir}")
    print(f"✓ BLIP model dir (from env): {model_paths.blip_model_dir}")
    print(f"✓ HF cache (from env): {model_paths.hf_cache_dir}")


def example_config_integration():
    """Integration with main Config class"""
    print("\n" + "=" * 50)
    print("Config Integration Example")
    print("=" * 50)
    
    # Create model paths
    model_paths = ModelPaths(
        models_base_dir="./integration_models",
        cache_base_dir="./integration_cache"
    )
    
    # Create config with model paths
    config = Config(
        model=ModelConfig(
            device="cpu",
            model_paths=model_paths,
            use_local_files_only=True
        )
    )
    
    print(f"✓ Model config device: {config.model.device}")
    print(f"✓ Model paths base dir: {config.model.model_paths.models_base_dir}")
    print(f"✓ Local BLIP path: {config.model.local_blip_model_path}")
    print(f"✓ Local CLIP path: {config.model.local_clip_model_path}")
    print(f"✓ Cache directory: {config.model.cache_dir}")


def example_save_load_config():
    """Save and load model paths configuration"""
    print("\n" + "=" * 50)
    print("Save/Load Configuration Example")
    print("=" * 50)
    
    # Create model paths configuration
    model_paths = ModelPaths(
        models_base_dir="./saved_models",
        cache_base_dir="./saved_cache",
        blip_model_dir="./saved_models/blip/custom",
        clip_model_dir="./saved_models/clip/custom"
    )
    
    # Save configuration
    config_file = "my_model_paths.json"
    model_paths.save_config(config_file)
    print(f"✓ Configuration saved to {config_file}")
    
    # Load configuration
    loaded_paths = ModelPaths.load_config(config_file)
    print(f"✓ Configuration loaded from {config_file}")
    print(f"✓ Loaded models base dir: {loaded_paths.models_base_dir}")
    print(f"✓ Loaded BLIP dir: {loaded_paths.blip_model_dir}")
    
    # Clean up
    if os.path.exists(config_file):
        os.remove(config_file)


def example_production_setup():
    """Production-ready model paths setup"""
    print("\n" + "=" * 50)
    print("Production Setup Example")
    print("=" * 50)
    
    # Production model paths configuration
    model_paths = ModelPaths(
        models_base_dir="/app/models",
        cache_base_dir="/app/cache",
        blip_model_dir="/app/models/blip/production",
        clip_model_dir="/app/models/clip/production",
        sentence_transformer_dir="/app/models/sentence_transformer/production",
        hf_cache_dir="/app/cache/huggingface",
        transformers_cache="/app/cache/transformers"
    )
    
    # Create manager
    manager = ModelPathsManager(model_paths)
    
    # Production setup
    print("Production model paths:")
    print(f"  Models: {model_paths.models_base_dir}")
    print(f"  Cache: {model_paths.cache_base_dir}")
    print(f"  BLIP: {model_paths.blip_model_dir}")
    print(f"  CLIP: {model_paths.clip_model_dir}")
    print(f"  Sentence Transformer: {model_paths.sentence_transformer_dir}")
    
    # Validation
    validation = model_paths.validate_paths()
    print(f"\nValidation results:")
    for check, result in validation.items():
        print(f"  {check}: {'✓' if result else '✗'}")
    
    # Model info
    info = model_paths.get_model_info()
    total_size = sum(size['mb'] for size in info['sizes'].values())
    print(f"\nTotal model size: {total_size:.2f} MB")


if __name__ == "__main__":
    example_basic_model_paths()
    example_custom_model_paths()
    example_model_paths_manager()
    example_env_model_paths()
    example_config_integration()
    example_save_load_config()
    example_production_setup()
    
    print("\n" + "=" * 50)
    print("✓ All model paths examples completed!")
    print("\nTo manage model paths via CLI:")
    print("  python model_paths.py --init     # Initialize structure")
    print("  python model_paths.py --status   # Show status")
    print("  python model_paths.py --cleanup  # Clean cache")