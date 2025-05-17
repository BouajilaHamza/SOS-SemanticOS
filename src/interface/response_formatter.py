"""
Response Formatter component for Natural Language Interface.

This component formats system responses for display to the user.
It converts internal response formats to user-friendly presentations.
"""

from typing import Dict, List, Any, Optional, Union
import re
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from rich.console import Console


class ResponseFormatter:
    """
    Formats system responses for display to the user.
    
    This class is responsible for:
    1. Converting internal response formats to user-friendly presentations
    2. Implementing different display modes for various response types
    3. Providing progress indicators for long-running operations
    """
    
    def __init__(self):
        """Initialize the ResponseFormatter."""
        self.console = Console()
        self.formatters = {
            "text": self._format_text,
            "code": self._format_code,
            "file_list": self._format_file_list,
            "search_results": self._format_search_results,
            "error": self._format_error,
            "system": self._format_system
        }
    
    def format_response(self, response: Union[str, Dict[str, Any]], response_type: str = "text") -> str:
        """
        Format a response for display.
        
        Args:
            response: Response content (string or dictionary)
            response_type: Type of response to format
            
        Returns:
            Formatted response string
        """
        # Get the appropriate formatter
        formatter = self.formatters.get(response_type, self._format_text)
        
        # Format the response
        return formatter(response)
    
    def _format_text(self, response: Union[str, Dict[str, Any]]) -> str:
        """
        Format a text response.
        
        Args:
            response: Text response
            
        Returns:
            Formatted text
        """
        if isinstance(response, dict):
            if "text" in response:
                return response["text"]
            else:
                return str(response)
        return str(response)
    
    def _format_code(self, response: Union[str, Dict[str, Any]]) -> str:
        """
        Format a code response.
        
        Args:
            response: Code response
            
        Returns:
            Formatted code block
        """
        if isinstance(response, dict):
            code = response.get("code", "")
            language = response.get("language", "python")
        else:
            code = str(response)
            language = "python"
        
        # Wrap in markdown code block
        return f"```{language}\n{code}\n```"
    
    def _format_file_list(self, response: Union[List[Dict[str, Any]], Dict[str, Any]]) -> str:
        """
        Format a file list response.
        
        Args:
            response: File list response
            
        Returns:
            Formatted file list
        """
        if isinstance(response, dict):
            files = response.get("files", [])
        else:
            files = response
        
        if not files:
            return "No files found."
        
        result = "Found the following files:\n\n"
        
        for i, file in enumerate(files, 1):
            if isinstance(file, dict):
                filename = file.get("filename", "Unknown")
                path = file.get("path", "")
                size = file.get("size", "")
                modified = file.get("modified", "")
                
                result += f"{i}. **{filename}**\n"
                if path:
                    result += f"   Path: {path}\n"
                if size:
                    result += f"   Size: {self._format_size(size)}\n"
                if modified:
                    result += f"   Modified: {modified}\n"
            else:
                result += f"{i}. {file}\n"
            
            result += "\n"
        
        return result
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _format_search_results(self, response: Union[List[Dict[str, Any]], Dict[str, Any]]) -> str:
        """
        Format search results.
        
        Args:
            response: Search results
            
        Returns:
            Formatted search results
        """
        if isinstance(response, dict):
            results = response.get("results", [])
            query = response.get("query", "")
        else:
            results = response
            query = ""
        
        if not results:
            return "No results found."
        
        if query:
            result = f"Search results for '{query}':\n\n"
        else:
            result = "Search results:\n\n"
        
        for i, item in enumerate(results, 1):
            if isinstance(item, dict):
                filename = item.get("filename", "Unknown")
                path = item.get("path", "")
                snippet = item.get("snippet", "")
                
                result += f"{i}. **{filename}**\n"
                if path:
                    result += f"   Path: {path}\n"
                if snippet:
                    result += f"   Snippet: \"{snippet}\"\n"
            else:
                result += f"{i}. {item}\n"
            
            result += "\n"
        
        return result
    
    def _format_error(self, response: Union[str, Dict[str, Any]]) -> str:
        """
        Format an error response.
        
        Args:
            response: Error response
            
        Returns:
            Formatted error message
        """
        if isinstance(response, dict):
            error_message = response.get("message", "An unknown error occurred.")
            error_type = response.get("type", "Error")
        else:
            error_message = str(response)
            error_type = "Error"
        
        return f"**{error_type}**: {error_message}"
    
    def _format_system(self, response: Union[str, Dict[str, Any]]) -> str:
        """
        Format a system message.
        
        Args:
            response: System message
            
        Returns:
            Formatted system message
        """
        if isinstance(response, dict):
            message = response.get("message", "")
        else:
            message = str(response)
        
        return f"*{message}*"
    
    def format_progress(self, operation: str, progress: float, status: str = "") -> str:
        """
        Format a progress indicator.
        
        Args:
            operation: Operation in progress
            progress: Progress value (0.0 to 1.0)
            status: Status message
            
        Returns:
            Formatted progress indicator
        """
        progress_int = int(progress * 20)
        bar = "█" * progress_int + "░" * (20 - progress_int)
        percentage = int(progress * 100)
        
        result = f"{operation}: [{bar}] {percentage}%"
        if status:
            result += f" - {status}"
            
        return result
    
    def highlight_matches(self, text: str, query: str) -> str:
        """
        Highlight query matches in text.
        
        Args:
            text: Text to highlight in
            query: Query to highlight
            
        Returns:
            Text with highlighted matches
        """
        if not query:
            return text
            
        # Escape regex special characters in query
        escaped_query = re.escape(query)
        
        # Replace matches with highlighted version
        return re.sub(
            f"({escaped_query})",
            r"**\1**",
            text,
            flags=re.IGNORECASE
        )
