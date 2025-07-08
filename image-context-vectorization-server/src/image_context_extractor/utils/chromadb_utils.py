"""
Utilities for ChromaDB configuration and telemetry management.
"""
import os
import logging

logger = logging.getLogger(__name__)


def disable_chromadb_telemetry():
    """
    Disable ChromaDB telemetry to prevent capture() errors.
    
    ChromaDB has telemetry enabled by default which can cause errors like:
    "Failed to send telemetry event ClientStartEvent: capture() takes 1 positional 
    argument but 3 were given"
    
    This function sets the necessary environment variables to disable telemetry.
    """
    telemetry_vars = {
        "ANONYMIZED_TELEMETRY": "False",
        "CHROMA_CLIENT_DISABLE_TELEMETRY": "True",
        "CHROMA_SERVER_TELEMETRY_IMPL": "None"
    }
    
    for var, value in telemetry_vars.items():
        if var not in os.environ:
            os.environ[var] = value
            logger.debug(f"Set {var}={value} to disable ChromaDB telemetry")


def configure_chromadb_logging():
    """Configure ChromaDB logging to reduce noise."""
    # Suppress ChromaDB's verbose logging
    chromadb_loggers = [
        "chromadb",
        "chromadb.telemetry",
        "chromadb.db.clickhouse",
        "chromadb.segment.impl.vector.local_hnsw",
    ]
    
    for logger_name in chromadb_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def setup_chromadb():
    """Setup ChromaDB with optimal configuration for this application."""
    disable_chromadb_telemetry()
    configure_chromadb_logging()
    logger.info("ChromaDB configured with telemetry disabled and logging optimized")


# Call setup on import to ensure it's always applied
setup_chromadb()