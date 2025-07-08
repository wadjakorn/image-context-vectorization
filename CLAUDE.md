# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **dual-component AI-powered image management system** consisting of:
- **Backend API**: Python FastAPI server with AI models for image context extraction and vectorization
- **Frontend UI**: React TypeScript web application for image upload, search, and management

The system uses BLIP (image captioning), CLIP (object detection), and SentenceTransformers (embeddings) to extract semantic information from images and store them in ChromaDB for similarity search.

## Development Rules "IMPORTANT!"

- **Summarize the plan before coding**: Always provide a brief summary of the intended changes or features before starting implementation.
- **Be simple and do not over-engineer**: Focus on clear, maintainable code. Avoid unnecessary complexity.
- **Do not add new features**: Stick to the existing functionality. Do not introduce new features unless explicitly requested.

## Development Commands

### Backend (Python API)
```bash
# Navigate to backend directory
cd image-context-vectorization-server

# Installation
pip install -e .                    # Development installation (recommended)
pip install -r requirements.txt     # Alternative installation

# Start API server
python run_api.py --dev             # Development mode
./start_api.sh                      # Using start script
python run_api.py --host 0.0.0.0 --port 8000  # Production mode

# CLI operations
image-context-extractor process-image image.jpg
image-context-extractor process-directory ./images/
image-context-extractor search "people at a party" --results 5
image-context-extractor stats
image-context-extractor init-models --download

# Model management
python scripts/model_utils.py --download-all
image-context-extractor test-models --preload

# Examples
python examples/example_usage.py
python examples/api_examples.py
```

### Frontend (React UI)
```bash
# Navigate to frontend directory
cd image-context-vectorization-ui

# Installation and development
npm install                         # Install dependencies
npm start                          # Start development server (localhost:3000)
npm run build                      # Build for production
npm test                           # Run test suite
```

### Development Tools (if available)
```bash
# Backend linting/formatting
black src/                         # Code formatting
flake8 src/                        # Linting  
mypy src/                          # Type checking
pytest tests/                      # Testing
```

## Architecture Overview

### Repository Structure
```
image-context-vectorization/
├── image-context-vectorization-server/    # Python FastAPI backend
│   ├── src/image_context_extractor/       # Main package
│   │   ├── api/                           # FastAPI routes and app
│   │   ├── core/                          # Core business logic
│   │   ├── config/                        # Configuration management
│   │   ├── models/                        # AI model management
│   │   ├── database/                      # Vector database operations
│   │   └── utils/                         # Utility functions
│   ├── models/                            # Downloaded AI models
│   ├── examples/                          # Usage examples
│   └── scripts/                           # Utility scripts
└── image-context-vectorization-ui/        # React frontend
    ├── src/components/                # UI components
    ├── src/services/                  # API client
    └── public/                        # Static assets
```

### Core Processing Pipeline
```
Image → BLIP (caption) → CLIP (objects/features) → SentenceTransformer (embeddings) → ChromaDB (storage)
```

### Backend Architecture Key Components

**Core Engine**: 
- `src/image_context_extractor/core/extractor.py`: **Primary orchestrator** - coordinates all image processing operations
- `src/image_context_extractor/core/image_processor.py`: Image validation and metadata extraction

**AI Models Layer**:
- `src/image_context_extractor/models/model_manager.py`: **Critical component** - manages BLIP, CLIP, and SentenceTransformer models with lazy loading
- Models load on-demand and stay in memory for performance (~3.5s initial load, ~0.015s subsequent requests)

**Configuration Management**:
- `src/image_context_extractor/config/settings.py`: Environment-driven configuration with `.env` support
- `src/image_context_extractor/config/model_paths.py`: Model storage and paths management

**Vector Database**:
- `src/image_context_extractor/database/vector_db.py`: ChromaDB integration for semantic search and similarity operations

**API Layer**:
- `src/image_context_extractor/api/app.py`: FastAPI application setup
- `src/image_context_extractor/api/routes/`: Route handlers organized by functionality
- **Unified endpoint**: `GET /api/v1/images/` handles both listing and search with optional parameters

### Frontend Architecture Key Components

**Main Application**:
- `src/App.tsx`: Main application with tabbed interface (Upload → Browse & Search → Processing → Models → Directory)
- `src/services/api.ts`: **Centralized API client** with TypeScript interfaces for all backend endpoints

