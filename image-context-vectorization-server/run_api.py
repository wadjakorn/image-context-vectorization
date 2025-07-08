#!/usr/bin/env python3
"""
API server startup script for Image Context Extractor.
"""
import argparse
import os
import sys
from pathlib import Path

# Disable ChromaDB telemetry early to prevent capture() errors
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_CLIENT_DISABLE_TELEMETRY", "True")

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from image_context_extractor.api.app import run_server
from image_context_extractor.utils.logging_utils import setup_logging


def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(description="Image Context Extractor API Server")
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Log level (default: info)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=".env",
        help="Configuration file path (default: .env)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode (enables reload and debug logging)"
    )
    
    args = parser.parse_args()
    
    # Development mode overrides
    if args.dev:
        args.reload = True
        args.log_level = "debug"
    
    # Setup logging
    setup_logging()
    
    print("🚀 Starting Image Context Extractor API Server")
    print(f"📍 Server will be available at: http://{args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔧 Configuration file: {args.config}")
    print()
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"⚠️  Warning: Configuration file '{args.config}' not found.")
        print("   Using default configuration. Create a .env file for custom settings.")
        print()
    
    try:
        run_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()