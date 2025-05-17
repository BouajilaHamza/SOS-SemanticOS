"""
Metadata Store component for Content-Aware Storage.

This component maintains a database of file metadata and content information.
It provides efficient storage and retrieval mechanisms for file metadata.
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import threading


class MetadataStore:
    """
    Maintains a database of file metadata and content information.
    
    This class is responsible for:
    1. Storing extracted text and metadata
    2. Providing efficient retrieval of file information
    3. Supporting incremental updates to avoid reprocessing unchanged files
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the MetadataStore.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path).expanduser().absolute()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self._init_database()
        
    def _init_database(self):
        """Initialize the database schema if it doesn't exist."""
        with self.lock:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Create files table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    extension TEXT,
                    size INTEGER,
                    created TEXT,
                    modified TEXT,
                    accessed TEXT,
                    content TEXT,
                    metadata TEXT,
                    last_indexed TEXT
                )
                ''')
                
                # Create index on path
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)')
                
                # Create index on filename
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename)')
                
                # Create index on extension
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension)')
                
                conn.commit()
    
    def store_file_data(self, file_path: str, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Store or update file content and metadata.
        
        Args:
            file_path: Path to the file
            content: Extracted text content
            metadata: Dictionary of metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    
                    # Check if file already exists in database
                    cursor.execute('SELECT id FROM files WHERE path = ?', (file_path,))
                    result = cursor.fetchone()
                    
                    # Convert metadata to JSON string
                    metadata_json = json.dumps(metadata)
                    
                    # Get current timestamp
                    import datetime
                    timestamp = datetime.datetime.now().isoformat()
                    
                    if result:
                        # Update existing record
                        cursor.execute('''
                        UPDATE files SET
                            filename = ?,
                            extension = ?,
                            size = ?,
                            created = ?,
                            modified = ?,
                            accessed = ?,
                            content = ?,
                            metadata = ?,
                            last_indexed = ?
                        WHERE path = ?
                        ''', (
                            metadata.get('filename', os.path.basename(file_path)),
                            metadata.get('extension', ''),
                            metadata.get('size', 0),
                            metadata.get('created', ''),
                            metadata.get('modified', ''),
                            metadata.get('accessed', ''),
                            content,
                            metadata_json,
                            timestamp,
                            file_path
                        ))
                    else:
                        # Insert new record
                        cursor.execute('''
                        INSERT INTO files (
                            path, filename, extension, size, created, modified, 
                            accessed, content, metadata, last_indexed
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            file_path,
                            metadata.get('filename', os.path.basename(file_path)),
                            metadata.get('extension', ''),
                            metadata.get('size', 0),
                            metadata.get('created', ''),
                            metadata.get('modified', ''),
                            metadata.get('accessed', ''),
                            content,
                            metadata_json,
                            timestamp
                        ))
                    
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Error storing file data for {file_path}: {e}")
            return False
    
    def remove_file_data(self, file_path: str) -> bool:
        """
        Remove file data from the store.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM files WHERE path = ?', (file_path,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing file data for {file_path}: {e}")
            return False
    
    def get_file_data(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve file data from the store.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file data or None if not found
        """
        try:
            with self.lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('''
                    SELECT * FROM files WHERE path = ?
                    ''', (file_path,))
                    row = cursor.fetchone()
                    
                    if row:
                        result = dict(row)
                        # Parse metadata JSON
                        if 'metadata' in result and result['metadata']:
                            result['metadata'] = json.loads(result['metadata'])
                        return result
                    return None
        except Exception as e:
            print(f"Error retrieving file data for {file_path}: {e}")
            return None
    
    def search_files(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for files matching the given criteria.
        
        Args:
            query: Dictionary of search criteria
            
        Returns:
            List of matching file data dictionaries
        """
        try:
            conditions = []
            params = []
            
            # Build query conditions
            for key, value in query.items():
                if key == 'extension':
                    conditions.append('extension = ?')
                    params.append(value)
                elif key == 'filename':
                    conditions.append('filename LIKE ?')
                    params.append(f'%{value}%')
                elif key == 'size_min':
                    conditions.append('size >= ?')
                    params.append(value)
                elif key == 'size_max':
                    conditions.append('size <= ?')
                    params.append(value)
                elif key == 'modified_after':
                    conditions.append('modified >= ?')
                    params.append(value)
                elif key == 'modified_before':
                    conditions.append('modified <= ?')
                    params.append(value)
                elif key == 'content':
                    conditions.append('content LIKE ?')
                    params.append(f'%{value}%')
            
            # Construct the SQL query
            sql = 'SELECT * FROM files'
            if conditions:
                sql += ' WHERE ' + ' AND '.join(conditions)
            
            with self.lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        result = dict(row)
                        # Parse metadata JSON
                        if 'metadata' in result and result['metadata']:
                            result['metadata'] = json.loads(result['metadata'])
                        results.append(result)
                    
                    return results
        except Exception as e:
            print(f"Error searching files: {e}")
            return []
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """
        Retrieve all files in the store.
        
        Returns:
            List of all file data dictionaries
        """
        try:
            with self.lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM files')
                    rows = cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        result = dict(row)
                        # Parse metadata JSON
                        if 'metadata' in result and result['metadata']:
                            result['metadata'] = json.loads(result['metadata'])
                        results.append(result)
                    
                    return results
        except Exception as e:
            print(f"Error retrieving all files: {e}")
            return []
    
    def get_file_count(self) -> int:
        """
        Get the total number of files in the store.
        
        Returns:
            Number of files
        """
        try:
            with self.lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM files')
                    return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting file count: {e}")
            return 0
