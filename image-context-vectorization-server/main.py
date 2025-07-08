#!/usr/bin/env python3
"""
Main entry point for the Image Context Extractor application.
"""
import os
import logging
import sys

# Disable ChromaDB telemetry early to prevent capture() errors
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_CLIENT_DISABLE_TELEMETRY", "True")

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from image_context_extractor import ImageContextExtractor, Config, get_config
from image_context_extractor.utils.logging_utils import setup_logging


def main():
    """Main entry point"""
    # Load configuration from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    setup_logging(getattr(logging, log_level))
    
    # Load config from .env file
    config = get_config()
    extractor = ImageContextExtractor(config)
    
    # Example usage:
    # extractor.process_image("path/to/your/image.jpg")
    # extractor.process_directory("path/to/your/images/")
    # results = extractor.search_similar_images("people at a party", n_results=3)
    # stats = extractor.get_stats()
    
    print("Image Context Extractor initialized successfully!")
    print(f"Configuration loaded from environment")
    print(f"Database stats: {extractor.get_stats()}")


if __name__ == "__main__":
    main()