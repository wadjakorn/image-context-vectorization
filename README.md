# Image Context Vectorization

An AI-powered image management system that extracts contextual information from images using machine learning models and enables semantic search through natural language queries.

## System Architecture

This project consists of two main components:

- **🐍 [Backend API](./image-context-vectorization-server/)** - Python FastAPI server with AI models (BLIP, CLIP, SentenceTransformers) for image processing and ChromaDB vector database for semantic search
- **⚛️ [Frontend UI](./image-context-vectorization-ui/)** - React TypeScript web application with drag-and-drop uploads, AI-powered search, and image gallery management

## Key Features

### Backend Capabilities
- **AI-Powered Analysis**: BLIP for captions, CLIP for objects, SentenceTransformers for embeddings
- **Vector Database**: ChromaDB for fast similarity search and duplicate detection
- **REST API**: Comprehensive FastAPI with WebSocket support and real-time updates
- **Model Management**: Lazy loading with performance monitoring and local model caching
- **Batch Processing**: CLI and API endpoints for directory processing

### Frontend Features
- **Modern UI**: Responsive React interface with dark mode support
- **Smart Search**: Natural language queries with object filtering
- **File Management**: Drag-and-drop uploads with progress tracking
- **Real-time Monitoring**: Processing status and model loading insights
- **Performance Optimization**: Request deduplication and memory-efficient thumbnail loading

## Quick Start

### 1. Backend Setup
```bash
cd image-context-vectorization-server
pip install -e .
python run_api.py --dev
```

### 2. Frontend Setup
```bash
cd image-context-vectorization-ui
npm install
npm start
```

### 3. Access the Application
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## Example Usage

### CLI Operations
```bash
# Process images
image-context-extractor process-directory ./photos/

# Search with natural language
image-context-extractor search "cats playing" --results 5

# Check system stats
image-context-extractor stats
```

### API Endpoints
```bash
# Upload and process images
curl -X POST "http://localhost:8000/api/v1/images/upload" -F "file=@image.jpg"

# Search images
curl "http://localhost:8000/api/v1/images/?query=sunset&limit=5"

# Filter by objects
curl "http://localhost:8000/api/v1/images/?objects=cat,dog&limit=10"
```

### Web Interface
1. **Upload** - Drag and drop images for automatic AI processing
2. **Search** - Use natural language like "people at beach" or "red car"
3. **Browse** - View gallery with AI-generated captions and detected objects
4. **Monitor** - Track processing status and model performance

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Frontend │───▶│   FastAPI Server │───▶│   ChromaDB      │
│  (TypeScript)   │    │   (Python)       │    │   (Vectors)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   AI Models      │
                       │   BLIP + CLIP +  │
                       │   Transformers   │
                       └──────────────────┘
```

## Technology Stack

### Backend
- **FastAPI** - High-performance API framework
- **ChromaDB** - Vector database for semantic search
- **Transformers** - Hugging Face models (BLIP, CLIP, SentenceTransformers)
- **PIL/Pillow** - Image processing
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - Modern frontend framework
- **TypeScript** - Type safety and developer experience
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client with timeout handling
- **React Dropzone** - File upload interface

## Performance

### Model Loading Times (CPU/M1 Mac)
- **First Request**: ~3.5 seconds (model loading)
- **Subsequent Requests**: ~0.015 seconds (350x faster)
- **Memory Usage**: ~2.2GB RAM for all models
- **GPU Support**: Set `DEVICE=cuda` for faster inference

### Optimization Features
- **Lazy Loading**: Models load only when needed
- **Local Caching**: Avoid reprocessing duplicate images
- **Request Deduplication**: Prevent redundant API calls
- **Memory Management**: Automatic cleanup of image resources

## Configuration

Both components support extensive configuration through environment variables:

- **Backend**: See [server configuration](./image-context-vectorization-server/README.md#configuration)
- **Frontend**: See [UI configuration](./image-context-vectorization-ui/README.md#configuration)

## Documentation

### Detailed Documentation
- **[Backend README](./image-context-vectorization-server/README.md)** - Complete API setup, configuration, and usage
- **[Frontend README](./image-context-vectorization-ui/README.md)** - UI features, development, and deployment
- **[API Documentation](./image-context-vectorization-server/API_DOCUMENTATION.md)** - Complete REST API reference

### Additional Resources
- **[Project Structure](./image-context-vectorization-server/PROJECT_STRUCTURE.md)** - Architecture details
- **[Troubleshooting](./image-context-vectorization-server/TROUBLESHOOTING.md)** - Common issues and solutions

## Development

### Requirements
- **Backend**: Python 3.8+, pip
- **Frontend**: Node.js 16+, npm
- **Optional**: CUDA-compatible GPU for faster processing

### Development Workflow
1. Start backend API server
2. Wait for model initialization
3. Start frontend development server
4. Access web interface at localhost:3000

## Use Cases

- **Photo Management**: Organize personal photo collections with AI-generated tags
- **Content Discovery**: Find images using natural language descriptions
- **Digital Asset Management**: Manage large image repositories with semantic search
- **Duplicate Detection**: Identify and manage similar or duplicate images
- **Research & Analysis**: Extract insights from image collections

## License

This project is designed for educational and research purposes. See individual component directories for specific licensing information.