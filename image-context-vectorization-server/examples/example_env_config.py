#!/usr/bin/env python3
"""
Example usage with environment-based configuration
"""
import os
import logging
from main import ImageContextExtractor, setup_logging
from config import get_config, Config


def example_with_env_file():
    """Example using .env file configuration"""
    print("Environment Configuration Example")
    print("=" * 50)
    
    # Setup logging
    setup_logging(level=logging.INFO)
    
    print("\n1. Using .env file configuration...")
    
    # Create a sample .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("Creating sample .env file...")
        with open('.env', 'w') as f:
            f.write("""# Sample configuration
DEVICE=cpu
DB_PATH=./env_test_db
COLLECTION_NAME=env_test_collection
MAX_CAPTION_LENGTH=150
OBJECT_CONFIDENCE_THRESHOLD=0.15
LOG_LEVEL=INFO
""")
        print("✓ Created .env file")
    
    # Load configuration from .env file
    config = get_config()
    
    print(f"✓ Device: {config.model.device}")
    print(f"✓ Database path: {config.database.db_path}")
    print(f"✓ Collection: {config.database.collection_name}")
    print(f"✓ Max caption length: {config.processing.max_caption_length}")
    print(f"✓ Object threshold: {config.processing.object_confidence_threshold}")
    
    # Initialize extractor
    extractor = ImageContextExtractor(config)
    print("✓ Extractor initialized with .env config")


def example_with_env_variables():
    """Example using environment variables directly"""
    print("\n" + "=" * 50)
    print("Environment Variables Example")
    print("=" * 50)
    
    # Set environment variables programmatically
    os.environ['DEVICE'] = 'cpu'
    os.environ['DB_PATH'] = './env_vars_db'
    os.environ['COLLECTION_NAME'] = 'env_vars_collection'
    os.environ['USE_LOCAL_FILES_ONLY'] = 'false'
    os.environ['CACHE_DIR'] = './env_cache'
    
    # Load configuration from environment
    config = Config.from_env()
    
    print(f"✓ Device: {config.model.device}")
    print(f"✓ Database path: {config.database.db_path}")
    print(f"✓ Use local files only: {config.model.use_local_files_only}")
    print(f"✓ Cache dir: {config.model.cache_dir}")


def example_with_overrides():
    """Example using environment config with overrides"""
    print("\n" + "=" * 50)
    print("Environment Config with Overrides Example")
    print("=" * 50)
    
    # Load config from .env but override specific values
    config = get_config(
        **{
            'model.device': 'cuda' if os.environ.get('CUDA_VISIBLE_DEVICES') else 'cpu',
            'database.db_path': './override_db',
            'processing.max_caption_length': 200
        }
    )
    
    print(f"✓ Device (overridden): {config.model.device}")
    print(f"✓ Database path (overridden): {config.database.db_path}")
    print(f"✓ Max caption length (overridden): {config.processing.max_caption_length}")


def example_local_models_env():
    """Example configuring local models via environment"""
    print("\n" + "=" * 50)
    print("Local Models via Environment Example")
    print("=" * 50)
    
    # Create .env file with local model configuration
    env_content = """
# Local models configuration
LOCAL_BLIP_MODEL_PATH=./models/blip/Salesforce_blip-image-captioning-base
LOCAL_CLIP_MODEL_PATH=./models/clip/openai_clip-vit-base-patch32
LOCAL_SENTENCE_TRANSFORMER_PATH=./models/sentence_transformer/all-MiniLM-L6-v2
USE_LOCAL_FILES_ONLY=true
CACHE_DIR=./local_models_cache

# Database for local models
DB_PATH=./local_models_db
COLLECTION_NAME=local_models_collection

# Processing settings
OBJECT_CONFIDENCE_THRESHOLD=0.12
SUPPORTED_FORMATS=.png,.jpg,.jpeg,.webp
"""
    
    with open('.env.local', 'w') as f:
        f.write(env_content)
    
    # Load config from custom env file
    config = get_config('.env.local')
    
    print(f"✓ Local BLIP path: {config.model.local_blip_model_path}")
    print(f"✓ Local CLIP path: {config.model.local_clip_model_path}")
    print(f"✓ Local ST path: {config.model.local_sentence_transformer_path}")
    print(f"✓ Use local files only: {config.model.use_local_files_only}")
    print(f"✓ Supported formats: {config.processing.supported_formats}")


def example_production_vs_development():
    """Example showing different configs for different environments"""
    print("\n" + "=" * 50)
    print("Production vs Development Configuration")
    print("=" * 50)
    
    # Development configuration
    dev_env = """
# Development settings
DEVICE=cpu
DB_PATH=./dev_db
LOG_LEVEL=DEBUG
USE_LOCAL_FILES_ONLY=false
OBJECT_CONFIDENCE_THRESHOLD=0.1
"""
    
    # Production configuration
    prod_env = """
# Production settings
DEVICE=cuda
DB_PATH=/app/data/prod_db
LOG_LEVEL=INFO
USE_LOCAL_FILES_ONLY=true
LOCAL_BLIP_MODEL_PATH=/app/models/blip/model
LOCAL_CLIP_MODEL_PATH=/app/models/clip/model
LOCAL_SENTENCE_TRANSFORMER_PATH=/app/models/sentence_transformer/model
CACHE_DIR=/app/cache
OBJECT_CONFIDENCE_THRESHOLD=0.15
"""
    
    # Write environment files
    with open('.env.development', 'w') as f:
        f.write(dev_env)
    
    with open('.env.production', 'w') as f:
        f.write(prod_env)
    
    # Load different configs
    dev_config = get_config('.env.development')
    prod_config = get_config('.env.production')
    
    print("Development config:")
    print(f"  Device: {dev_config.model.device}")
    print(f"  DB path: {dev_config.database.db_path}")
    print(f"  Use local files: {dev_config.model.use_local_files_only}")
    
    print("\nProduction config:")
    print(f"  Device: {prod_config.model.device}")
    print(f"  DB path: {prod_config.database.db_path}")
    print(f"  Use local files: {prod_config.model.use_local_files_only}")
    print(f"  Local BLIP: {prod_config.model.local_blip_model_path}")


def example_config_validation():
    """Example showing config validation and error handling"""
    print("\n" + "=" * 50)
    print("Configuration Validation Example")
    print("=" * 50)
    
    try:
        # Test with invalid device
        config = get_config(**{'model.device': 'invalid_device'})
        print("⚠️  Warning: No device validation implemented")
        
        # Test with missing directory
        config = get_config(**{'database.db_path': '/nonexistent/path'})
        print("⚠️  Warning: No path validation implemented")
        
        print("✓ Config loaded (validation could be improved)")
        
    except Exception as e:
        print(f"✗ Config validation error: {e}")


if __name__ == "__main__":
    example_with_env_file()
    example_with_env_variables()
    example_with_overrides()
    example_local_models_env()
    example_production_vs_development()
    example_config_validation()
    
    print("\n" + "=" * 50)
    print("✓ All environment configuration examples completed!")
    print("Check the generated .env files for reference.")