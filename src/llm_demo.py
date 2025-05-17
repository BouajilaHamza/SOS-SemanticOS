"""
LLM Demo script for testing the Local LLM Integration.

This script demonstrates the basic usage of the Local LLM system by:
1. Initializing the LLM with a specified model
2. Processing sample queries
3. Demonstrating intent extraction and specialized responses
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from llm.llm_api import LocalLLM


def main():
    """Main function to demonstrate LLM functionality."""
    # Define directories
    home_dir = str(Path.home())
    storage_dir = os.path.join(home_dir, ".semantic_os", "llm")
    
    # Initialize LLM
    print("Initializing Local LLM...")
    llm = LocalLLM(storage_dir, model_name="microsoft/phi-2")
    
    # Load the model (with quantization for efficiency)
    print("Loading language model (this may take a moment)...")
    success = llm.initialize(quantize=True)
    
    if not success:
        print("Failed to initialize LLM. Exiting.")
        return
    
    try:
        print("\nModel information:")
        model_info = llm.get_model_info()
        for key, value in model_info.items():
            print(f"  {key}: {value}")
        
        # Process a simple query
        print("\nProcessing a simple query...")
        query = "What can you help me with in the Semantic OS?"
        print(f"User: {query}")
        
        response = llm.process_query(query)
        print(f"Assistant: {response}")
        
        # Extract intent from a query
        print("\nExtracting intent from a query...")
        intent_query = "Find files related to python programming"
        print(f"User: {intent_query}")
        
        intent_data = llm.extract_intent(intent_query)
        print(f"Intent: {intent_data}")
        
        # Generate a specialized response for a file operation
        print("\nGenerating a specialized response for a file operation...")
        operation = "create"
        file_path = "/home/user/documents/project_plan.md"
        additional_context = {
            "content": "# Project Plan\n\n## Objectives\n\n- Implement Semantic OS\n- Test with users\n- Gather feedback"
        }
        
        print(f"User: Create a new project plan file")
        response = llm.generate_file_operation_response(operation, file_path, additional_context)
        print(f"Assistant: {response}")
        
        # Generate a specialized response for a search operation
        print("\nGenerating a specialized response for a search operation...")
        search_query = "semantic computing"
        search_context = {
            "file_types": ["pdf", "md", "txt"],
            "date_range": "last month"
        }
        
        print(f"User: Find documents about semantic computing from the last month")
        response = llm.generate_search_response(search_query, search_context)
        print(f"Assistant: {response}")
        
        # Show conversation history
        print("\nConversation history:")
        history = llm.get_conversation_history()
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            print(f"{role.capitalize()}: {content[:50]}..." if len(content) > 50 else f"{role.capitalize()}: {content}")
        
        print("\nLLM demonstration completed successfully.")
    finally:
        # Shut down LLM
        print("Shutting down LLM...")
        llm.shutdown()


if __name__ == "__main__":
    main()
