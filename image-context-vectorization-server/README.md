# Image Context Extraction & Vectorization

A Python application that extracts contextual information from images using AI models and stores them in a vector database for similarity search.

## Features

- **Image Caption Generation**: Uses BLIP model to generate descriptive captions
- **Object Detection**: Identifies objects in images using CLIP model
- **Feature Extraction**: Extracts visual features using CLIP embeddings
- **Vector Database**: Stores image embeddings in ChromaDB for fast similarity search
- **Batch Processing**: Process single images or entire directories
- **Similarity Search**: Find similar images using text queries
- **Duplicate Detection**: Prevents reprocessing of already processed images
- **REST API**: Complete FastAPI backend with comprehensive endpoints
- **Model Loading Timing**: Track and optimize model loading performance
- **WebSocket Support**: Real-time updates and notifications

## Installation

### Method 1: Development Installation (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd image-context-vectorization
```

2. Install in development mode:
```bash
pip install -e .
```

### Method 2: Direct Installation

```bash
pip install -r requirements.txt
```

The application will automatically download required AI models on first run.

## Quick Start

### Basic Usage

#### Using the Package
```python
from image_context_extractor import ImageContextExtractor, Config, get_config
from image_context_extractor.utils.logging_utils import setup_logging

# Setup logging
setup_logging()

# Initialize extractor
config = get_config()  # Loads from .env
extractor = ImageContextExtractor(config)

# Process a single image
image_id = extractor.process_image("path/to/your/image.jpg")

# Process all images in a directory
result = extractor.process_directory("path/to/your/images/")

# Search for similar images
results = extractor.search_similar_images("people at a party", n_results=5)

# Get database statistics
stats = extractor.get_stats()
```

#### Using the CLI
```bash
# Process a single image
image-context-extractor process-image image.jpg

# Process a directory
image-context-extractor process-directory ./images/

# Search for similar images
image-context-extractor search "people at a party" --results 5

# Show database statistics
image-context-extractor stats

# Initialize model directory structure
image-context-extractor init-models --download
```

#### Using the Main Script
```bash
python main.py
```

Make sure to update the image paths in the examples to point to your actual images.

## Configuration

### Environment File Configuration

The easiest way to configure the application is using a `.env` file:

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```env
# Model configuration
DEVICE=cuda
LOCAL_BLIP_MODEL_PATH=./models/blip/Salesforce_blip-image-captioning-base
USE_LOCAL_FILES_ONLY=true

# Database configuration
DB_PATH=./my_custom_db
COLLECTION_NAME=my_images

# Processing configuration
OBJECT_CONFIDENCE_THRESHOLD=0.15
MAX_CAPTION_LENGTH=150
```

3. Run the application (automatically loads `.env`):
```python
from config import get_config
from main import ImageContextExtractor

config = get_config()  # Loads from .env
extractor = ImageContextExtractor(config)
```

### Environment Variables

You can also use environment variables directly:

```bash
export DEVICE=cuda
export DB_PATH=./my_db
export USE_LOCAL_FILES_ONLY=true
python main.py
```

## Model Loading Performance

The application uses several AI models that need to be loaded into memory. Here's how to monitor and optimize model loading:

### Check Model Loading Times

**Using CLI:**
```bash
# Check current model status (doesn't load models)
python -m src.image_context_extractor.cli test-models

# Preload all models and see timing
python -m src.image_context_extractor.cli test-models --preload

# Test with different device
python -m src.image_context_extractor.cli test-models --preload --device cuda
```

**Using API:**
```bash
# Check model status via API
curl http://localhost:8000/api/v1/models/status

# Preload models via API and get timing
curl -X POST http://localhost:8000/api/v1/models/preload
```

### Typical Loading Times

On CPU (M1 Mac):
- **Sentence Transformer**: ~0.4 seconds
- **BLIP Processor**: ~0.01 seconds  
- **BLIP Model**: ~2.0 seconds
- **CLIP Processor**: ~0.04 seconds
- **CLIP Model**: ~1.0 seconds
- **Total**: ~3.5 seconds

On GPU (CUDA):
- Models load faster but require additional GPU memory transfer time

### Model Loading Behavior

- **Lazy Loading**: Models load only when first used, not at startup
- **Persistent**: Once loaded, models stay in memory for subsequent requests
- **Progress Logging**: Loading progress is logged with timestamps and emojis:
  ```
  🔄 Loading BLIP model from: models/blip/Salesforce_blip-image-captioning-base
  ✅ BLIP model loaded in 2.03 seconds
  ```

### Optimization Tips

1. **Use Local Models**: Pre-download models to avoid network delays
2. **Use GPU**: Set `DEVICE=cuda` for faster inference (requires CUDA)
3. **Preload Models**: Use the preload endpoints to load models before processing
4. **Monitor Memory**: Large models require significant RAM/GPU memory

### Programmatic Configuration

For advanced use cases, configure programmatically:

```python
from config import Config, ModelConfig, DatabaseConfig

