"""
Interface Demo script for testing the Natural Language Interface.

This script demonstrates the basic usage of the Natural Language Interface by:
1. Initializing the interface with a simple message handler
2. Processing sample user inputs
3. Demonstrating special commands and system messages
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from interface.interface_api import NaturalLanguageInterface
from llm.llm_api import LocalLLM
from cas.cas_api import ContentAwareStorage


class SemanticOSDemo:
    """Demo class to showcase the Semantic OS interface with LLM and CAS integration."""
    
    def __init__(self):
        """Initialize the demo."""
        # Define directories
        self.home_dir = str(Path.home())
        self.storage_dir = os.path.join(self.home_dir, ".semantic_os")
        
        # Initialize components
        self.llm = None
        self.cas = None
        self.interface = None
        
        # Create storage directory
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def initialize(self):
        """Initialize all components."""
        print("Initializing Semantic OS components...")
        
        # Initialize LLM
        print("Loading language model...")
        self.llm = LocalLLM(os.path.join(self.storage_dir, "llm"), model_name="microsoft/phi-2")
        self.llm.initialize(quantize=True)
        
        # Initialize CAS
        print("Setting up content-aware storage...")
        test_dir = os.path.join(self.home_dir, "test_files")
        os.makedirs(test_dir, exist_ok=True)
        self.cas = ContentAwareStorage([test_dir], os.path.join(self.storage_dir, "cas"))
        self.cas.start()
        
        # Initialize interface
        print("Starting natural language interface...")
        self.interface = NaturalLanguageInterface(
            os.path.join(self.storage_dir, "interface"),
            message_handler=self.handle_message
        )
        
        # Register special commands
        self.register_commands()
        
        # Start interface
        self.interface.start()
        
        print("Semantic OS initialized successfully.")
    
    def register_commands(self):
        """Register special commands for the interface."""
        # Help command
        self.interface.register_command(
            "help",
            r"^help$|^commands$|^\?$",
            lambda _: self.get_help()
        )
        
        # Session info command
        self.interface.register_command(
            "session",
            r"^session$|^session info$",
            lambda _: self.get_session_info()
        )
        
        # Search command
        self.interface.register_command(
            "search",
            r"^search\s+(?P<query>.+)$",
            lambda groups: self.search_files(groups["query"])
        )
        
        # System info command
        self.interface.register_command(
            "system",
            r"^system$|^system info$",
            lambda _: self.get_system_info()
        )
    
    def handle_message(self, message: str) -> str:
        """
        Handle a user message.
        
        Args:
            message: User message
            
        Returns:
            Response message
        """
        # Process message with LLM
        response = self.llm.process_query(message)
        
        # Extract intent
        intent_data = self.llm.extract_intent(message)
        intent = intent_data.get("intent", "")
        
        # Handle search intent
        if intent == "search_files" or intent == "search_content":
            # Extract search terms
            search_terms = message.lower()
            for prefix in ["find", "search", "look for", "locate"]:
                if search_terms.startswith(prefix):
                    search_terms = search_terms[len(prefix):].strip()
            
            # Perform search
            search_results = self.cas.search(search_terms)
            
            # Add search results to response
            if search_results:
                response += f"\n\nI found {len(search_results)} files related to '{search_terms}':"
                for i, result in enumerate(search_results[:5], 1):
                    response += f"\n{i}. {result.get('filename', 'Unknown')} - {result.get('path', '')}"
                
                if len(search_results) > 5:
                    response += f"\n...and {len(search_results) - 5} more."
        
        return response
    
    def get_help(self) -> str:
        """
        Get help information.
        
        Returns:
            Help text
        """
        return """
Available commands:
- help: Show this help message
- session: Show current session information
- search [query]: Search for files matching the query
- system: Show system information

You can also ask questions in natural language, and I'll do my best to help you!
"""
    
    def get_session_info(self) -> str:
        """
        Get session information.
        
        Returns:
            Session information text
        """
        session_info = self.interface.get_session_info()
        
        return f"""
Session Information:
- ID: {session_info.get('session_id', 'Unknown')}
- Started: {session_info.get('start_time', 'Unknown')}
- Messages: {session_info.get('message_count', 0)}
- Duration: {session_info.get('duration', 'Unknown')}
"""
    
    def search_files(self, query: str) -> str:
        """
        Search for files.
        
        Args:
            query: Search query
            
        Returns:
            Search results text
        """
        results = self.cas.search(query)
        
        if not results:
            return f"No files found matching '{query}'."
        
        response = f"Found {len(results)} files matching '{query}':\n"
        
        for i, result in enumerate(results[:10], 1):
            filename = result.get('filename', 'Unknown')
            path = result.get('path', '')
            response += f"\n{i}. {filename} - {path}"
        
        if len(results) > 10:
            response += f"\n\n...and {len(results) - 10} more."
        
        return response
    
    def get_system_info(self) -> str:
        """
        Get system information.
        
        Returns:
            System information text
        """
        # Get CAS statistics
        cas_stats = self.cas.get_statistics()
        
        # Get LLM information
        llm_info = self.llm.get_model_info()
        
        return f"""
Semantic OS System Information:

Content-Aware Storage:
- Total files: {cas_stats.get('total_files', 0)}
- Total size: {cas_stats.get('total_size', 0)} bytes
- Monitored directories: {', '.join(cas_stats.get('monitored_directories', []))}

Language Model:
- Model: {llm_info.get('name', 'Unknown')}
- Device: {llm_info.get('device', 'Unknown')}
- Quantized: {llm_info.get('quantized', False)}
"""
    
    def shutdown(self):
        """Shut down all components."""
        print("Shutting down Semantic OS...")
        
        # Stop interface
        if self.interface:
            self.interface.stop()
        
        # Stop CAS
        if self.cas:
            self.cas.stop()
        
        # Unload LLM
        if self.llm:
            self.llm.shutdown()
        
        print("Semantic OS shut down successfully.")


def main():
    """Main function to run the demo."""
    demo = SemanticOSDemo()
    
    try:
        demo.initialize()
        
        print("\nSemanticOS is running. Press Ctrl+C to exit.")
        
        # Keep the main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived exit signal.")
    finally:
        demo.shutdown()


if __name__ == "__main__":
    main()
