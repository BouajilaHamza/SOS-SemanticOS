"""
Input Processor component for Natural Language Interface.

This component handles user input and prepares it for processing.
It manages input history and provides input validation and preprocessing.
"""

from typing import List, Dict, Any, Optional, Callable
import re


class InputProcessor:
    """
    Handles user input and prepares it for processing.
    
    This class is responsible for:
    1. Managing input history and recall functionality
    2. Implementing auto-completion and suggestions
    3. Providing input validation and preprocessing
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the InputProcessor.
        
        Args:
            max_history: Maximum number of input history items to store
        """
        self.input_history = []
        self.max_history = max_history
        self.command_patterns = {}
        self.suggestion_providers = []
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input before sending it for further processing.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Processed input
        """
        # Trim whitespace
        processed_input = user_input.strip()
        
        # Skip empty input
        if not processed_input:
            return ""
        
        # Add to history
        self._add_to_history(processed_input)
        
        return processed_input
    
    def _add_to_history(self, input_text: str) -> None:
        """
        Add input to history.
        
        Args:
            input_text: Input text to add
        """
        # Don't add duplicates consecutively
        if self.input_history and self.input_history[-1] == input_text:
            return
            
        self.input_history.append(input_text)
        
        # Trim history if needed
        if len(self.input_history) > self.max_history:
            self.input_history = self.input_history[-self.max_history:]
    
    def get_history(self) -> List[str]:
        """
        Get the input history.
        
        Returns:
            List of historical inputs
        """
        return self.input_history.copy()
    
    def clear_history(self) -> None:
        """Clear the input history."""
        self.input_history = []
    
    def register_command_pattern(self, name: str, pattern: str, handler: Callable[[Dict[str, str]], str]) -> None:
        """
        Register a command pattern for special handling.
        
        Args:
            name: Name of the command
            pattern: Regex pattern to match
            handler: Function to handle matched commands
        """
        self.command_patterns[name] = {
            "pattern": re.compile(pattern, re.IGNORECASE),
            "handler": handler
        }
    
    def check_special_commands(self, input_text: str) -> Optional[str]:
        """
        Check if input matches any special command patterns.
        
        Args:
            input_text: Input text to check
            
        Returns:
            Command result if matched, None otherwise
        """
        for name, command in self.command_patterns.items():
            match = command["pattern"].match(input_text)
            if match:
                # Extract named groups
                groups = match.groupdict()
                # Call handler with extracted groups
                return command["handler"](groups)
        return None
    
    def register_suggestion_provider(self, provider: Callable[[str], List[str]]) -> None:
        """
        Register a function that provides suggestions based on partial input.
        
        Args:
            provider: Function that takes partial input and returns suggestions
        """
        self.suggestion_providers.append(provider)
    
    def get_suggestions(self, partial_input: str) -> List[str]:
        """
        Get suggestions based on partial input.
        
        Args:
            partial_input: Partial user input
            
        Returns:
            List of suggestions
        """
        all_suggestions = []
        
        # Get suggestions from all providers
        for provider in self.suggestion_providers:
            suggestions = provider(partial_input)
            all_suggestions.extend(suggestions)
        
        # Add history-based suggestions
        for item in reversed(self.input_history):
            if item.startswith(partial_input) and item not in all_suggestions:
                all_suggestions.append(item)
        
        return all_suggestions[:10]  # Limit to 10 suggestions
    
    def validate_input(self, input_text: str) -> Tuple[bool, str]:
        """
        Validate user input.
        
        Args:
            input_text: Input text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for empty input
        if not input_text.strip():
            return False, "Input cannot be empty."
        
        # Check for excessive length
        if len(input_text) > 1000:
            return False, "Input is too long (maximum 1000 characters)."
        
        return True, ""
