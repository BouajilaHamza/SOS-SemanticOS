"""
Local LLM API for Semantic OS.

This module provides a unified interface for interacting with the local LLM.
It integrates the model manager, context manager, prompt engineer, and inference engine.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import os
from pathlib import Path

from .model_manager import ModelManager
from .context_manager import ContextManager
from .prompt_engineer import PromptEngineer
from .inference_engine import InferenceEngine


class LocalLLM:
    """
    Unified API for the Local LLM integration.
    
    This class integrates the model manager, context manager, prompt engineer,
    and inference engine to provide a comprehensive interface for natural language
    understanding and generation.
    """
    
    def __init__(self, storage_dir: str, model_name: str = "microsoft/phi-2"):
        """
        Initialize the Local LLM integration.
        
        Args:
            storage_dir: Directory to store model files and context data
            model_name: Name or path of the model to use
        """
        self.storage_dir = Path(storage_dir).expanduser().absolute()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.model_manager = ModelManager(
            model_dir=str(self.storage_dir / "models"),
            model_name=model_name
        )
        self.context_manager = ContextManager()
        self.prompt_engineer = PromptEngineer(model_name=model_name)
        self.inference_engine = InferenceEngine(self.model_manager)
    
    def initialize(self, quantize: bool = True) -> bool:
        """
        Initialize the LLM system.
        
        Args:
            quantize: Whether to apply quantization for reduced memory usage
            
        Returns:
            True if successful, False otherwise
        """
        # Load the model
        success = self.model_manager.load_model(quantize=quantize)
        
        # Set up system context
        if success:
            self.context_manager.set_system_context("instructions", self.prompt_engineer._get_default_system_instructions())
            self.context_manager.set_system_context("model_info", self.model_manager.get_model_metadata())
        
        return success
    
    def shutdown(self) -> bool:
        """
        Shut down the LLM system.
        
        Returns:
            True if successful, False otherwise
        """
        return self.model_manager.unload_model()
    
    def process_query(self, query: str, generation_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a user query and generate a response.
        
        Args:
            query: User query text
            generation_params: Parameters for text generation
            
        Returns:
            Generated response
        """
        # Add user message to context
        self.context_manager.add_user_message(query)
        
        # Get conversation history
        conversation_history = self.context_manager.get_formatted_history()
        
        # Get system context
        system_context = self.context_manager.get_system_context()
        
        # Format prompt
        prompt = self.prompt_engineer.format_prompt(
            user_input=query,
            conversation_history=conversation_history,
            system_context=system_context
        )
        
        # Generate response
        response = self.inference_engine.generate_with_fallback(
            prompt=prompt,
            generation_params=generation_params
        )
        
        # Add assistant response to context
        self.context_manager.add_assistant_message(response)
        
        return response
    
    def extract_intent(self, query: str) -> Dict[str, Any]:
        """
        Extract intent and entities from a user query.
        
        Args:
            query: User query text
            
        Returns:
            Dictionary containing intent and entities
        """
        # Use prompt engineer's rule-based intent extraction
        intent_data = self.prompt_engineer.extract_command_intent(query)
        
        # For more sophisticated intent extraction, we could use the LLM directly
        # This would be implemented in a real system
        
        return intent_data
    
    def generate_file_operation_response(self, 
                                       operation: str, 
                                       file_path: str, 
                                       additional_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response for a file operation.
        
        Args:
            operation: Type of file operation
            file_path: Path of the file
            additional_context: Additional context for the operation
            
        Returns:
            Generated response
        """
        # Create specialized prompt
        specialized_prompt = self.prompt_engineer.create_file_operation_prompt(
            operation=operation,
            file_path=file_path,
            additional_context=additional_context
        )
        
        # Process as a regular query
        return self.process_query(specialized_prompt)
    
    def generate_search_response(self, 
                               query: str, 
                               search_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response for a search operation.
        
        Args:
            query: Search query
            search_context: Additional context for the search
            
        Returns:
            Generated response
        """
        # Create specialized prompt
        specialized_prompt = self.prompt_engineer.create_search_prompt(
            query=query,
            search_context=search_context
        )
        
        # Process as a regular query
        return self.process_query(specialized_prompt)
    
    def save_session(self, file_path: Optional[str] = None) -> bool:
        """
        Save the current session state.
        
        Args:
            file_path: Path to save the session (default: auto-generated)
            
        Returns:
            True if successful, False otherwise
        """
        if file_path is None:
            # Generate a default file path
            import time
            timestamp = int(time.time())
            file_path = str(self.storage_dir / f"session_{timestamp}.json")
        
        return self.context_manager.save_context(file_path)
    
    def load_session(self, file_path: str) -> bool:
        """
        Load a saved session state.
        
        Args:
            file_path: Path to the saved session
            
        Returns:
            True if successful, False otherwise
        """
        return self.context_manager.load_context(file_path)
    
    def clear_session(self):
        """Clear the current session state."""
        self.context_manager.clear_history()
    
    def switch_model(self, model_name: str, quantize: bool = True) -> bool:
        """
        Switch to a different language model.
        
        Args:
            model_name: Name or path of the new model
            quantize: Whether to apply quantization
            
        Returns:
            True if successful, False otherwise
        """
        # Switch the model
        success = self.model_manager.switch_model(model_name, quantize=quantize)
        
        # Update prompt engineer if successful
        if success:
            self.prompt_engineer = PromptEngineer(model_name=model_name)
            
            # Update system context
            self.context_manager.set_system_context("instructions", self.prompt_engineer._get_default_system_instructions())
            self.context_manager.set_system_context("model_info", self.model_manager.get_model_metadata())
        
        return success
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary of model information
        """
        return self.model_manager.get_model_metadata()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the current conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.context_manager.get_conversation_history()
