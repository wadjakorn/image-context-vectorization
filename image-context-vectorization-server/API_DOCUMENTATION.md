# Image Context Extractor API Documentation

## Overview

The Image Context Extractor API provides a comprehensive REST API and WebSocket interface for processing images, extracting contextual information, and performing similarity searches. The API is built with FastAPI and includes automatic documentation, real-time updates, model loading management, and comprehensive error handling.

## Quick Start

### 1. Start the API Server

```bash
# Method 1: Using the run script
python run_api.py --dev

# Method 2: Using the CLI
image-context-extractor serve --dev

# Method 3: Direct uvicorn
uvicorn src.image_context_extractor.api.app:create_app --reload --host 0.0.0.0 --port 8000
```

### 2. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Info**: http://localhost:8000/api/v1/info

### 3. Test the API

```bash
# Check health
curl http://localhost:8000/api/v1/health

# Check model status
curl http://localhost:8000/api/v1/models/status

# Preload models (optional for faster responses)
curl -X POST http://localhost:8000/api/v1/models/preload

# Run example tests
python examples/api_examples.py
```

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding authentication middleware.

## API Endpoints

### Health & Status

#### `GET /api/v1/health`
Get service health status and basic information.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database_connected": true,
  "models_loaded": true,
  "uptime": 123.45,
  "stats": {
    "total_images": 150,
    "collection_name": "image_contexts",
    "db_path": "./image_vector_db"
  }
}
```

#### `GET /api/v1/status`
Get detailed system status including CPU, memory, and disk usage.

#### `GET /api/v1/config`
Get current configuration settings.

#### `GET /api/v1/metrics`
Get application metrics and statistics.

---

### Model Management

#### `GET /api/v1/models/status`
Get current model loading status without triggering model loads.

**Response:**
```json
{
  "models": {
    "blip_processor": true,
    "blip_model": true,
    "clip_processor": true,
    "clip_model": true,
    "sentence_transformer": true
  },
  "device": "cpu",
  "timestamp": "2025-07-07T10:36:13.577413"
}
```

#### `POST /api/v1/models/preload`
Preload all models and return detailed timing information.

**Response:**
```json
{
  "success": true,
  "timings": {
    "sentence_transformer": 0.37,
    "blip_processor": 0.01,
    "blip_model": 1.64,
    "clip_processor": 0.04,
    "clip_model": 0.96,
    "total": 3.02
  },
  "device": "cpu",
  "timestamp": "2025-07-07T10:35:46.147405"
}
```

**Use Cases:**
- Check which models are already loaded in memory
- Preload models during server startup or warm-up
- Monitor model loading performance
- Optimize cold start times

**Typical Loading Times:**
- **CPU (M1 Mac)**: ~3.5 seconds total
- **GPU (CUDA)**: Varies based on GPU and model size

---

### Image Processing

#### `POST /api/v1/images/process`
Process a single image and extract contextual information.

**Request Body:**
```json
{
  "image_path": "/path/to/image.jpg",
  "force_reprocess": false
}
```

**Response:**
```json
{
  "success": true,
  "image_id": "abc123...",
  "message": "Image processed successfully",
  "image_info": {
    "id": "abc123...",
    "path": "/path/to/image.jpg",
    "filename": "image.jpg",
    "size": [1920, 1080],
    "file_size": 2048576,
    "format": "JPEG",
    "caption": "A beautiful sunset over the ocean",
    "objects": ["sky", "water", "sun"]
  },
  "processing_time": 2.34,
  "was_duplicate": false
}
```

#### `POST /api/v1/images/upload`
Upload an image file and optionally process it immediately.

**Request:** Multipart form data
- `file`: Image file (required)
- `process_immediately`: Boolean (default: true)
- `overwrite`: Boolean (default: false)
- `upload_dir`: String (default: "uploads")

**Response:**
```json
{
  "success": true,
  "filename": "uploaded_image.jpg",
  "file_path": "uploads/uploaded_image.jpg",
  "file_size": 1024768,
  "image_id": "def456...",
  "message": "Image uploaded and processed successfully"
}
```

#### `GET /api/v1/images/info/{image_id}`
Get detailed information about a processed image.

#### `GET /api/v1/images/download/{image_id}`
Download an image file by its ID.

#### `GET /api/v1/images/`
List all processed images or search for similar images based on query.

**Query Parameters:**
- `query`: Optional search query. If provided, performs similarity search instead of listing
- `objects`: Optional comma-separated list of objects to filter by (e.g., "cat,dog,person")
- `limit`: Number of results (default: 100)
- `offset`: Offset for pagination (default: 0, list mode only)
- `min_score`: Minimum similarity score for search results (default: null, search mode only)
- `include_metadata`: Include search metadata like score and distance (default: true, search mode only)

**Examples:**

List all images:
```bash
GET /api/v1/images/?limit=20&offset=0
```

List images containing cats:
```bash
GET /api/v1/images/?objects=cat&limit=20
```

List images containing cats or dogs:
```bash
GET /api/v1/images/?objects=cat,dog&limit=20
```

Search for images with objects filter:
```bash
GET /api/v1/images/?query=cats%20playing&objects=cat&limit=5&min_score=0.7
```

Search for images containing person or child:
```bash
GET /api/v1/images/?query=playground&objects=person,child&limit=10
```

**Response (List Mode):**
```json
[
  {
    "id": "abc123...",
    "path": "/path/to/image.jpg",
    "filename": "image.jpg",
    "size": [1920, 1080],
    "file_size": 2048576,
    "format": "JPEG",
    "caption": "A beautiful sunset over the ocean",
    "objects": ["sky", "water", "sun"]
  }
]
```

**Response (Search Mode):**
```json
[
  {
    "id": "abc123...",
    "path": "/path/to/image.jpg",
    "filename": "image.jpg",
    "size": [1920, 1080],
    "file_size": 2048576,
    "format": "JPEG",
    "caption": "Two cats playing with a ball",
    "objects": ["cat", "animal"],
    "score": 0.85,
    "distance": 0.15
  }
]
```

#### `DELETE /api/v1/images/{image_id}`
Delete an image from the database and optionally from disk.

**Query Parameters:**
- `delete_file`: Boolean - also delete file from disk (default: false)

---

### Directory Processing

#### `POST /api/v1/directories/process`
Process all images in a directory synchronously.

**Request Body:**
```json
{
  "directory_path": "/path/to/images/",
  "force_reprocess": false,
  "recursive": false
}
```

**Response:**
```json
{
  "success": true,
  "total_files": 50,
  "processed": 45,
  "skipped": 3,
  "failed": 2,
  "processed_ids": ["id1", "id2", "..."],
  "failed_files": ["/path/to/failed1.jpg"],
  "processing_time": 123.45,
  "message": "Directory processed: 45 images processed"
}
```

#### `POST /api/v1/directories/process-async`
Process all images in a directory asynchronously (background task).

**Response:**
```json
{
  "task_id": "task-uuid-123",
  "status": "queued",
  "message": "Directory processing started in background"
}
```

#### `GET /api/v1/directories/scan`
Scan a directory for image files without processing them.

**Query Parameters:**
- `directory_path`: Path to directory (required)
- `recursive`: Boolean - scan subdirectories (default: false)

#### `GET /api/v1/directories/task/{task_id}`
Get status of a background processing task.

**Response:**
```json
{
  "task_id": "task-uuid-123",
  "status": "processing",
  "progress": 65.5,
  "message": "Processing image 33 of 50",
  "result": null,
  "error": null,
  "created_at": "2023-12-01T10:00:00",
  "updated_at": "2023-12-01T10:05:00"
}
```

#### `GET /api/v1/directories/tasks`
List all background processing tasks.


---

### Duplicate Detection

#### `POST /api/v1/duplicates/check`
Check for duplicate images.

**Request Body:**
```json
{
  "image_path": "/path/to/check.jpg",
  "directory_path": "/path/to/directory/",
  "similarity_threshold": 0.95
}
```

**Response:**
```json
{
  "success": true,
  "total_images": 100,
  "duplicate_groups": [
    {
      "representative_id": "img123",
      "duplicate_ids": ["img124", "img125"],
      "similarity_scores": [0.98, 0.96],
      "paths": ["/path/1.jpg", "/path/2.jpg", "/path/3.jpg"]
    }
  ],
  "total_duplicates": 5,
  "check_time": 12.34,
  "message": "Found 2 duplicate groups with 5 duplicate images"
}
```

#### `GET /api/v1/duplicates/check-image`
Check if a specific image has duplicates.

#### `GET /api/v1/duplicates/check-directory`
Check for duplicates within a directory.

#### `POST /api/v1/duplicates/compare`
Compare two specific images and return similarity metrics.

**Request Body:**
```json
{
  "image1_path": "/path/to/image1.jpg",
  "image2_path": "/path/to/image2.jpg"
}
```

#### `DELETE /api/v1/duplicates/remove-duplicates`
Remove duplicate images from database and optionally from disk.

**Query Parameters:**
- `similarity_threshold`: Threshold for duplicates (default: 0.98)
- `dry_run`: Don't actually delete (default: true)
- `keep_first`: Keep first image in each group (default: true)

---

### WebSocket Endpoints

#### `WS /ws`
General WebSocket endpoint for real-time updates.

#### `WS /ws/processing`
WebSocket endpoint for processing updates.

#### `WS /ws/search`
WebSocket endpoint for live search functionality.

**Example WebSocket Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Send ping
ws.send(JSON.stringify({"type": "ping"}));

// Subscribe to processing updates
ws.send(JSON.stringify({
  "type": "subscribe",
  "channel": "processing"
}));
```

