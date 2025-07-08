import logging
import os
from typing import Optional


def setup_logging(level=logging.INFO, log_file: Optional[str] = None, format_string: Optional[str] = None):
    """Setup logging configuration"""
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    
    if log_file is None:
        log_file = os.getenv('LOG_FILE', 'image_context_extraction.log')
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers
    )
    
    # Set specific logger levels if needed
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)