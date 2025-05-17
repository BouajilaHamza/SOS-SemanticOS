"""
Interface API component for Natural Language Interface.

This module provides a unified interface for interacting with the natural language interface.
It integrates the terminal UI, input processor, response formatter, and session manager.
"""

from typing import Dict, List, Any, Optional, Callable
import threading
import asyncio
from pathlib import Path

from .terminal_ui import TerminalUI
from .input_processor import InputProcessor
from .response_formatter import ResponseFormatter
from .session_manager import SessionManager


class NaturalLanguageInterface:
    """
    Unified API for the Natural Language Interface.
    
    This class integrates the terminal UI, input processor, response formatter,
    and session manager to provide a comprehensive interface for natural language
    interaction with the Semantic OS.
    """
    
    def __init__(self, storage_dir: str, message_handler: Optional[Callable[[str], str]] = None):
        """
        Initialize the Natural Language Interface.
        
        Args:
            storage_dir: Directory to store interface data
            message_handler: Function to handle user messages
        """
        self.storage_dir = Path(storage_dir).expanduser().absolute()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.terminal_ui = TerminalUI()
        self.input_processor = InputProcessor()
        self.response_formatter = ResponseFormatter()
        self.session_manager = SessionManager(str(self.storage_dir / "sessions"))
        
        # Set message handler
        self.message_handler = message_handler
        
        # Set up UI message callback
        self.terminal_ui.set_message_callback(self._handle_message)
        
        # Thread for running the UI
        self.ui_thread = None
        self.running = False
    
    def _handle_message(self, message: str) -> None:
        """
        Handle a user message.
        
        Args:
            message: User message
        """
        # Process input
        processed_input = self.input_processor.process_input(message)
        if not processed_input:
            return
            
        # Update session
        self.session_manager.increment_message_count()
        
        # Check for special commands
        special_result = self.input_processor.check_special_commands(processed_input)
        if special_result:
            # Display system message for special commands
            self.display_system_message(special_result)
            return
        
        # Process message with handler if available
        if self.message_handler:
            try:
                # Process message
                response = self.message_handler(processed_input)
                
                # Format and display response
                formatted_response = self.response_formatter.format_response(response)
                self.display_assistant_message(formatted_response)
            except Exception as e:
                # Display error
                error_msg = f"Error processing message: {str(e)}"
                self.display_system_message(error_msg)
        else:
            # No handler available
            self.display_system_message("No message handler configured.")
    
    def start(self) -> None:
        """Start the natural language interface."""
        if self.running:
            return
            
        self.running = True
        
        # Start UI in a separate thread
        self.ui_thread = threading.Thread(target=self._run_ui)
        self.ui_thread.daemon = True
        self.ui_thread.start()
    
    def _run_ui(self) -> None:
        """Run the terminal UI."""
        self.terminal_ui.run()
        self.running = False
    
    def stop(self) -> None:
        """Stop the natural language interface."""
        if not self.running:
            return
            
        # Save session
        self.session_manager.save_session()
        
        # Stop UI
        self.terminal_ui.stop()
        
        # Wait for UI thread to finish
        if self.ui_thread and self.ui_thread.is_alive():
            self.ui_thread.join(timeout=5.0)
            
        self.running = False
    
    def display_assistant_message(self, message: str) -> None:
        """
        Display an assistant message in the UI.
        
        Args:
            message: Assistant message
        """
        self.terminal_ui.display_response(message)
    
    def display_system_message(self, message: str) -> None:
        """
        Display a system message in the UI.
        
        Args:
            message: System message
        """
        self.terminal_ui.display_system_message(message)
    
    def update_status(self, status: str) -> None:
        """
        Update the status bar in the UI.
        
        Args:
            status: Status text
        """
        self.terminal_ui.update_status(status)
    
    def register_command(self, name: str, pattern: str, handler: Callable[[Dict[str, str]], str]) -> None:
        """
        Register a special command pattern.
        
        Args:
            name: Command name
            pattern: Regex pattern to match
            handler: Function to handle matched commands
        """
        self.input_processor.register_command_pattern(name, pattern, handler)
    
    def register_suggestion_provider(self, provider: Callable[[str], List[str]]) -> None:
        """
        Register a suggestion provider.
        
        Args:
            provider: Function that provides suggestions for partial input
        """
        self.input_processor.register_suggestion_provider(provider)
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.
        
        Returns:
            Dictionary of session information
        """
        return self.session_manager.get_session_info()
    
    def save_session(self) -> str:
        """
        Save the current session.
        
        Returns:
            Path to the saved session file
        """
        return self.session_manager.save_session()
    
    def load_session(self, session_id: str) -> bool:
        """
        Load a saved session.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            True if successful, False otherwise
        """
        return self.session_manager.load_session(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all saved sessions.
        
        Returns:
            List of session information dictionaries
        """
        return self.session_manager.list_sessions()
    
    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.session_manager.set_preference(key, value)
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.
        
        Args:
            key: Preference key
            default: Default value if preference is not set
            
        Returns:
            Preference value or default
        """
        return self.session_manager.get_preference(key, default)
