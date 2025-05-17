"""
Session Manager component for Natural Language Interface.

This component maintains user session state across interactions.
It tracks conversation history and manages user preferences and settings.
"""

from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime
from pathlib import Path


class SessionManager:
    """
    Maintains user session state across interactions.
    
    This class is responsible for:
    1. Tracking conversation history
    2. Managing user preferences and settings
    3. Implementing session persistence for continuity across restarts
    """
    
    def __init__(self, session_dir: str):
        """
        Initialize the SessionManager.
        
        Args:
            session_dir: Directory to store session data
        """
        self.session_dir = Path(session_dir).expanduser().absolute()
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = self._generate_session_id()
        self.session_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0,
            "preferences": {},
            "context": {}
        }
    
    def _generate_session_id(self) -> str:
        """
        Generate a unique session ID.
        
        Returns:
            Session ID string
        """
        import uuid
        return f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.session_data["last_activity"] = datetime.now().isoformat()
    
    def increment_message_count(self):
        """Increment the message count."""
        self.session_data["message_count"] += 1
        self.update_activity()
    
    def set_preference(self, key: str, value: Any):
        """
        Set a user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.session_data["preferences"][key] = value
        self.update_activity()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.
        
        Args:
            key: Preference key
            default: Default value if preference is not set
            
        Returns:
            Preference value or default
        """
        return self.session_data["preferences"].get(key, default)
    
    def set_context(self, key: str, value: Any):
        """
        Set a context value.
        
        Args:
            key: Context key
            value: Context value
        """
        self.session_data["context"][key] = value
        self.update_activity()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a context value.
        
        Args:
            key: Context key
            default: Default value if context is not set
            
        Returns:
            Context value or default
        """
        return self.session_data["context"].get(key, default)
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.
        
        Returns:
            Dictionary of session information
        """
        # Calculate session duration
        start_time = datetime.fromisoformat(self.session_data["start_time"])
        duration_seconds = (datetime.now() - start_time).total_seconds()
        
        # Format duration
        hours, remainder = divmod(int(duration_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return {
            "session_id": self.session_id,
            "start_time": self.session_data["start_time"],
            "last_activity": self.session_data["last_activity"],
            "message_count": self.session_data["message_count"],
            "duration": duration_str
        }
    
    def save_session(self) -> str:
        """
        Save the current session to a file.
        
        Returns:
            Path to the saved session file
        """
        # Update last activity
        self.update_activity()
        
        # Generate filename
        filename = f"{self.session_id}.json"
        file_path = self.session_dir / filename
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        
        return str(file_path)
    
    def load_session(self, session_id: str) -> bool:
        """
        Load a session from a file.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            True if successful, False otherwise
        """
        # Generate filename
        filename = f"{session_id}.json"
        file_path = self.session_dir / filename
        
        # Check if file exists
        if not file_path.exists():
            return False
        
        try:
            # Load from file
            with open(file_path, 'r') as f:
                self.session_data = json.load(f)
            
            # Update session ID
            self.session_id = session_id
            
            # Update last activity
            self.update_activity()
            
            return True
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all saved sessions.
        
        Returns:
            List of session information dictionaries
        """
        sessions = []
        
        # Find all session files
        for file_path in self.session_dir.glob("session_*.json"):
            try:
                # Load session data
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                
                # Extract basic info
                sessions.append({
                    "session_id": session_data.get("session_id", "unknown"),
                    "start_time": session_data.get("start_time", ""),
                    "last_activity": session_data.get("last_activity", ""),
                    "message_count": session_data.get("message_count", 0)
                })
            except Exception as e:
                print(f"Error reading session file {file_path}: {e}")
        
        # Sort by last activity (most recent first)
        sessions.sort(key=lambda s: s.get("last_activity", ""), reverse=True)
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a saved session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Generate filename
        filename = f"{session_id}.json"
        file_path = self.session_dir / filename
        
        # Check if file exists
        if not file_path.exists():
            return False
        
        try:
            # Delete file
            file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
