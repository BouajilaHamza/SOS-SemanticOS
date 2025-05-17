"""
Content-Aware Storage (CAS) module for Semantic OS.

This module implements a semantic file system layer that organizes and retrieves
files based on content and context rather than traditional hierarchical structures.
"""

from .file_indexer import FileIndexer
from .metadata_store import MetadataStore
from .semantic_index import SemanticIndex
from .cas_api import ContentAwareStorage

__all__ = ['FileIndexer', 'MetadataStore', 'SemanticIndex', 'ContentAwareStorage']