**Core Components**:
- `src/components/ImageBrowser.tsx`: **700+ line unified interface** combining search and gallery functionality
- `src/components/ImageUpload.tsx`: Drag-and-drop upload with progress tracking
- `src/components/ModelManagement.tsx`: AI model preloading and status monitoring
- `src/components/ProcessingStatus.tsx`: Real-time task monitoring

### Critical Architecture Patterns

**Lazy Loading Pattern**: AI models load only when first needed, then persist in memory. Monitor with:
```bash
curl http://localhost:8000/api/v1/models/status
curl -X POST http://localhost:8000/api/v1/models/preload
```

**Unified API Design**: The main images endpoint serves dual purposes:
- **List mode**: `GET /api/v1/images/?limit=20&offset=0`
- **Search mode**: `GET /api/v1/images/?query=cats&limit=5`  
- **Object filtering**: `GET /api/v1/images/?objects=cat,dog&limit=10`

**Configuration Factory Pattern**: Use `get_config()` for environment-specific settings from `.env` files

**Frontend State Management**: 
- Uses `Map<string, ImageThumbnail>` with `useRef` for tracking loaded images
- Automatic cleanup of blob URLs to prevent memory leaks
- Request deduplication to prevent duplicate API calls

## Environment Configuration

### Backend (.env in server directory)
```env
# Model configuration
DEVICE=cuda                         # or cpu
LOCAL_BLIP_MODEL_PATH=./models/blip/Salesforce_blip-image-captioning-base
USE_LOCAL_FILES_ONLY=true          # for offline operation

# Database configuration  
DB_PATH=./image_vector_db
COLLECTION_NAME=image_contexts

# Processing configuration
OBJECT_CONFIDENCE_THRESHOLD=0.15
MAX_CAPTION_LENGTH=150
```

### Frontend (.env in UI directory)
```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Timeout configuration (milliseconds)
REACT_APP_API_TIMEOUT=30000
REACT_APP_UPLOAD_TIMEOUT=120000
REACT_APP_SEARCH_TIMEOUT=60000
REACT_APP_PROCESSING_TIMEOUT=300000
REACT_APP_MODEL_PRELOAD_TIMEOUT=180000
REACT_APP_HEALTH_TIMEOUT=10000
```

## Performance Considerations

### Model Loading Performance
- **First request**: ~3.5 seconds (model loading on CPU)
- **Subsequent requests**: ~0.015 seconds (350x faster)
- **Memory usage**: ~2.2GB RAM for all models
- **GPU acceleration**: Set `DEVICE=cuda` for faster inference

### API Performance Optimization
- Use `get_image_data_by_id()` for cached lookups (100-350x performance improvement)
- Preload models before processing batches
- Database caching prevents reprocessing duplicate images

### Frontend Performance Optimization
- **Lazy thumbnail loading**: Images load on-demand via `/api/v1/images/download/{id}`
- **Request deduplication**: Prevents duplicate API calls during state changes
- **Memory cleanup**: Automatic blob URL revocation
- **useCallback optimization**: Critical functions memoized to prevent re-renders

## API Documentation

When the backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/api/v1/health

## Development Workflow

### Starting Development Environment
1. **Start Backend**: `cd image-context-vectorization-server && python run_api.py --dev`
2. **Wait for API to initialize**: Ensure models are preloaded and API is responsive
3. **Start Frontend**: `cd image-context-vectorization-ui && npm start`
4. **Access UI**: http://localhost:3000 (connects to API on localhost:8000)

### Testing Changes
Always test both modes of the unified API endpoint:
```bash
# Test listing
curl "http://localhost:8000/api/v1/images/?limit=5"

# Test search  
curl "http://localhost:8000/api/v1/images/?query=cats&limit=3"

# Test object filtering
curl "http://localhost:8000/api/v1/images/?objects=cat,dog&limit=5"
```

### Model Management
- **Download models locally**: `python scripts/model_utils.py --download-all`
- **Check model status**: `image-context-extractor test-models --preload`
- **Preload via API**: `curl -X POST http://localhost:8000/api/v1/models/preload`

## Important Notes

### Error Handling
- Backend preserves original HTTP status codes (not generic 500s)
- Frontend includes operation-specific timeouts with visual indicators
- ChromaDB operations include proper error recovery

### File Support
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP, WebP
- **Upload limits**: 10MB per file, 10 files per batch
- **Processing**: Automatic AI processing on upload (configurable)

### Database Operations
- Check for duplicates: `extractor_instance.is_image_processed(image_path)`
- Vector similarity search with configurable thresholds
- Cached metadata for performance optimization

This architecture provides a comprehensive, scalable system for AI-powered image management with multiple deployment options and extensive performance optimizations.