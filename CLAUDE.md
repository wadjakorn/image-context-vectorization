# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **dual-component AI-powered image management system** consisting of:
- **Backend API**: Python FastAPI server with AI models for image context extraction and vectorization
- **Frontend UI**: React TypeScript web application for image upload, search, and management

The system uses BLIP (image captioning), CLIP (object detection), and SentenceTransformers (embeddings) to extract semantic information from images and store them in ChromaDB for similarity search.

## Development Rules "IMPORTANT!"

- **Do not coding until user allow to start**: Always provide a brief summary of the intended changes or features. let user approve before starting implementation.
- **Do not add new features**: Stick to the existing functionality. Do not introduce new features unless user requested.
- **Use Gemini CLI passively**: To minimize context window usage, use the Gemini CLI with the `-p` flag for code analysis and verification tasks.

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
- `src/components/ImageBrowser.tsx`: **Unified interface** combining search and gallery functionality
- `src/components/ImageUpload.tsx`: Drag-and-drop upload with progress tracking
- `src/components/ModelManagement.tsx`: AI model preloading and status monitoring
- `src/components/ProcessingStatus.tsx`: Real-time task monitoring
- `src/components/DirectoryScanner.tsx`: Directory scanning functionality
- `src/components/TimeoutIndicator.tsx`: Timeout status indicator

### Critical Architecture Patterns

**Lazy Loading Pattern**: AI models load only when first needed, then persist in memory. Monitor with:
```bash
curl http://localhost:8000/api/v1/models/status
curl -X POST http://localhost:8000/api/v1/models/preload
```

**Unified API Design**: The main images endpoint serves dual purposes:
- **List mode**: `GET /api/v1/images/?limit=20&offset=0`
- **Search mode**: `GET /api/v1/images/?query=cats&limit=5`

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

## Development Workflow

### Starting Development Environment
1. **Start Backend**: `cd image-context-vectorization-server && python run_api.py --dev`
2. **Wait for API to initialize**: Ensure models are preloaded and API is responsive
3. **Start Frontend**: `cd image-context-vectorization-ui && npm start`
4. **Access UI**: http://localhost:3000 (connects to API on localhost:8000)

# Using Gemini CLI for Large Codebase Analysis

When analyzing large codebases or multiple files that might exceed context limits, use the Gemini CLI with its massive
context window. Use `gemini -p` to leverage Google Gemini's large context capacity.

## File and Directory Inclusion Syntax

Use the `@` syntax to include files and directories in your Gemini prompts. The paths should be relative to WHERE you run the
gemini command:

### Examples:

**Single file analysis:**
```bash
gemini -p "@src/main.py Explain this file's purpose and structure"

Multiple files:
gemini -p "@package.json @src/index.js Analyze the dependencies used in the code"

Entire directory:
gemini -p "@src/ Summarize the architecture of this codebase"

Multiple directories:
gemini -p "@src/ @tests/ Analyze test coverage for the source code"

Current directory and subdirectories:
gemini -p "@./ Give me an overview of this entire project"

#
Or use --all_files flag:
gemini --all_files -p "Analyze the project structure and dependencies"

Implementation Verification Examples

Check if a feature is implemented:
gemini -p "@src/ @lib/ Has dark mode been implemented in this codebase? Show me the relevant files and functions"

Verify authentication implementation:
gemini -p "@src/ @middleware/ Is JWT authentication implemented? List all auth-related endpoints and middleware"

Check for specific patterns:
gemini -p "@src/ Are there any React hooks that handle WebSocket connections? List them with file paths"

Verify error handling:
gemini -p "@src/ @api/ Is proper error handling implemented for all API endpoints? Show examples of try-catch blocks"

Check for rate limiting:
gemini -p "@backend/ @middleware/ Is rate limiting implemented for the API? Show the implementation details"

Verify caching strategy:
gemini -p "@src/ @lib/ @services/ Is Redis caching implemented? List all cache-related functions and their usage"

Check for specific security measures:
gemini -p "@src/ @api/ Are SQL injection protections implemented? Show how user inputs are sanitized"

Verify test coverage for features:
gemini -p "@src/payment/ @tests/ Is the payment processing module fully tested? List all test cases"

When to Use Gemini CLI

Use gemini -p when:
- Analyzing entire codebases or large directories
- Comparing multiple large files
- Need to understand project-wide patterns or architecture
- Current context window is insufficient for the task
- Working with files totaling more than 100KB
- Verifying if specific features, patterns, or security measures are implemented
- Checking for the presence of certain coding patterns across the entire codebase

Important Notes

- Paths in @ syntax are relative to your current working directory when invoking gemini
- The CLI will include file contents directly in the context
- No need for --yolo flag for read-only analysis
- Gemini's context window can handle entire codebases that would overflow Claude's context
- When checking implementations, be specific about what you're looking for to get accurate results # Using Gemini CLI for Large Codebase Analysis


When analyzing large codebases or multiple files that might exceed context limits, use the Gemini CLI with its massive
context window. Use `gemini -p` to leverage Google Gemini's large context capacity.


## File and Directory Inclusion Syntax


Use the `@` syntax to include files and directories in your Gemini prompts. The paths should be relative to WHERE you run the
gemini command:


### Examples:


**Single file analysis:**
```bash
gemini -p "@src/main.py Explain this file's purpose and structure"


Multiple files:
gemini -p "@package.json @src/index.js Analyze the dependencies used in the code"


Entire directory:
gemini -p "@src/ Summarize the architecture of this codebase"


Multiple directories:
gemini -p "@src/ @tests/ Analyze test coverage for the source code"


Current directory and subdirectories:
gemini -p "@./ Give me an overview of this entire project"
# Or use --all_files flag:
gemini --all_files -p "Analyze the project structure and dependencies"


Implementation Verification Examples


Check if a feature is implemented:
gemini -p "@src/ @lib/ Has dark mode been implemented in this codebase? Show me the relevant files and functions"


Verify authentication implementation:
gemini -p "@src/ @middleware/ Is JWT authentication implemented? List all auth-related endpoints and middleware"


Check for specific patterns:
gemini -p "@src/ Are there any React hooks that handle WebSocket connections? List them with file paths"


Verify error handling:
gemini -p "@src/ @api/ Is proper error handling implemented for all API endpoints? Show examples of try-catch blocks"


Check for rate limiting:
gemini -p "@backend/ @middleware/ Is rate limiting implemented for the API? Show the implementation details"


Verify caching strategy:
gemini -p "@src/ @lib/ @services/ Is Redis caching implemented? List all cache-related functions and their usage"


Check for specific security measures:
gemini -p "@src/ @api/ Are SQL injection protections implemented? Show how user inputs are sanitized"


Verify test coverage for features:
gemini -p "@src/payment/ @tests/ Is the payment processing module fully tested? List all test cases"


When to Use Gemini CLI


Use gemini -p when:
- Analyzing entire codebases or large directories
- Comparing multiple large files
- Need to understand project-wide patterns or architecture
- Current context window is insufficient for the task
- Working with files totaling more than 100KB
- Verifying if specific features, patterns, or security measures are implemented
- Checking for the presence of certain coding patterns across the entire codebase


Important Notes
- Paths in @ syntax are relative to your current working directory when invoking gemini
- The CLI will include file contents directly in the context
- No need for --yolo flag for read-only analysis
- Gemini's context window can handle entire codebases that would overflow Claude's context
- When checking implementations, be specific about what you're looking for to get accurate results