# Manual configuration
config = Config(
    model=ModelConfig(device="cuda"),
    database=DatabaseConfig(db_path="./my_custom_db"),
    processing=ProcessingConfig(object_confidence_threshold=0.2)
)

# Environment config with overrides
config = get_config(**{
    'model.device': 'cuda',
    'database.db_path': './override_db'
})

extractor = ImageContextExtractor(config)
```

### Model Paths Configuration

For advanced model management, use the model paths system:

```python
from model_paths import ModelPaths, ModelPathsManager
from config import Config, ModelConfig

# Create custom model paths
model_paths = ModelPaths(
    models_base_dir="./my_models",
    cache_base_dir="./my_cache",
    blip_model_dir="./my_models/blip/custom",
    clip_model_dir="./my_models/clip/custom"
)

# Initialize directory structure
manager = ModelPathsManager(model_paths)
manager.create_model_structure()

# Use with config
config = Config(
    model=ModelConfig(
        model_paths=model_paths,
        use_local_files_only=True
    )
)
```

### CLI Model Management

```bash
# Initialize model directory structure
python -c "from src.image_context_extractor.config.model_paths import main; main()" --init

# Show model status and sizes  
python -c "from src.image_context_extractor.config.model_paths import main; main()" --status

# Using the main CLI
image-context-extractor init-models --download
```

## Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- GIF (.gif)
- WebP (.webp)

## Architecture

The application follows a clean, modular architecture:

```
src/image_context_extractor/
├── core/           # Core functionality
├── config/         # Configuration management  
├── models/         # AI model management
├── database/       # Vector database operations
├── utils/          # Utility functions
└── cli.py          # Command-line interface
```

### Key Components

- **`core/extractor.py`**: Main orchestrator class
- **`config/settings.py`**: Configuration management with environment support
- **`config/model_paths.py`**: Model paths and storage management
- **`models/model_manager.py`**: AI model management with lazy loading
- **`database/vector_db.py`**: Vector database operations
- **`core/image_processor.py`**: Image handling and validation
- **`cli.py`**: Command-line interface for all operations

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed architecture documentation.

## Logging

The application creates detailed logs in `image_context_extraction.log` and outputs to console. Log levels can be configured during setup.

## Error Handling

Comprehensive error handling ensures graceful failures and informative error messages for debugging.

## How Vector Database Works

The system performs the following steps:

1. **Context Extraction**: Uses computer vision models to extract:
   - Visual elements (objects, people, scenes, colors)
   - Semantic meaning and relationships
   - Generated captions describing the image

2. **Vector Conversion**: Converts extracted context into numerical vectors (embeddings) that capture semantic meaning

3. **Database Storage**: Stores vectors in ChromaDB with efficient indexing for fast similarity search

4. **Similarity Search**: Enables finding similar images using natural language queries

## Using Local Models

### Download Models Locally

```bash
# Download all default models
python scripts/model_utils.py --download-all

# List local models
python scripts/model_utils.py --list

# Show model information
python scripts/model_utils.py --info

# Clean up models
python scripts/model_utils.py --clean all
```

### Configure Local Models

```python
from config import Config, ModelConfig

# Use local models
config = Config(
    model=ModelConfig(
        # Local model paths
        local_blip_model_path="./models/blip/Salesforce_blip-image-captioning-base",
        local_clip_model_path="./models/clip/openai_clip-vit-base-patch32",
        local_sentence_transformer_path="./models/sentence_transformer/all-MiniLM-L6-v2",
        
        # Force offline mode
        use_local_files_only=True,
        
        # Custom cache directory
        cache_dir="./model_cache"
    )
)

extractor = ImageContextExtractor(config)
```

### Offline Mode

```python
# Complete offline operation
config = Config(
    model=ModelConfig(
        local_blip_model_path="./models/blip/Salesforce_blip-image-captioning-base",
        local_clip_model_path="./models/clip/openai_clip-vit-base-patch32", 
        local_sentence_transformer_path="./models/sentence_transformer/all-MiniLM-L6-v2",
        use_local_files_only=True  # No internet access required
    )
)
```

### Mixed Mode

```python
# Use some local, some remote models
config = Config(
    model=ModelConfig(
        local_blip_model_path="./models/blip/Salesforce_blip-image-captioning-base",
        # CLIP and sentence transformer will be downloaded if needed
        clip_model_name="openai/clip-vit-base-patch32",
        sentence_transformer_model="all-MiniLM-L6-v2"
    )
)
```

## Performance Tips

- Use GPU acceleration with `device="cuda"` for faster processing
- Process images in batches for efficiency
- Resize large images to reduce processing time
- Use incremental updates for large collections
- Download models locally to avoid repeated downloads
- Use offline mode for air-gapped environments