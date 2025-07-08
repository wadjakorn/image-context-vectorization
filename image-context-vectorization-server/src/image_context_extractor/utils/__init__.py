"""Utility functions and helper classes."""

from .chromadb_utils import setup_chromadb, disable_chromadb_telemetry
from .logging_utils import setup_logging

# Ensure ChromaDB is configured on import
setup_chromadb()

__all__ = ["setup_logging", "setup_chromadb", "disable_chromadb_telemetry"]