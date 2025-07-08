#!/usr/bin/env python3
"""
Command-line interface for Image Context Extractor
"""
import argparse
import logging
import os
import sys
from pathlib import Path

# Disable ChromaDB telemetry early to prevent capture() errors
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_CLIENT_DISABLE_TELEMETRY", "True")

from .core.extractor import ImageContextExtractor
from .config.settings import get_config
from .utils.logging_utils import setup_logging


def setup_cli_parser():
    """Setup command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Image Context Extractor - Extract contextual information from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single image
  %(prog)s process-image image.jpg
  
  # Process a directory of images
  %(prog)s process-directory ./images/
  
  # Search for similar images
  %(prog)s search "people at a party" --results 5
  
  # Show database statistics
  %(prog)s stats
  
  # Initialize model directory structure
  %(prog)s init-models
        """
    )
    
    # Global options
    parser.add_argument("--config", type=str, default=".env",
                       help="Configuration file path (default: .env)")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="Logging level")
    parser.add_argument("--log-file", type=str,
                       help="Log file path (default: image_context_extraction.log)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process single image
    process_image_parser = subparsers.add_parser("process-image", help="Process a single image")
    process_image_parser.add_argument("image_path", help="Path to the image file")
    process_image_parser.add_argument("--force", action="store_true",
                                    help="Force reprocessing even if already processed")
    
    # Process directory
    process_dir_parser = subparsers.add_parser("process-directory", help="Process all images in a directory")
    process_dir_parser.add_argument("directory_path", help="Path to the directory containing images")
    process_dir_parser.add_argument("--force", action="store_true",
                                   help="Force reprocessing even if already processed")
    
    # Search similar images
    search_parser = subparsers.add_parser("search", help="Search for similar images")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--results", "-n", type=int, default=5,
                              help="Number of results to return (default: 5)")
    
    # Show statistics
    subparsers.add_parser("stats", help="Show database statistics")
    
    # List processed images
    subparsers.add_parser("list", help="List all processed images")
    
    # Initialize models
    init_parser = subparsers.add_parser("init-models", help="Initialize model directory structure")
    init_parser.add_argument("--download", action="store_true",
                           help="Also download default models")
    
    # Start API server
    server_parser = subparsers.add_parser("serve", help="Start the API server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    server_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    server_parser.add_argument("--dev", action="store_true", help="Development mode")
    
    # Test model loading
    test_parser = subparsers.add_parser("test-models", help="Test model loading and show timing")
    test_parser.add_argument("--preload", action="store_true", help="Preload all models")
    test_parser.add_argument("--device", choices=["cpu", "cuda", "auto"], help="Override device for testing")
    
    return parser


def cmd_process_image(args, extractor):
    """Process a single image"""
    if not os.path.exists(args.image_path):
        print(f"Error: Image file not found: {args.image_path}")
        return 1
    
    try:
        image_id = extractor.process_image(args.image_path, force_reprocess=args.force)
        print(f"✓ Successfully processed image: {image_id}")
        return 0
    except Exception as e:
        print(f"✗ Error processing image: {e}")
        return 1


def cmd_process_directory(args, extractor):
    """Process a directory of images"""
    if not os.path.exists(args.directory_path):
        print(f"Error: Directory not found: {args.directory_path}")
        return 1
    
    try:
        result = extractor.process_directory(args.directory_path, force_reprocess=args.force)
        print(f"✓ Processing complete:")
        print(f"  Total files: {result['total_files']}")
        print(f"  Processed: {result['processed']}")
        print(f"  Skipped: {result['skipped']}")
        print(f"  Failed: {result['failed']}")
        return 0
    except Exception as e:
        print(f"✗ Error processing directory: {e}")
        return 1


def cmd_search(args, extractor):
    """Search for similar images"""
    try:
        results = extractor.search_similar_images(args.query, n_results=args.results)
        
        if not results:
            print(f"No results found for query: '{args.query}'")
            return 0
        
        print(f"Found {len(results)} similar images for query: '{args.query}'")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['image_path']}")
            print(f"   Caption: {result['caption']}")
            print(f"   Distance: {result['distance']:.4f}")
            print(f"   Objects: {', '.join(result['objects'])}")
            print()
        
        return 0
    except Exception as e:
        print(f"✗ Error searching: {e}")
        return 1


