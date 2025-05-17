"""
Main module for testing the Content-Aware Storage (CAS) functionality.

This script demonstrates the basic usage of the CAS system by:
1. Initializing the CAS with a specified directory to monitor
2. Performing initial indexing of files
3. Executing sample searches and retrievals
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from cas.cas_api import ContentAwareStorage


def main():
    """Main function to demonstrate CAS functionality."""
    # Define directories
    home_dir = str(Path.home())
    test_dir = os.path.join(home_dir, "test_files")
    storage_dir = os.path.join(home_dir, ".semantic_os", "storage")
    
    # Create test directory if it doesn't exist
    os.makedirs(test_dir, exist_ok=True)
    
    # Create some test files
    create_test_files(test_dir)
    
    # Initialize CAS
    print(f"Initializing Content-Aware Storage with directory: {test_dir}")
    cas = ContentAwareStorage([test_dir], storage_dir)
    
    # Start CAS
    print("Starting CAS system...")
    cas.start()
    
    try:
        # Wait for initial indexing to complete
        print("Waiting for initial indexing to complete...")
        import time
        time.sleep(2)
        
        # Get statistics
        stats = cas.get_statistics()
        print("\nCAS Statistics:")
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size']} bytes")
        print("File extensions:")
        for ext, count in stats.get('extensions', {}).items():
            print(f"  {ext or 'no extension'}: {count} files")
        
        # Perform a search
        print("\nSearching for 'python'...")
        results = cas.search("python")
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('filename')} - {result.get('path')}")
        
        # Get metadata for a specific file
        if results:
            file_path = results[0].get('path')
            print(f"\nMetadata for {os.path.basename(file_path)}:")
            metadata = cas.get_file_metadata(file_path)
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        
        # Demonstrate related files
        if results:
            file_path = results[0].get('path')
            print(f"\nFiles related to {os.path.basename(file_path)}:")
            related = cas.get_related_files(file_path)
            for i, rel in enumerate(related, 1):
                print(f"{i}. {rel.get('filename')} - {rel.get('path')}")
        
        print("\nCAS demonstration completed successfully.")
    finally:
        # Stop CAS
        print("Stopping CAS system...")
        cas.stop()


def create_test_files(directory):
    """Create some test files for demonstration."""
    # Python file
    with open(os.path.join(directory, "hello.py"), "w") as f:
        f.write("""
# Simple Python script
def hello():
    print("Hello from Python!")

if __name__ == "__main__":
    hello()
""")
    
    # Markdown file
    with open(os.path.join(directory, "readme.md"), "w") as f:
        f.write("""
# Semantic OS

A natural language operating system that enables content-aware file management.

## Features

- Content-Aware Storage
- Local LLM Integration
- Natural Language Interface
- Modular Command Processing
""")
    
    # Text file
    with open(os.path.join(directory, "notes.txt"), "w") as f:
        f.write("""
Notes on Semantic Computing

Semantic computing involves understanding the meaning and context of data.
This enables more intuitive interactions with computers through natural language.

Key concepts:
- Natural Language Processing
- Knowledge Representation
- Semantic Search
- Context Awareness
""")


if __name__ == "__main__":
    main()
