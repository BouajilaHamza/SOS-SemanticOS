"""
Semantic Index component for Content-Aware Storage.

This component provides search capabilities based on the Whoosh library.
It creates and maintains inverted indices for efficient text search.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union
import threading
import shutil

from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED, DATETIME
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import Term, And, Or
from whoosh.analysis import StemmingAnalyzer


class SemanticIndex:
    """
    Provides search capabilities based on the Whoosh library.
    
    This class is responsible for:
    1. Creating and maintaining inverted indices for efficient text search
    2. Supporting complex queries including fuzzy matching and semantic similarity
    3. Implementing ranking algorithms to prioritize relevant results
    """
    
    def __init__(self, index_dir: str):
        """
        Initialize the SemanticIndex.
        
        Args:
            index_dir: Directory to store the Whoosh index
        """
        self.index_dir = Path(index_dir).expanduser().absolute()
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.schema = Schema(
            path=ID(stored=True, unique=True),
            filename=TEXT(stored=True),
            content=TEXT(analyzer=StemmingAnalyzer()),
            extension=ID(stored=True),
            tags=KEYWORD(stored=True, commas=True, lowercase=True),
            created=DATETIME(stored=True),
            modified=DATETIME(stored=True),
            metadata=STORED
        )
        self._init_index()
        
    def _init_index(self):
        """Initialize the Whoosh index if it doesn't exist."""
        with self.lock:
            if not exists_in(str(self.index_dir)):
                create_in(str(self.index_dir), self.schema)
    
    def add_document(self, file_data: Dict[str, Any]) -> bool:
        """
        Add or update a document in the index.
        
        Args:
            file_data: Dictionary containing file data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                ix = open_dir(str(self.index_dir))
                writer = ix.writer()
                
                # Extract required fields
                path = file_data.get('path', '')
                filename = file_data.get('filename', os.path.basename(path))
                content = file_data.get('content', '')
                extension = file_data.get('extension', '')
                
                # Extract metadata
                metadata = file_data.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    metadata = json.loads(metadata)
                
                # Extract dates
                from datetime import datetime
                created = metadata.get('created', '')
                modified = metadata.get('modified', '')
                
                if created and isinstance(created, str):
                    try:
                        created = datetime.fromisoformat(created)
                    except ValueError:
                        created = datetime.now()
                
                if modified and isinstance(modified, str):
                    try:
                        modified = datetime.fromisoformat(modified)
                    except ValueError:
                        modified = datetime.now()
                
                # Generate tags from metadata
                tags = []
                for key, value in metadata.items():
                    if isinstance(value, str) and key not in ['created', 'modified', 'accessed']:
                        tags.append(value.lower())
                
                # Add document to index
                writer.update_document(
                    path=path,
                    filename=filename,
                    content=content,
                    extension=extension,
                    tags=','.join(tags),
                    created=created,
                    modified=modified,
                    metadata=metadata
                )
                
                writer.commit()
                return True
        except Exception as e:
            print(f"Error adding document to index: {e}")
            return False
    
    def remove_document(self, file_path: str) -> bool:
        """
        Remove a document from the index.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                ix = open_dir(str(self.index_dir))
                writer = ix.writer()
                writer.delete_by_term('path', file_path)
                writer.commit()
                return True
        except Exception as e:
            print(f"Error removing document from index: {e}")
            return False
    
    def search(self, query_str: str, fields: Optional[List[str]] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search the index for documents matching the query.
        
        Args:
            query_str: Search query string
            fields: List of fields to search (defaults to content and filename)
            limit: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        try:
            if not fields:
                fields = ['content', 'filename', 'tags']
                
            with self.lock:
                ix = open_dir(str(self.index_dir))
                with ix.searcher() as searcher:
                    parser = MultifieldParser(fields, ix.schema)
                    query = parser.parse(query_str)
                    results = searcher.search(query, limit=limit)
                    
                    return [dict(result) for result in results]
        except Exception as e:
            print(f"Error searching index: {e}")
            return []
    
    def advanced_search(self, criteria: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        """
        Perform an advanced search with multiple criteria.
        
        Args:
            criteria: Dictionary of search criteria
            limit: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        try:
            with self.lock:
                ix = open_dir(str(self.index_dir))
                with ix.searcher() as searcher:
                    queries = []
                    
                    # Process each criterion
                    for field, value in criteria.items():
                        if field == 'content' or field == 'filename':
                            parser = QueryParser(field, ix.schema)
                            queries.append(parser.parse(value))
                        elif field == 'extension':
                            queries.append(Term('extension', value))
                        elif field == 'tags':
                            parser = QueryParser('tags', ix.schema)
                            queries.append(parser.parse(value))
                    
                    # Combine queries with AND
                    if queries:
                        query = And(queries)
                        results = searcher.search(query, limit=limit)
                        return [dict(result) for result in results]
                    return []
        except Exception as e:
            print(f"Error performing advanced search: {e}")
            return []
    
    def rebuild_index(self, file_data_list: List[Dict[str, Any]]) -> bool:
        """
        Rebuild the entire index from a list of file data.
        
        Args:
            file_data_list: List of file data dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a temporary index directory
            temp_dir = self.index_dir.parent / f"{self.index_dir.name}_temp"
            if temp_dir.exists():
                shutil.rmtree(str(temp_dir))
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a new index in the temporary directory
            ix = create_in(str(temp_dir), self.schema)
            writer = ix.writer()
            
            # Add all documents to the new index
            for file_data in file_data_list:
                # Extract required fields
                path = file_data.get('path', '')
                filename = file_data.get('filename', os.path.basename(path))
                content = file_data.get('content', '')
                extension = file_data.get('extension', '')
                
                # Extract metadata
                metadata = file_data.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    metadata = json.loads(metadata)
                
                # Extract dates
                from datetime import datetime
                created = metadata.get('created', '')
                modified = metadata.get('modified', '')
                
                if created and isinstance(created, str):
                    try:
                        created = datetime.fromisoformat(created)
                    except ValueError:
                        created = datetime.now()
                
                if modified and isinstance(modified, str):
                    try:
                        modified = datetime.fromisoformat(modified)
                    except ValueError:
                        modified = datetime.now()
                
                # Generate tags from metadata
                tags = []
                for key, value in metadata.items():
                    if isinstance(value, str) and key not in ['created', 'modified', 'accessed']:
                        tags.append(value.lower())
                
                # Add document to index
                writer.add_document(
                    path=path,
                    filename=filename,
                    content=content,
                    extension=extension,
                    tags=','.join(tags),
                    created=created,
                    modified=modified,
                    metadata=metadata
                )
            
            writer.commit()
            
            # Replace the old index with the new one
            with self.lock:
                if self.index_dir.exists():
                    shutil.rmtree(str(self.index_dir))
                shutil.move(str(temp_dir), str(self.index_dir))
                
            return True
        except Exception as e:
            print(f"Error rebuilding index: {e}")
            return False
