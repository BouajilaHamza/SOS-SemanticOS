"""
File Indexer component for Content-Aware Storage.

This component monitors the file system for changes and extracts metadata from files.
It implements file system watchers and supports various file types through a plugin-based
extractor system.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .extractors import BaseExtractor, TextExtractor, ImageExtractor, PDFExtractor


class FileIndexer:
    """
    Monitors the file system for changes and extracts metadata from files.
    
    This class is responsible for:
    1. Detecting file creation, modification, and deletion events
    2. Extracting content and metadata from files
    3. Notifying the metadata store of changes
    """
    
    def __init__(self, base_dirs: List[str], metadata_store: Any):
        """
        Initialize the FileIndexer.
        
        Args:
            base_dirs: List of directory paths to monitor
            metadata_store: Reference to the metadata store for storing extracted data
        """
        self.base_dirs = [Path(d).expanduser().absolute() for d in base_dirs]
        self.metadata_store = metadata_store
        self.observer = Observer()
        self.extractors: Dict[str, BaseExtractor] = {}
        self.watched_paths: Set[str] = set()
        self._register_default_extractors()
        
    def _register_default_extractors(self):
        """Register the default set of content extractors."""
        self.register_extractor(TextExtractor(), ['.txt', '.md', '.py', '.js', '.html', '.css', '.json'])
        self.register_extractor(PDFExtractor(), ['.pdf'])
        self.register_extractor(ImageExtractor(), ['.jpg', '.jpeg', '.png', '.gif', '.bmp'])
        
    def register_extractor(self, extractor: BaseExtractor, extensions: List[str]):
        """
        Register a content extractor for specific file extensions.
        
        Args:
            extractor: The extractor instance
            extensions: List of file extensions this extractor handles
        """
        for ext in extensions:
            self.extractors[ext.lower()] = extractor
            
    def get_extractor_for_file(self, file_path: str) -> Optional[BaseExtractor]:
        """
        Get the appropriate extractor for a given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The appropriate extractor or None if no suitable extractor is found
        """
        ext = os.path.splitext(file_path)[1].lower()
        return self.extractors.get(ext)
    
    def start_monitoring(self):
        """Start monitoring the file system for changes."""
        event_handler = FileSystemChangeHandler(self)
        for directory in self.base_dirs:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            self.observer.schedule(event_handler, str(directory), recursive=True)
            self.watched_paths.add(str(directory))
        self.observer.start()
        
    def stop_monitoring(self):
        """Stop monitoring the file system."""
        self.observer.stop()
        self.observer.join()
        
    def index_file(self, file_path: str) -> bool:
        """
        Extract content and metadata from a file and store it.
        
        Args:
            file_path: Path to the file to index
            
        Returns:
            True if indexing was successful, False otherwise
        """
        try:
            extractor = self.get_extractor_for_file(file_path)
            if extractor is None:
                return False
                
            metadata = extractor.extract_metadata(file_path)
            content = extractor.extract_content(file_path)
            
            if metadata and content:
                self.metadata_store.store_file_data(file_path, content, metadata)
                return True
            return False
        except Exception as e:
            print(f"Error indexing file {file_path}: {e}")
            return False
            
    def remove_file_index(self, file_path: str) -> bool:
        """
        Remove a file from the index.
        
        Args:
            file_path: Path to the file to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        try:
            self.metadata_store.remove_file_data(file_path)
            return True
        except Exception as e:
            print(f"Error removing file {file_path} from index: {e}")
            return False
            
    def index_directory(self, directory: str, recursive: bool = True) -> int:
        """
        Index all files in a directory.
        
        Args:
            directory: Path to the directory to index
            recursive: Whether to index subdirectories
            
        Returns:
            Number of files successfully indexed
        """
        indexed_count = 0
        dir_path = Path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return 0
            
        pattern = '**/*' if recursive else '*'
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                if self.index_file(str(file_path)):
                    indexed_count += 1
                    
        return indexed_count


class FileSystemChangeHandler(FileSystemEventHandler):
    """
    Handler for file system events that triggers indexing actions.
    """
    
    def __init__(self, indexer: FileIndexer):
        """
        Initialize the handler.
        
        Args:
            indexer: Reference to the FileIndexer
        """
        self.indexer = indexer
        
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if not event.is_directory:
            self.indexer.index_file(event.src_path)
            
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if not event.is_directory:
            self.indexer.index_file(event.src_path)
            
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if not event.is_directory:
            self.indexer.remove_file_index(event.src_path)
            
    def on_moved(self, event: FileSystemEvent):
        """Handle file move events."""
        if not event.is_directory:
            self.indexer.remove_file_index(event.src_path)
            self.indexer.index_file(event.dest_path)
