# Troubleshooting Guide

## Common Issues and Solutions

### ChromaDB Telemetry Error

**Error Message:**
```
Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
```

**Cause:** ChromaDB has telemetry enabled by default, which can cause compatibility issues with certain versions.

**Solution:** This has been automatically fixed in the application by disabling ChromaDB telemetry. The following environment variables are set:

```bash
ANONYMIZED_TELEMETRY=False
CHROMA_CLIENT_DISABLE_TELEMETRY=True
```

**Manual Fix (if needed):**
1. Set environment variables before running:
   ```bash
   export ANONYMIZED_TELEMETRY=False
   export CHROMA_CLIENT_DISABLE_TELEMETRY=True
   python main.py
   ```

2. Or add to your `.env` file:
   ```env
   ANONYMIZED_TELEMETRY=False
   CHROMA_CLIENT_DISABLE_TELEMETRY=True
   ```

---

### Model Loading Issues

**Error:** Models fail to load or CUDA out of memory

**Solutions:**
1. **Use CPU instead of GPU:**
   ```env
   DEVICE=cpu
   ```

2. **Use local models to avoid downloads:**
   ```bash
   python scripts/model_utils.py --download-all
   ```
   Then set:
   ```env
   USE_LOCAL_FILES_ONLY=true
   LOCAL_BLIP_MODEL_PATH=./models/blip/Salesforce_blip-image-captioning-base
   ```

3. **Clear model cache:**
   ```bash
   rm -rf ~/.cache/huggingface/
   rm -rf ./model_cache/
   ```

---

### Database Connection Issues

**Error:** ChromaDB database connection fails

**Solutions:**
1. **Check permissions:**
   ```bash
   ls -la ./image_vector_db/
   chmod -R 755 ./image_vector_db/
   ```

2. **Delete and recreate database:**
   ```bash
   rm -rf ./image_vector_db/
   # Restart application to recreate
   ```

3. **Use different database path:**
   ```env
   DB_PATH=/tmp/image_vector_db
   ```

---

### API Server Issues

**Error:** FastAPI server fails to start

**Solutions:**
1. **Check port availability:**
   ```bash
   lsof -i :8000
   # Kill any processes using the port
   kill -9 <PID>
   ```

2. **Use different port:**
   ```bash
   python run_api.py --port 8080
   ```

3. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

### File Upload Issues

**Error:** Image upload fails or processing errors

**Solutions:**
1. **Check file permissions:**
   ```bash
   chmod 644 /path/to/image.jpg
   ```

2. **Verify supported formats:**
   - Supported: PNG, JPEG, BMP, GIF, WebP
   - Check file extension and actual format match

3. **Check file size:**
   - Large files may cause memory issues
   - Consider resizing images before processing

4. **Verify file path:**
   ```bash
   ls -la /path/to/image.jpg
   file /path/to/image.jpg  # Check actual file type
   ```

---

### Memory Issues

**Error:** Out of memory during processing

**Solutions:**
1. **Process smaller batches:**
   ```env
   BATCH_SIZE=1
   MAX_WORKERS=1
   ```

2. **Use CPU instead of GPU:**
   ```env
   DEVICE=cpu
   ```

3. **Increase system memory or swap:**
   ```bash
   # Check memory usage
   free -h
   top
   ```

4. **Process images individually:**
   ```bash
   image-context-extractor process-image image1.jpg
   image-context-extractor process-image image2.jpg
   ```

---

### Import Errors

**Error:** Module import failures

**Solutions:**
1. **Install in development mode:**
   ```bash
   pip install -e .
   ```

2. **Check Python path:**
   ```bash
   export PYTHONPATH=/path/to/image-context-vectorization/src:$PYTHONPATH
   ```

3. **Virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

### WebSocket Connection Issues

**Error:** WebSocket connections fail or disconnect

**Solutions:**
1. **Check firewall settings:**
   ```bash
   # Allow port 8000
   sudo ufw allow 8000
   ```

2. **Use different WebSocket URL:**
   ```javascript
   const ws = new WebSocket('ws://127.0.0.1:8000/ws');
   ```

3. **Check proxy settings:**
   - Some proxies block WebSocket connections
   - Try direct connection without proxy

---

### Performance Issues

**Error:** Slow processing or high CPU usage

**Solutions:**
1. **Use GPU acceleration:**
   ```env
   DEVICE=cuda
   ```

2. **Optimize model loading:**
   ```env
   USE_LOCAL_FILES_ONLY=true
   ```

3. **Process in smaller batches:**
   ```env
   BATCH_SIZE=5
   ```

4. **Monitor system resources:**
   ```bash
   htop
   nvidia-smi  # For GPU monitoring
   ```

---

### Configuration Issues

**Error:** Configuration not loading or incorrect settings

**Solutions:**
1. **Check .env file location:**
   ```bash
   ls -la .env
   cat .env
   ```

2. **Verify environment variables:**
   ```bash
   env | grep DEVICE
   env | grep DB_PATH
   ```

3. **Use absolute paths:**
   ```env
   DB_PATH=/absolute/path/to/db
   LOCAL_BLIP_MODEL_PATH=/absolute/path/to/model
   ```

4. **Check file permissions:**
   ```bash
   chmod 644 .env
   ```

---

### Logging Issues

**Error:** Logs not appearing or too verbose

**Solutions:**
1. **Set log level:**
   ```env
   LOG_LEVEL=INFO
   ```

2. **Check log file permissions:**
   ```bash
   touch image_context_extraction.log
   chmod 644 image_context_extraction.log
   ```

3. **Disable verbose logging:**
   ```python
   import logging
   logging.getLogger('transformers').setLevel(logging.WARNING)
   logging.getLogger('chromadb').setLevel(logging.WARNING)
   ```

---

## Getting Help

If you continue to experience issues:

1. **Check the logs:**
   ```bash
   tail -f image_context_extraction.log
   ```

2. **Run with debug logging:**
   ```bash
   LOG_LEVEL=DEBUG python main.py
   ```

3. **Test individual components:**
   ```bash
   # Test database
   python -c "from src.image_context_extractor.database.vector_db import VectorDatabase; from src.image_context_extractor.config.settings import DatabaseConfig; db = VectorDatabase(DatabaseConfig()); print('Database OK')"
   
   # Test models
   python -c "from src.image_context_extractor.models.model_manager import ModelManager; from src.image_context_extractor.config.settings import ModelConfig; mm = ModelManager(ModelConfig()); print('Models OK')"
   ```

4. **Check system requirements:**
   - Python 3.8+
   - Sufficient RAM (4GB+ recommended)
   - Disk space for models and database
   - CUDA (optional, for GPU acceleration)

5. **Create a minimal test case:**
   ```python
   from src.image_context_extractor import ImageContextExtractor, Config
   config = Config()
   extractor = ImageContextExtractor(config)
   print("Basic initialization successful")
   ```

---

## Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEVICE` | Processing device | `cpu` | `cuda` |
| `DB_PATH` | Database path | `./image_vector_db` | `/data/db` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `ANONYMIZED_TELEMETRY` | ChromaDB telemetry | `False` | `False` |
| `USE_LOCAL_FILES_ONLY` | Force local models | `false` | `true` |
| `BATCH_SIZE` | Processing batch size | `10` | `5` |

See `.env.example` for a complete list of configuration options.