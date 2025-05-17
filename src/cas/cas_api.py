"""
Content-Aware Storage (CAS) API for Semantic OS.

This module provides a unified interface for interacting with the Content-Aware Storage system.
It integrates the file indexer, metadata store, and semantic index components.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import threading
import time

from .file_indexer import FileIndexer
from .metadata_store import MetadataStore
from .semantic_index import SemanticIndex


class ContentAwareStorage:
    """
    Unified API for the Content-Aware Storage system.
    
    This class integrates the file indexer, metadata store, and semantic index components
    to provide a comprehensive interface for content-aware file operations.
    """
    
    def __init__(self, base_dirs: List[str], storage_dir: str):
        """
        Initialize the Content-Aware Storage system.
        
        Args:
            base_dirs: List of directory paths to monitor and index
            storage_dir: Directory to store metadata and index files
        """
        self.base_dirs = [Path(d).expanduser().absolute() for d in base_dirs]
        self.storage_dir = Path(storage_dir).expanduser().absolute()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.metadata_store = MetadataStore(str(self.storage_dir / "metadata.db"))
        self.semantic_index = SemanticIndex(str(self.storage_dir / "index"))
        self.file_indexer = FileIndexer(base_dirs, self.metadata_store)
        
        # Set up synchronization
        self.lock = threading.RLock()
        self._sync_thread = None
        self._stop_sync = threading.Event()
    
    def start(self):
        """Start the Content-Aware Storage system."""
        # Start file monitoring
        self.file_indexer.start_monitoring()
        
        # Start background synchronization
        self._stop_sync.clear()
        self._sync_thread = threading.Thread(target=self._sync_loop)
        self._sync_thread.daemon = True
        self._sync_thread.start()
        
        # Perform initial indexing
        self._initial_indexing()
    
    def stop(self):
        """Stop the Content-Aware Storage system."""
        # Stop file monitoring
        self.file_indexer.stop_monitoring()
        
        # Stop background synchronization
        if self._sync_thread and self._sync_thread.is_alive():
            self._stop_sync.set()
            self._sync_thread.join(timeout=5.0)
    
    def _initial_indexing(self):
        """Perform initial indexing of all monitored directories."""
        for directory in self.base_dirs:
            self.file_indexer.index_directory(str(directory), recursive=True)
    
    def _sync_loop(self):
        """Background thread for synchronizing metadata store with semantic index."""
        while not self._stop_sync.is_set():
            try:
                # Get all files from metadata store
                all_files = self.metadata_store.get_all_files()
                
                # Update semantic index
                for file_data in all_files:
                    self.semantic_index.add_document(file_data)
                
                # Sleep for a while
                for _ in range(60):  # Check stop flag every second
                    if self._stop_sync.is_set():
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"Error in sync loop: {e}")
                time.sleep(10)  # Sleep on error
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for files matching the given query.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching file data dictionaries
        """
        return self.semantic_index.search(query, limit=limit)
    
    def advanced_search(self, criteria: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        """
        Perform an advanced search with multiple criteria.
        
        Args:
            criteria: Dictionary of search criteria
            limit: Maximum number of results to return
            
        Returns:
            List of matching file data dictionaries
        """
        return self.semantic_index.advanced_search(criteria, limit=limit)
    
    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of file metadata or None if not found
        """
        file_data = self.metadata_store.get_file_data(file_path)
        if file_data:
            return file_data.get('metadata', {})
        return None
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get the extracted content of a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content or None if not found
        """
        file_data = self.metadata_store.get_file_data(file_path)
        if file_data:
            return file_data.get('content', '')
        return None
    
    def get_related_files(self, file_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find files related to the given file based on content similarity.
        
        Args:
            file_path: Path to the reference file
            limit: Maximum number of related files to return
            
        Returns:
            List of related file data dictionaries
        """
        # Get content of the reference file
        content = self.get_file_content(file_path)
        if not content:
            return []
        
        # Use the content as a search query
        # This is a simple approach; more sophisticated similarity measures could be used
        return self.search(content, limit=limit)
    
    def tag_file(self, file_path: str, tags: List[str]) -> bool:
        """
        Add tags to a file.
        
        Args:
            file_path: Path to the file
            tags: List of tags to add
            
        Returns:
            True if successful, False otherwise
        """
        file_data = self.metadata_store.get_file_data(file_path)
        if not file_data:
            return False
        
        # Update metadata with tags
        metadata = file_data.get('metadata', {})
        if isinstance(metadata, str):
            import json
            metadata = json.loads(metadata)
        
        existing_tags = metadata.get('tags', [])
        if isinstance(existing_tags, str):
            existing_tags = existing_tags.split(',')
        
        # Combine and deduplicate tags
        all_tags = list(set(existing_tags + tags))
        metadata['tags'] = all_tags
        
        # Update file data
        file_data['metadata'] = metadata
        
        # Store updated data
        success = self.metadata_store.store_file_data(
            file_path, 
            file_data.get('content', ''), 
            metadata
        )
        
        # Update index
        if success:
            self.semantic_index.add_document(file_data)
        
        return success
    
    def organize_by_topic(self, topic: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize files by a specific topic or category.
        
        Args:
            topic: Topic or category to organize by
            
        Returns:
            Dictionary mapping subtopics to lists of file data
        """
        # Search for files related to the topic
        files = self.search(topic, limit=100)
        
        # Group files by potential subtopics
        # This is a placeholder implementation; more sophisticated clustering could be used
        subtopics = {}
        for file in files:
            metadata = file.get('metadata', {})
            if isinstance(metadata, str):
                import json
                metadata = json.loads(metadata)
            
            # Use file extension as a simple subtopic
            extension = file.get('extension', '').lstrip('.')
            if not extension:
                extension = 'unknown'
            
            if extension not in subtopics:
                subtopics[extension] = []
            
            subtopics[extension].append(file)
        
        return subtopics
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the indexed files.
        
        Returns:
            Dictionary of statistics
        """
        all_files = self.metadata_store.get_all_files()
        
        # Count files by extension
        extensions = {}
        total_size = 0
        
        for file in all_files:
            ext = file.get('extension', '').lower()
            if ext not in extensions:
                extensions[ext] = 0
            extensions[ext] += 1
            
            # Sum file sizes
            size = file.get('size', 0)
            if isinstance(size, (int, float)):
                total_size += size
        
        return {
            'total_files': len(all_files),
            'total_size': total_size,
            'extensions': extensions,
            'monitored_directories': [str(d) for d in self.base_dirs]
        }
    
    def reindex_file(self, file_path: str) -> bool:
        """
        Force reindexing of a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        return self.file_indexer.index_file(file_path)
    
    def reindex_directory(self, directory: str, recursive: bool = True) -> int:
        """
        Force reindexing of all files in a directory.
        
        Args:
            directory: Path to the directory
            recursive: Whether to index subdirectories
            
        Returns:
            Number of files successfully indexed
        """
        return self.file_indexer.index_directory(directory, recursive=recursive)
