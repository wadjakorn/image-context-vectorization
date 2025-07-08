#!/usr/bin/env python3
"""
Example usage of the Image Context Extractor
"""
import os
import logging
import sys

# Disable ChromaDB telemetry early to prevent capture() errors
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_CLIENT_DISABLE_TELEMETRY", "True")

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from image_context_extractor import ImageContextExtractor, Config
from image_context_extractor.utils.logging_utils import setup_logging


def main():
    # Setup logging
    setup_logging(level=logging.INFO)
    
    # Initialize with default config
    config = Config()
    extractor = ImageContextExtractor(config)
    
    print("Image Context Extractor - Example Usage")
    print("=" * 50)
    
    # Example 1: Process a single image
    print("\n1. Processing a single image:")
    image_path = "/Users/wadjakorntonsri/Downloads/google image search/fastfood.webp"  # Replace with actual path
    
    if os.path.exists(image_path):
        try:
            image_id = extractor.process_image(image_path)
            print(f"✓ Successfully processed image: {image_id}")
        except Exception as e:
            print(f"✗ Error processing image: {e}")
    else:
        print(f"✗ Image file not found: {image_path}")
    
    # Example 2: Process all images in a directory
    print("\n2. Processing directory:")
    image_directory = "/Users/wadjakorntonsri/Downloads/google image search/"  # Replace with actual directory
    
    if os.path.exists(image_directory):
        try:
            processed_ids = extractor.process_directory(image_directory)
            print(f"✓ Processed {len(processed_ids)} images")
        except Exception as e:
            print(f"✗ Error processing directory: {e}")
    else:
        print(f"✗ Directory not found: {image_directory}")
    
    # Example 3: Search for similar images
    print("\n3. Searching for similar images:")
    search_queries = [
        "people at a party",
        "nature landscape",
        "urban architecture",
        "animals in the wild"
    ]
    
    for query in search_queries:
        try:
            results = extractor.search_similar_images(query, n_results=3)
            print(f"\nQuery: '{query}'")
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['image_path']}")
                    print(f"     Caption: {result['caption']}")
                    print(f"     Distance: {result['distance']:.4f}")
            else:
                print("  No results found")
        except Exception as e:
            print(f"✗ Error searching for '{query}': {e}")
    
    # Example 4: Get database statistics
    print("\n4. Database statistics:")
    try:
        stats = extractor.get_stats()
        print(f"✓ Total images in database: {stats['total_images']}")
        print(f"✓ Collection name: {stats['collection_name']}")
        print(f"✓ Database path: {stats['db_path']}")
    except Exception as e:
        print(f"✗ Error getting stats: {e}")


if __name__ == "__main__":
    main()