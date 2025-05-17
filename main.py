#!/usr/bin/env python3
"""
Semantic OS - Main Entry Point

This script initializes and runs the Semantic Operating System.
It integrates all components and provides a unified interface.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent))

from src.cas.cas_api import ContentAwareStorage
from src.llm.llm_api import LocalLLM
from src.interface.interface_api import NaturalLanguageInterface
from src.mcp.mcp_api import ModularCommandProcessing


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Semantic Operating System')
    
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to configuration file')
    parser.add_argument('--storage-dir', type=str, default=os.path.expanduser('~/.semantic_os'),
                        help='Directory to store system data')
    parser.add_argument('--monitor-dirs', type=str, nargs='+',
                        default=[os.path.expanduser('~/Documents')],
                        help='Directories to monitor for content indexing')
    parser.add_argument('--model', type=str, default='microsoft/phi-2',
                        help='Language model to use')
    parser.add_argument('--no-ui', action='store_true',
                        help='Run without the terminal UI')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    
    return parser.parse_args()


class SemanticOS:
    """Main class for the Semantic Operating System."""
    
    def __init__(self, args):
        """
        Initialize the Semantic OS.
        
        Args:
            args: Command line arguments
        """
        self.args = args
        self.storage_dir = args.storage_dir
        self.monitor_dirs = args.monitor_dirs
        self.model_name = args.model
        self.debug = args.debug
        
        # Create storage directory
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize components
        self.cas = None
        self.llm = None
        self.mcp = None
        self.interface = None
    
    def initialize(self):
        """Initialize all components."""
        print("Initializing Semantic OS...")
        
        try:
            # Initialize CAS
            print("Setting up Content-Aware Storage...")
            self.cas = ContentAwareStorage(
                self.monitor_dirs,
                os.path.join(self.storage_dir, "cas")
            )
            self.cas.start()
            
            # Initialize LLM
            print("Loading Language Model...")
            self.llm = LocalLLM(
                os.path.join(self.storage_dir, "llm"),
                model_name=self.model_name
            )
            self.llm.initialize(quantize=True)
            
            # Initialize MCP
            print("Setting up Modular Command Processing...")
            self.mcp = ModularCommandProcessing(
                os.path.join(self.storage_dir, "mcp"),
                llm_service=self.llm,
                cas_service=self.cas
            )
            self.mcp.initialize_default_processors()
            
            # Initialize Interface if UI is enabled
            if not self.args.no_ui:
                print("Starting Natural Language Interface...")
                self.interface = NaturalLanguageInterface(
                    os.path.join(self.storage_dir, "interface"),
                    message_handler=self._handle_message
                )
                
            print("Semantic OS initialized successfully.")
            return True
        except Exception as e:
            print(f"Error initializing Semantic OS: {e}")
            return False
    
    def _handle_message(self, message):
        """
        Handle a user message.
        
        Args:
            message: User message
            
        Returns:
            Response message
        """
        # Process message with MCP
        result = self.mcp.process_command(message)
        
        # Extract response
        if isinstance(result, dict) and 'message' in result:
            return result['message']
        elif isinstance(result, dict) and 'status' in result:
            if result['status'] == 'success':
                return f"Operation completed successfully: {result.get('operation', 'unknown')}"
            else:
                return f"Error: {result.get('message', 'Unknown error')}"
        else:
            return str(result)
    
    def run(self):
        """Run the Semantic OS."""
        if self.interface:
            # Start the interface
            self.interface.start()
            
            try:
                # Keep the main thread alive
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nReceived exit signal.")
            finally:
                self.shutdown()
        else:
            # Run in command-line mode
            print("Running in command-line mode. Press Ctrl+C to exit.")
            print("Enter commands (empty line to exit):")
            
            try:
                while True:
                    command = input("> ")
                    if not command:
                        break
                    
                    result = self.mcp.process_command(command)
                    print(f"Result: {result}")
            except KeyboardInterrupt:
                print("\nReceived exit signal.")
            finally:
                self.shutdown()
    
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
    """Main entry point."""
    args = parse_arguments()
    
    # Create and initialize Semantic OS
    semantic_os = SemanticOS(args)
    
    if semantic_os.initialize():
        # Run the system
        semantic_os.run()
    else:
        print("Failed to initialize Semantic OS. Exiting.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
