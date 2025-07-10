#!/usr/bin/env python3
"""
Example usage with local models
"""
import os
import logging
from main import ImageContextExtractor, setup_logging
from src.image_context_extractor.config.settings import Config, ModelConfig, DatabaseConfig, ProcessingConfig
from model_utils import ModelDownloader


def example_with_local_models():
    """Example showing how to use local models"""
    
    # Setup logging
    setup_logging(level=logging.INFO)
    
    print("Local Models Example")
    print("=" * 50)
    
    # Step 1: Download models locally (optional)
    print("\n1. Setting up local models...")
    downloader = ModelDownloader("./models")
    
    # Check if models exist, download if needed
    model_info = downloader.get_model_info()
    print(f"Current models: {model_info['total_models']} models, {model_info['total_size_mb']:.2f} MB")
    
    if model_info['total_models'] == 0:
        print("No local models found. Downloading...")
        local_paths = downloader.download_all_default_models()
        print("Downloaded models:")
        for model_type, path in local_paths.items():
            print(f"  {model_type}: {path}")
    else:
        print("Using existing local models")
    
    # Step 2: Configure to use local models
    print("\n2. Configuring local model paths...")
    
    # Get the local model paths
    models_dir = "./models"
    
    # Create config with local model paths
    config = Config(
        model=ModelConfig(
            # Local model paths
            local_blip_model_path=os.path.join(models_dir, "blip", "Salesforce_blip-image-captioning-base"),
            local_clip_model_path=os.path.join(models_dir, "clip", "openai_clip-vit-base-patch32"),
            local_sentence_transformer_path=os.path.join(models_dir, "sentence_transformer", "all-MiniLM-L6-v2"),
            
            # Force use of local files only (no internet access)
            use_local_files_only=True,
            
            # Use GPU if available
            device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu",
            
            # Custom cache directory
            cache_dir="./model_cache"
        ),
        database=DatabaseConfig(
            db_path="./local_models_db"
        )
    )
    
    # Step 3: Initialize extractor with local models
    print("\n3. Initializing extractor with local models...")
    extractor = ImageContextExtractor(config)
    
    # Step 4: Test processing (replace with your image path)
    print("\n4. Testing image processing...")
    
    # Example image path - replace with your actual image
    test_image = "/Users/wadjakorntonsri/Downloads/google image search/fastfood.webp"
    
    if os.path.exists(test_image):
        try:
            # Process image
            image_id = extractor.process_image(test_image)
            print(f"✓ Successfully processed image: {image_id}")
            
            # Search for similar images
            results = extractor.search_similar_images("food", n_results=3)
            print(f"✓ Found {len(results)} similar images")
            
        except Exception as e:
            print(f"✗ Error processing image: {e}")
    else:
        print(f"✗ Test image not found: {test_image}")
    
    # Step 5: Show stats
    print("\n5. Database statistics:")
    stats = extractor.get_stats()
    print(f"✓ Total images in database: {stats['total_images']}")
    print(f"✓ Database path: {stats['db_path']}")


def example_offline_mode():
    """Example showing completely offline operation"""
    
    print("\n" + "="*50)
    print("Offline Mode Example")
    print("="*50)
    
    # Configure for completely offline operation
    config = Config(
        model=ModelConfig(
            # Use local models only
            local_blip_model_path="./models/blip/Salesforce_blip-image-captioning-base",
            local_clip_model_path="./models/clip/openai_clip-vit-base-patch32", 
            local_sentence_transformer_path="./models/sentence_transformer/all-MiniLM-L6-v2",
            
            # Force offline mode
            use_local_files_only=True,
            
            # Use custom cache
            cache_dir="./offline_cache"
        ),
        database=DatabaseConfig(
            db_path="./offline_db"
        )
    )
    
    try:
        print("Initializing in offline mode...")
        extractor = ImageContextExtractor(config)
        print("✓ Offline mode initialized successfully")
        
        # This would work completely offline
        print("✓ Ready for offline image processing")
        
    except Exception as e:
        print(f"✗ Offline mode failed: {e}")
        print("Make sure local models are downloaded first")


def example_mixed_mode():
    """Example showing mixed local/remote model usage"""
    
    print("\n" + "="*50) 
    print("Mixed Mode Example")
    print("="*50)
    
    # Use some local models, some remote
    config = Config(
        model=ModelConfig(
            # Use local BLIP model
            local_blip_model_path="./models/blip/Salesforce_blip-image-captioning-base",
            
            # Use remote CLIP model (will download if needed)
            clip_model_name="openai/clip-vit-base-patch32",
            
            # Use remote sentence transformer
            sentence_transformer_model="all-MiniLM-L6-v2",
            
            # Allow downloads but prefer local
            use_local_files_only=False,
            cache_dir="./mixed_cache"
        )
    )
    
    print("Mixed mode configuration created")
    print("- BLIP: Local model")
    print("- CLIP: Remote model") 
    print("- Sentence Transformer: Remote model")


if __name__ == "__main__":
    example_with_local_models()
    example_offline_mode()
    example_mixed_mode()