#### `GET /ws/stats`
Get WebSocket connection statistics.

---

## Model Loading and Performance

### Model Loading Behavior

The API uses **lazy loading** for AI models, meaning models are loaded into memory only when first needed. This provides several benefits:

- **Fast Startup**: API server starts immediately without waiting for models
- **Memory Efficiency**: Only load models that are actually used
- **Scalability**: Different instances can load different model combinations

### Model Loading Process

1. **API Startup**: Server starts with no models loaded
2. **First Request**: When an endpoint needs a model, it triggers loading with detailed logging
3. **Subsequent Requests**: Models stay in memory for fast access
4. **Manual Preloading**: Use `/api/v1/models/preload` to load all models upfront

### Loading Time Examples

**CPU (M1 Mac):**
```
🔄 Loading Sentence Transformer from: models/sentence_transformer/all-MiniLM-L6-v2
✅ Sentence Transformer loaded in 0.39 seconds

🔄 Loading BLIP model from: models/blip/Salesforce_blip-image-captioning-base
✅ BLIP model loaded in 2.03 seconds

🎉 All models preloaded in 3.50 seconds
```

**GPU (CUDA):**
- Additional time for GPU memory transfer
- Faster inference after loading

### Performance Optimization

1. **Preload Models**: Call `/api/v1/models/preload` during server warm-up
2. **Use Local Models**: Set `USE_LOCAL_FILES_ONLY=true` to avoid downloads
3. **GPU Acceleration**: Set `DEVICE=cuda` for faster inference
4. **Monitor Status**: Use `/api/v1/models/status` to check what's loaded

