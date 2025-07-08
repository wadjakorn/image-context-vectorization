# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Image Context Extraction & Vectorization** system that extracts contextual information from images using AI models (BLIP, CLIP, SentenceTransformers) and stores them in a ChromaDB vector database for semantic similarity search. The system provides multiple interfaces: CLI, REST API, and direct Python API.

## Development Commands

### Installation & Setup
```bash
# Development installation (recommended)
pip install -e .

# Alternative installation
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"

# Setup configuration
cp .env.example .env  # Edit with your settings
```

### Common Development Tasks
```bash
# Start API server (development mode)
python run_api.py --dev
# or
./start_api.sh

# Start API server (production)
python run_api.py --host 0.0.0.0 --port 8000

# CLI operations
image-context-extractor process-image image.jpg
image-context-extractor process-directory ./images/
image-context-extractor search "people at a party" --results 5
image-context-extractor stats

# Test model loading performance
image-context-extractor test-models --preload

# Download models locally
python scripts/model_utils.py --download-all
image-context-extractor init-models --download

# Run examples
python examples/example_usage.py
python examples/api_examples.py
```

### Development Tools (if dev dependencies installed)
```bash
# Code formatting
black src/

# Linting
flake8 src/

# Type checking
mypy src/

# Testing
pytest tests/
```

## Architecture Overview

### Core Processing Pipeline
```
Image → BLIP (caption) → CLIP (objects/features) → SentenceTransformer (embeddings) → ChromaDB (storage)
```

### Key Components Structure

**Configuration Layer**: Environment-driven configuration management
- `src/image_context_extractor/config/settings.py`: Main config with `.env` support
- `src/image_context_extractor/config/model_paths.py`: Model storage management

**Core Processing Engine**: Main orchestration and business logic
- `src/image_context_extractor/core/extractor.py`: **Primary orchestrator class** - coordinates all operations
- `src/image_context_extractor/core/image_processor.py`: Image validation and metadata extraction

**AI Models Layer**: Manages multiple AI models with lazy loading
- `src/image_context_extractor/models/model_manager.py`: **Critical component** - handles BLIP, CLIP, and SentenceTransformer models
- Models load on-demand and stay in memory for performance

**Vector Database**: ChromaDB integration for semantic search
- `src/image_context_extractor/database/vector_db.py`: Vector storage and similarity search operations

**API Layer**: FastAPI REST API with real-time capabilities
- `src/image_context_extractor/api/app.py`: FastAPI application setup
- `src/image_context_extractor/api/routes/`: Route handlers for different endpoints
- **Unified endpoint**: `GET /api/v1/images/` handles both listing and search (with optional `query` and `objects` parameters)

**CLI Interface**: Comprehensive command-line tool
- `src/image_context_extractor/cli.py`: Full CLI with subcommands for all operations

### Critical Architecture Patterns

**Lazy Loading**: Models load only when first needed, then stay in memory. Monitor with:
```bash
curl http://localhost:8000/api/v1/models/status
curl -X POST http://localhost:8000/api/v1/models/preload
```

**Configuration Factory**: Use `get_config()` from `.env` files for environment-specific settings

**Database Caching**: The system caches extracted features to avoid reprocessing. Check with:
```python
# Check if image already processed
was_duplicate = extractor_instance.is_image_processed(image_path)
```

**Unified API Design**: The main images endpoint (`/api/v1/images/`) serves dual purposes:
- **List mode**: `GET /api/v1/images/?limit=20&offset=0`
- **Search mode**: `GET /api/v1/images/?query=cats&limit=5`
- **Object filtering**: `GET /api/v1/images/?objects=cat,dog&limit=10`

## Development Environment Setup

### VS Code Configuration
The project includes VS Code settings for development:
- Python cache disabling: `PYTHONDONTWRITEBYTECODE=1`
- Development launch configurations with `--dev` flag
- Proper PYTHONPATH setup for src/ directory

### Environment Variables
Key configuration through `.env` file:
```env
DEVICE=cuda                    # or cpu
USE_LOCAL_FILES_ONLY=true      # for offline operation
LOCAL_BLIP_MODEL_PATH=./models/blip/Salesforce_blip-image-captioning-base
DB_PATH=./image_vector_db
COLLECTION_NAME=image_contexts
```

### Model Management
Models are downloaded automatically on first use, but for development:
- Use local models to avoid repeated downloads
- Pre-download with `python scripts/model_utils.py --download-all`
- Models typically require ~2.2GB RAM total

## API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/api/v1/health

## Important Notes

### Performance Considerations
- **First request**: ~3.5 seconds (model loading)
- **Subsequent requests**: ~0.015 seconds (350x faster)
- **Database lookups**: Use cached data via `get_image_data_by_id()` for ~100-350x performance improvement

### Error Handling Patterns
- HTTP exceptions preserve original status codes (not 500)
- NumPy array handling uses safe extraction methods
- ChromaDB operations include proper error recovery

### Testing API Changes
Always test both list and search modes of the unified endpoint:
```bash
# Test listing
curl "http://localhost:8000/api/v1/images/?limit=5"

# Test search
curl "http://localhost:8000/api/v1/images/?query=cats&limit=3"

# Test object filtering
curl "http://localhost:8000/api/v1/images/?objects=cat,dog&limit=5"
```

This architecture provides a flexible, performant system for image understanding with multiple deployment options and comprehensive caching for production use.