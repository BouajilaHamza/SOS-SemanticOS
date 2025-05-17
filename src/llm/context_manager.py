"""
Context Manager component for Local LLM Integration.

This component maintains conversation state and context for improved responses.
It tracks conversation history and manages context window limitations.
"""

from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime


class ContextManager:
    """
    Maintains conversation state and context for improved responses.
    
    This class is responsible for:
    1. Tracking conversation history
    2. Managing context window limitations
    3. Implementing strategies for context prioritization and summarization
    """
    
    def __init__(self, max_history: int = 10, max_tokens: int = 1024):
        """
        Initialize the ContextManager.
        
        Args:
            max_history: Maximum number of conversation turns to keep in history
            max_tokens: Maximum number of tokens to keep in context window
        """
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.conversation_history = []
        self.system_context = {}
        self.session_data = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "turn_count": 0
        }
    
    def _generate_session_id(self) -> str:
        """
        Generate a unique session ID.
        
        Returns:
            Session ID string
        """
        import uuid
        import time
        return f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def add_user_message(self, message: str) -> int:
        """
        Add a user message to the conversation history.
        
        Args:
            message: User message text
            
        Returns:
            Turn index of the added message
        """
        turn_idx = self.session_data["turn_count"]
        
        # Add message to history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "turn": turn_idx
        })
        
        # Increment turn count
        self.session_data["turn_count"] += 1
        
        # Trim history if needed
        self._trim_history()
        
        return turn_idx
    
    def add_assistant_message(self, message: str) -> int:
        """
        Add an assistant message to the conversation history.
        
        Args:
            message: Assistant message text
            
        Returns:
            Turn index of the added message
        """
        turn_idx = self.session_data["turn_count"]
        
        # Add message to history
        self.conversation_history.append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "turn": turn_idx
        })
        
        # Increment turn count
        self.session_data["turn_count"] += 1
        
        # Trim history if needed
        self._trim_history()
        
        return turn_idx
    
    def add_system_message(self, message: str) -> int:
        """
        Add a system message to the conversation history.
        
        Args:
            message: System message text
            
        Returns:
            Turn index of the added message
        """
        turn_idx = self.session_data["turn_count"]
        
        # Add message to history
        self.conversation_history.append({
            "role": "system",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "turn": turn_idx
        })
        
        # Increment turn count
        self.session_data["turn_count"] += 1
        
        # Trim history if needed
        self._trim_history()
        
        return turn_idx
    
    def _trim_history(self):
        """Trim conversation history to stay within limits."""
        # Trim by number of turns
        if len(self.conversation_history) > self.max_history:
            # Keep the most recent messages
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the current conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
    
    def get_formatted_history(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for model input.
        
        Args:
            include_system: Whether to include system messages
            
        Returns:
            List of formatted messages
        """
        formatted = []
        
        # Add current system context if requested
        if include_system and self.system_context.get("instructions"):
            formatted.append({
                "role": "system",
                "content": self.system_context["instructions"]
            })
        
        # Add conversation history
        for msg in self.conversation_history:
            if not include_system and msg["role"] == "system":
                continue
                
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.session_data["turn_count"] = 0
    
    def set_system_context(self, context_type: str, content: Any):
        """
        Set system context information.
        
        Args:
            context_type: Type of context (e.g., "instructions", "user_info")
            content: Context content
        """
        self.system_context[context_type] = content
    
    def get_system_context(self, context_type: Optional[str] = None) -> Any:
        """
        Get system context information.
        
        Args:
            context_type: Type of context to retrieve (None for all)
            
        Returns:
            Context content or entire context dictionary
        """
        if context_type is None:
            return self.system_context.copy()
        return self.system_context.get(context_type)
    
    def get_last_user_message(self) -> Optional[str]:
        """
        Get the last user message from the conversation history.
        
        Returns:
            Last user message or None if not found
        """
        for msg in reversed(self.conversation_history):
            if msg["role"] == "user":
                return msg["content"]
        return None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """
        Get the last assistant message from the conversation history.
        
        Returns:
            Last assistant message or None if not found
        """
        for msg in reversed(self.conversation_history):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
    
    def save_context(self, file_path: str) -> bool:
        """
        Save the current context to a file.
        
        Args:
            file_path: Path to save the context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                "session_data": self.session_data,
                "conversation_history": self.conversation_history,
                "system_context": self.system_context
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving context: {e}")
            return False
    
    def load_context(self, file_path: str) -> bool:
        """
        Load context from a file.
        
        Args:
            file_path: Path to load the context from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            self.session_data = data.get("session_data", self.session_data)
            self.conversation_history = data.get("conversation_history", [])
            self.system_context = data.get("system_context", {})
                
            return True
        except Exception as e:
            print(f"Error loading context: {e}")
            return False
