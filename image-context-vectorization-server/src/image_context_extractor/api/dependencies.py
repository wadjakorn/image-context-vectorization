"""
Shared dependencies for FastAPI routes.
"""
from typing import Optional
from ..core.extractor import ImageContextExtractor
from ..config.settings import get_config

# Global extractor instance
_global_extractor: Optional[ImageContextExtractor] = None


def get_extractor() -> ImageContextExtractor:
    """Get the global extractor instance, creating it if needed."""
    global _global_extractor
    if _global_extractor is None:
        config = get_config()
        # Skip compatibility check during API dependency injection to prevent startup blocking
        _global_extractor = ImageContextExtractor(config, skip_compatibility_check=True)
    return _global_extractor


def get_extractor_lazy() -> ImageContextExtractor:
    """Get extractor instance without triggering model loading."""
    return get_extractor()