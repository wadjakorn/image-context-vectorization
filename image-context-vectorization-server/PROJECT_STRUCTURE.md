# Project Structure

This document describes the structure and organization of the Image Context Extractor project.

## Directory Structure

```
image-context-vectorization/
├── src/                                    # Source code package
│   └── image_context_extractor/           # Main package
│       ├── __init__.py                     # Package initialization and exports
│       ├── cli.py                          # Command-line interface
│       ├── core/                           # Core functionality
│       │   ├── __init__.py
│       │   ├── extractor.py               # Main ImageContextExtractor class
│       │   └── image_processor.py         # Image processing utilities
│       ├── config/                         # Configuration management
│       │   ├── __init__.py
│       │   ├── settings.py                # Configuration classes
│       │   └── model_paths.py             # Model paths management
│       ├── models/                         # AI models management
│       │   ├── __init__.py
│       │   └── model_manager.py           # Model loading and management
│       ├── database/                       # Vector database operations
│       │   ├── __init__.py
│       │   └── vector_db.py               # ChromaDB vector operations
│       └── utils/                          # Utility functions
│           ├── __init__.py
│           └── logging_utils.py           # Logging configuration
├── examples/                               # Usage examples
│   ├── example_usage.py                   # Basic usage examples
│   ├── example_env_config.py              # Environment configuration examples
│   ├── example_local_models.py            # Local models examples
│   └── example_model_paths.py             # Model paths examples
├── scripts/                                # Utility scripts
│   └── model_utils.py                     # Model download and management
├── tests/                                  # Test files (future)
├── docs/                                   # Documentation (future)
├── main.py                                 # Main entry point
├── setup.py                               # Package setup and installation
├── requirements.txt                       # Python dependencies
├── .env.example                           # Environment configuration template
├── .gitignore                             # Git ignore rules
└── README.md                              # Project documentation
```

## Package Components

### `src/image_context_extractor/`
Main package containing all the core functionality.

#### `core/`
- **`extractor.py`**: Main `ImageContextExtractor` class that orchestrates the entire pipeline
- **`image_processor.py`**: Image loading, validation, and metadata extraction

#### `config/`
- **`settings.py`**: Configuration classes (`Config`, `ModelConfig`, `DatabaseConfig`, `ProcessingConfig`)
- **`model_paths.py`**: Model paths management and organization

#### `models/`
- **`model_manager.py`**: AI model loading and management (BLIP, CLIP, Sentence Transformers)

#### `database/`
- **`vector_db.py`**: Vector database operations using ChromaDB

#### `utils/`
- **`logging_utils.py`**: Logging configuration and utilities

### `examples/`
Complete working examples demonstrating different features:
- Basic usage
- Environment configuration
- Local models setup
- Model paths management

### `scripts/`
Utility scripts for maintenance and setup:
- Model downloading and management
- Database utilities

## Key Design Patterns

### 1. **Separation of Concerns**
Each module has a single responsibility:
- Configuration management is separate from business logic
- Model management is isolated from database operations
- Image processing is independent of AI models

### 2. **Dependency Injection**
Configuration objects are passed to components, making the system:
- Testable
- Configurable
- Modular

### 3. **Factory Pattern**
Configuration classes use factory methods (`from_env()`) to create instances from different sources.

### 4. **Package Structure**
Following Python best practices:
- `src/` layout for better packaging
- Clear module boundaries
- Proper `__init__.py` files with exports

## Import Structure

### From Package Root
```python
from image_context_extractor import ImageContextExtractor, Config, get_config
```

### From Submodules
```python
from image_context_extractor.config import ModelConfig, DatabaseConfig
from image_context_extractor.models import ModelManager
from image_context_extractor.database import VectorDatabase
```

## Configuration Flow

1. **Environment Variables** → Load from `.env` file or system environment
2. **Config Classes** → Parse and validate configuration
3. **Component Initialization** → Pass config to components
4. **Runtime** → Use configured components

## Extension Points

### Adding New Models
1. Extend `ModelManager` class
2. Add configuration options to `ModelConfig`
3. Update model paths if needed

### Adding New Databases
1. Create new database module in `database/`
2. Implement common interface
3. Add configuration to `DatabaseConfig`

### Adding New Image Processors
1. Extend `ImageProcessor` class
2. Add processing options to `ProcessingConfig`

## Development Workflow

### Local Development
```bash
# Install in development mode
pip install -e .

# Run examples
python examples/example_usage.py

# Use CLI
python -m image_context_extractor.cli --help
```

### Testing
```bash
# Run tests (future)
pytest tests/

# Type checking
mypy src/

# Code formatting
black src/
```

### Building
```bash
# Build package
python setup.py sdist bdist_wheel

# Install from source
pip install .
```

This structure provides a clean, maintainable, and extensible codebase that follows Python packaging best practices.