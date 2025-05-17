"""
Command Processor component for Modular Command Processing.

This component defines the interface and lifecycle for command processors.
It implements a plugin architecture for adding new command processors.
"""

from typing import Dict, List, Any, Optional, Protocol, runtime_checkable
from abc import ABC, abstractmethod


@runtime_checkable
class CommandProcessor(Protocol):
    """Protocol defining the interface for command processors."""
    
    def process(self, command: str, intent_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Process a command.
        
        Args:
            command: Command text
            intent_data: Intent data extracted from the command
            context: Additional context for processing
            
        Returns:
            Processing result
        """
        ...


class BaseCommandProcessor(ABC):
    """
    Base class for command processors.
    
    This class provides a common foundation for command processors
    and implements the CommandProcessor protocol.
    """
    
    def __init__(self):
        """Initialize the command processor."""
        self.metadata = {
            'name': self.__class__.__name__,
            'description': self.__doc__ or "No description available",
            'capabilities': []
        }
    
    @abstractmethod
    def process(self, command: str, intent_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Process a command.
        
        Args:
            command: Command text
            intent_data: Intent data extracted from the command
            context: Additional context for processing
            
        Returns:
            Processing result
        """
        pass
    
    def can_process(self, intent: str) -> bool:
        """
        Check if this processor can handle a specific intent.
        
        Args:
            intent: Intent string
            
        Returns:
            True if this processor can handle the intent, False otherwise
        """
        return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this processor.
        
        Returns:
            Dictionary of metadata
        """
        return self.metadata.copy()
    
    def update_metadata(self, updates: Dict[str, Any]) -> None:
        """
        Update processor metadata.
        
        Args:
            updates: Dictionary of metadata updates
        """
        self.metadata.update(updates)


class FileOperationProcessor(BaseCommandProcessor):
    """Command processor for file operations."""
    
    def __init__(self, cas_service=None):
        """
        Initialize the file operation processor.
        
        Args:
            cas_service: Reference to the Content-Aware Storage service
        """
        super().__init__()
        self.cas_service = cas_service
        self.update_metadata({
            'name': 'FileOperationProcessor',
            'description': 'Handles file operations such as create, open, delete, and move',
            'capabilities': ['create_file', 'open_file', 'delete_file', 'move_file']
        })
    
    def can_process(self, intent: str) -> bool:
        """Check if this processor can handle a specific intent."""
        return intent in ['create_file', 'open_file', 'delete_file', 'move_file']
    
    def process(self, command: str, intent_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Process a file operation command."""
        intent = intent_data.get('intent', '')
        
        if not self.cas_service:
            return {
                'status': 'error',
                'message': 'Content-Aware Storage service not available'
            }
        
        if intent == 'create_file':
            # Extract file path and content from command or context
            # This is a simplified implementation
            return {
                'status': 'success',
                'message': 'File creation would be implemented here',
                'operation': 'create_file'
            }
        
        elif intent == 'open_file':
            # Extract file path from command or context
            # This is a simplified implementation
            return {
                'status': 'success',
                'message': 'File opening would be implemented here',
                'operation': 'open_file'
            }
        
        elif intent == 'delete_file':
            # Extract file path from command or context
            # This is a simplified implementation
            return {
                'status': 'success',
                'message': 'File deletion would be implemented here',
                'operation': 'delete_file'
            }
        
        elif intent == 'move_file':
            # Extract source and destination paths from command or context
            # This is a simplified implementation
            return {
                'status': 'success',
                'message': 'File moving would be implemented here',
                'operation': 'move_file'
            }
        
        return {
            'status': 'error',
            'message': f'Unsupported file operation: {intent}'
        }


class SearchProcessor(BaseCommandProcessor):
    """Command processor for search operations."""
    
    def __init__(self, cas_service=None):
        """
        Initialize the search processor.
        
        Args:
            cas_service: Reference to the Content-Aware Storage service
        """
        super().__init__()
        self.cas_service = cas_service
        self.update_metadata({
            'name': 'SearchProcessor',
            'description': 'Handles search operations for files and content',
            'capabilities': ['search_files', 'search_content']
        })
    
    def can_process(self, intent: str) -> bool:
        """Check if this processor can handle a specific intent."""
        return intent in ['search_files', 'search_content']
    
    def process(self, command: str, intent_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Process a search command."""
        intent = intent_data.get('intent', '')
        
        if not self.cas_service:
            return {
                'status': 'error',
                'message': 'Content-Aware Storage service not available'
            }
        
        # Extract search query from command
        # This is a simplified implementation
        query = command.lower()
        for prefix in ['find', 'search', 'look for', 'locate']:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
        
        if intent == 'search_files' or intent == 'search_content':
            try:
                # Perform search using CAS
                results = self.cas_service.search(query)
                
                return {
                    'status': 'success',
                    'message': f'Found {len(results)} results for "{query}"',
                    'operation': 'search',
                    'query': query,
                    'results': results
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Error during search: {str(e)}',
                    'operation': 'search'
                }
        
        return {
            'status': 'error',
            'message': f'Unsupported search operation: {intent}'
        }


class GeneralQueryProcessor(BaseCommandProcessor):
    """Command processor for general queries."""
    
    def __init__(self, llm_service=None):
        """
        Initialize the general query processor.
        
        Args:
            llm_service: Reference to the LLM service
        """
        super().__init__()
        self.llm_service = llm_service
        self.update_metadata({
            'name': 'GeneralQueryProcessor',
            'description': 'Handles general queries using the LLM',
            'capabilities': ['general_query']
        })
    
    def can_process(self, intent: str) -> bool:
        """Check if this processor can handle a specific intent."""
        return intent == 'general_query'
    
    def process(self, command: str, intent_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Process a general query."""
        if not self.llm_service:
            return {
                'status': 'error',
                'message': 'LLM service not available'
            }
        
        try:
            # Process query using LLM
            response = self.llm_service.process_query(command)
            
            return {
                'status': 'success',
                'message': response,
                'operation': 'general_query'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error processing query: {str(e)}',
                'operation': 'general_query'
            }


class SystemInfoProcessor(BaseCommandProcessor):
    """Command processor for system information queries."""
    
    def __init__(self, cas_service=None, llm_service=None):
        """
        Initialize the system info processor.
        
        Args:
            cas_service: Reference to the Content-Aware Storage service
            llm_service: Reference to the LLM service
        """
        super().__init__()
        self.cas_service = cas_service
        self.llm_service = llm_service
        self.update_metadata({
            'name': 'SystemInfoProcessor',
            'description': 'Provides information about the system',
            'capabilities': ['system_info']
        })
    
    def can_process(self, intent: str) -> bool:
        """Check if this processor can handle a specific intent."""
        return intent == 'system_info'
    
    def process(self, command: str, intent_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Process a system info command."""
        system_info = {
            'name': 'Semantic OS',
            'version': '0.1.0',
            'components': []
        }
        
        # Add CAS information if available
        if self.cas_service:
            try:
                cas_stats = self.cas_service.get_statistics()
                system_info['components'].append({
                    'name': 'Content-Aware Storage',
                    'status': 'active',
                    'statistics': cas_stats
                })
            except Exception as e:
                system_info['components'].append({
                    'name': 'Content-Aware Storage',
                    'status': 'error',
                    'error': str(e)
                })
        
        # Add LLM information if available
        if self.llm_service:
            try:
                llm_info = self.llm_service.get_model_info()
                system_info['components'].append({
                    'name': 'Language Model',
                    'status': 'active',
                    'model': llm_info
                })
            except Exception as e:
                system_info['components'].append({
                    'name': 'Language Model',
                    'status': 'error',
                    'error': str(e)
                })
        
        return {
            'status': 'success',
            'message': 'System information retrieved',
            'operation': 'system_info',
            'system_info': system_info
        }