def cmd_stats(args, extractor):
    """Show database statistics"""
    try:
        stats = extractor.get_stats()
        print("Database Statistics:")
        print(f"  Total images: {stats['total_images']}")
        print(f"  Collection name: {stats['collection_name']}")
        print(f"  Database path: {stats['db_path']}")
        return 0
    except Exception as e:
        print(f"✗ Error getting stats: {e}")
        return 1


def cmd_list(args, extractor):
    """List all processed images"""
    try:
        images = extractor.get_processed_images()
        
        if not images:
            print("No images have been processed yet.")
            return 0
        
        print(f"Processed images ({len(images)}):")
        for image_path in images:
            status = "✓" if os.path.exists(image_path) else "✗ (missing)"
            print(f"  {status} {image_path}")
        
        return 0
    except Exception as e:
        print(f"✗ Error listing images: {e}")
        return 1


def cmd_init_models(args, extractor):
    """Initialize model directory structure"""
    try:
        from .config.model_paths import ModelPathsManager
        
        manager = ModelPathsManager(extractor.config.model.model_paths)
        manager.create_model_structure()
        manager.setup_environment_variables()
        
        print("✓ Model directory structure initialized")
        
        if args.download:
            print("Downloading default models...")
            # Import here to avoid circular imports
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
            from model_utils import ModelDownloader
            
            downloader = ModelDownloader(extractor.config.model.model_paths.models_base_dir)
            paths = downloader.download_all_default_models()
            
            print("✓ Downloaded models:")
            for model_type, path in paths.items():
                print(f"  {model_type}: {path}")
        
        return 0
    except Exception as e:
        print(f"✗ Error initializing models: {e}")
        return 1


def cmd_serve(args, extractor):
    """Start the API server"""
    try:
        from .api.app import run_server
        
        print("🚀 Starting Image Context Extractor API Server")
        print(f"📍 Server will be available at: http://{args.host}:{args.port}")
        print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
        print()
        
        if args.dev:
            args.reload = True
        
        run_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="debug" if args.dev else "info"
        )
        
        return 0
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        return 1


def cmd_test_models(args, extractor):
    """Test model loading times."""
    try:
        print("🧪 Testing model loading...")
        
        if args.device:
            print(f"📱 Using device: {args.device}")
            # Override device in config
            extractor.config.model.device = args.device
        
        print(f"📱 Current device: {extractor.config.model.device}")
        print()
        
        if args.preload:
            print("🚀 Preloading all models...")
            timings = extractor.model_manager.preload_all_models()
            
            print("\n📊 Model Loading Times:")
            print("-" * 40)
            for model_name, load_time in timings.items():
                if load_time is not None and model_name != 'total':
                    print(f"{model_name:20}: {load_time:6.2f}s")
            print("-" * 40)
            print(f"{'Total':20}: {timings['total']:6.2f}s")
        else:
            print("📋 Checking model status (without loading)...")
            status = extractor.model_manager.get_model_status()
            
            print("\n📊 Model Status:")
            print("-" * 40)
            for model_name, loaded in status.items():
                status_icon = "✅" if loaded else "⏳"
                print(f"{status_icon} {model_name:20}: {'Loaded' if loaded else 'Not loaded'}")
            
            print("\n💡 Use --preload to load all models and see timing")
        
        return 0
    except Exception as e:
        print(f"✗ Error testing models: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = setup_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_logging(level=log_level, log_file=args.log_file)
    
    try:
        # Load configuration
        config = get_config(args.config)
        extractor = ImageContextExtractor(config)
        
        # Execute command
        command_map = {
            "process-image": cmd_process_image,
            "process-directory": cmd_process_directory,
            "search": cmd_search,
            "stats": cmd_stats,
            "list": cmd_list,
            "init-models": cmd_init_models,
            "serve": cmd_serve,
            "test-models": cmd_test_models,
        }
        
        if args.command in command_map:
            return command_map[args.command](args, extractor)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())