### Model Memory Usage

Approximate memory requirements:
- **Sentence Transformer**: ~400MB
- **BLIP Model**: ~1.2GB
- **CLIP Model**: ~600MB
- **Total**: ~2.2GB RAM

---

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses:

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Image file not found: /path/to/image.jpg",
  "details": {
    "status_code": 404
  },
  "timestamp": "2023-12-01T10:00:00"
}
```

### Common Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `409`: Conflict (file already exists)
- `422`: Unprocessable Entity (invalid data)
- `500`: Internal Server Error

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider adding rate limiting middleware.

---

## CORS

CORS is enabled for all origins in development. Configure appropriately for production.

---

## Development

### Running in Development Mode

```bash
# With auto-reload
python run_api.py --dev

# Or using CLI
image-context-extractor serve --dev
```

### Adding Dependencies

```bash
pip install new-dependency
# Update requirements.txt
pip freeze > requirements.txt
```

### Testing

```bash
# Run API examples
python examples/api_examples.py

# Manual testing with curl
curl -X GET "http://localhost:8000/api/v1/health"
```

---

## Production Deployment

### Environment Variables

Create a `.env` file with production settings:

```env
# Model configuration
DEVICE=cuda
USE_LOCAL_FILES_ONLY=true
LOCAL_BLIP_MODEL_PATH=/app/models/blip/model
LOCAL_CLIP_MODEL_PATH=/app/models/clip/model

