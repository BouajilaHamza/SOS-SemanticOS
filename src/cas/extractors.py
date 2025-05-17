"""
Content extractors for different file types.

This module provides a plugin-based system for extracting content and metadata
from various file types. Each extractor implements a common interface and handles
specific file formats.
"""

import os
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseExtractor(ABC):
    """
    Base class for all content extractors.
    
    This abstract class defines the interface that all extractors must implement.
    """
    
    @abstractmethod
    def extract_content(self, file_path: str) -> str:
        """
        Extract the textual content from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content
        """
        pass
    
    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of metadata
        """
        pass
    
    def get_basic_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic file metadata common to all file types.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of basic metadata
        """
        try:
            stat = os.stat(file_path)
            return {
                'filename': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'extension': os.path.splitext(file_path)[1].lower(),
            }
        except Exception as e:
            print(f"Error getting basic metadata for {file_path}: {e}")
            return {}


class TextExtractor(BaseExtractor):
    """
    Extractor for plain text files.
    
    Handles various text-based formats including source code, markdown, and plain text.
    """
    
    def extract_content(self, file_path: str) -> str:
        """
        Extract text content from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Text content of the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            print(f"Error extracting content from {file_path}: {e}")
            return ""
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary of metadata
        """
        metadata = self.get_basic_metadata(file_path)
        
        try:
            content = self.extract_content(file_path)
            
            # Count lines, words, and characters
            lines = content.splitlines()
            words = re.findall(r'\b\w+\b', content)
            
            metadata.update({
                'line_count': len(lines),
                'word_count': len(words),
                'char_count': len(content),
            })
            
            # Try to detect language or file type based on extension and content
            ext = metadata.get('extension', '')
            if ext in ['.py']:
                metadata['language'] = 'python'
            elif ext in ['.js']:
                metadata['language'] = 'javascript'
            elif ext in ['.html', '.htm']:
                metadata['language'] = 'html'
            elif ext in ['.css']:
                metadata['language'] = 'css'
            elif ext in ['.md']:
                metadata['language'] = 'markdown'
            elif ext in ['.json']:
                metadata['language'] = 'json'
            else:
                metadata['language'] = 'text'
                
            # Extract potential title from first line
            if lines and lines[0].strip():
                metadata['title'] = lines[0].strip()
                
            return metadata
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return metadata


class PDFExtractor(BaseExtractor):
    """
    Extractor for PDF files.
    
    Uses external libraries to extract text and metadata from PDF documents.
    """
    
    def extract_content(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            # This is a placeholder. In a real implementation, we would use
            # a library like PyPDF2, pdfminer, or pdf2text to extract content.
            # For the PoC, we'll simulate PDF extraction.
            return f"[PDF Content from {os.path.basename(file_path)}]"
        except Exception as e:
            print(f"Error extracting content from PDF {file_path}: {e}")
            return ""
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary of metadata
        """
        metadata = self.get_basic_metadata(file_path)
        
        try:
            # This is a placeholder. In a real implementation, we would extract
            # PDF-specific metadata like author, title, creation date, etc.
            metadata.update({
                'document_type': 'pdf',
                'title': os.path.splitext(os.path.basename(file_path))[0],
            })
            return metadata
        except Exception as e:
            print(f"Error extracting metadata from PDF {file_path}: {e}")
            return metadata


class ImageExtractor(BaseExtractor):
    """
    Extractor for image files.
    
    Extracts metadata and generates text descriptions for image files.
    """
    
    def extract_content(self, file_path: str) -> str:
        """
        Extract "content" from an image file.
        
        For images, content is a textual description or placeholder.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Textual representation of the image
        """
        try:
            # This is a placeholder. In a real implementation, we might use
            # image recognition or OCR to extract text from images.
            return f"[Image: {os.path.basename(file_path)}]"
        except Exception as e:
            print(f"Error extracting content from image {file_path}: {e}")
            return ""
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from an image file.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary of metadata
        """
        metadata = self.get_basic_metadata(file_path)
        
        try:
            # This is a placeholder. In a real implementation, we would extract
            # image-specific metadata like dimensions, color depth, EXIF data, etc.
            metadata.update({
                'media_type': 'image',
                'format': metadata.get('extension', '').lstrip('.'),
            })
            return metadata
        except Exception as e:
            print(f"Error extracting metadata from image {file_path}: {e}")
            return metadata