# Database
DB_PATH=/app/data/vector_db
COLLECTION_NAME=production_images

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/api.log
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run_api.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Considerations

1. Add authentication middleware
2. Configure CORS for specific origins
3. Use HTTPS in production
4. Implement rate limiting
5. Validate and sanitize file uploads
6. Use environment variables for secrets

---

## Troubleshooting

### Common Issues

1. **Models not loading**: Check CUDA availability and model paths
2. **Database connection failed**: Verify ChromaDB installation and permissions
3. **File upload fails**: Check upload directory permissions
4. **WebSocket disconnects**: Check firewall settings and proxy configuration

### Logs

Check application logs for detailed error information:

```bash
tail -f image_context_extraction.log
```

---

## API Client Examples

### Python

```python
import aiohttp
import asyncio

async def process_image(image_path):
    async with aiohttp.ClientSession() as session:
        payload = {"image_path": image_path}
        async with session.post(
            "http://localhost:8000/api/v1/images/process",
            json=payload
        ) as response:
            return await response.json()

# Usage
result = asyncio.run(process_image("/path/to/image.jpg"))
print(result)
```

### JavaScript

```javascript
// Process image
const processImage = async (imagePath) => {
  const response = await fetch('http://localhost:8000/api/v1/images/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_path: imagePath,
      force_reprocess: false
    })
  });
  
  return await response.json();
};

// Search images
const searchImages = async (query, objects = null) => {
  let url = `http://localhost:8000/api/v1/images/?query=${encodeURIComponent(query)}&limit=5`;
  if (objects) {
    url += `&objects=${encodeURIComponent(objects)}`;
  }
  const response = await fetch(url);
  return await response.json();
};

// List all images
const listImages = async (limit = 20, offset = 0, objects = null) => {
  let url = `http://localhost:8000/api/v1/images/?limit=${limit}&offset=${offset}`;
  if (objects) {
    url += `&objects=${encodeURIComponent(objects)}`;
  }
  const response = await fetch(url);
  return await response.json();
};

// Filter images by objects
const filterImagesByObjects = async (objects, limit = 20) => {
  const response = await fetch(`http://localhost:8000/api/v1/images/?objects=${encodeURIComponent(objects)}&limit=${limit}`);
  return await response.json();
};

// Check model status
const checkModelStatus = async () => {
  const response = await fetch('http://localhost:8000/api/v1/models/status');
  return await response.json();
};

// Preload models
const preloadModels = async () => {
  const response = await fetch('http://localhost:8000/api/v1/models/preload', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  });
  return await response.json();
};
```

### cURL

```bash
# Health check
curl -X GET "http://localhost:8000/api/v1/health"

# Process image
curl -X POST "http://localhost:8000/api/v1/images/process" \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/path/to/image.jpg"}'

# Search images
curl -X GET "http://localhost:8000/api/v1/images/?query=cats&limit=3"

# List all images
curl -X GET "http://localhost:8000/api/v1/images/?limit=20&offset=0"

# Filter images by objects
curl -X GET "http://localhost:8000/api/v1/images/?objects=cat,dog&limit=10"

# Search with object filter
curl -X GET "http://localhost:8000/api/v1/images/?query=playing&objects=cat&limit=5"

# Upload image
curl -X POST "http://localhost:8000/api/v1/images/upload" \
  -F "file=@/path/to/image.jpg" \
  -F "process_immediately=true"

# Check model status
curl -X GET "http://localhost:8000/api/v1/models/status"

# Preload models
curl -X POST "http://localhost:8000/api/v1/models/preload"
```

This API provides a complete solution for image context extraction with support for web frontends, mobile apps, and other client applications.