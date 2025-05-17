"""
Integration Test Script for Semantic OS.

This script performs an end-to-end integration test of the Semantic OS by:
1. Creating a test environment with sample files
2. Initializing all components (CAS, LLM, Interface, MCP)
3. Running a series of commands through the system
4. Validating the responses and interactions between components
"""

import os
import sys
import time
import shutil
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from cas.cas_api import ContentAwareStorage
from llm.llm_api import LocalLLM
from mcp.mcp_api import ModularCommandProcessing


class SemanticOSIntegrationTest:
    """Integration test for the Semantic OS."""
    
    def __init__(self):
        """Initialize the integration test."""
        # Define directories
        self.home_dir = str(Path.home())
        self.test_dir = os.path.join(self.home_dir, "semantic_os_test")
        self.test_files_dir = os.path.join(self.test_dir, "test_files")
        self.storage_dir = os.path.join(self.test_dir, "storage")
        
        # Initialize components
        self.cas = None
        self.llm = None
        self.mcp = None
        
        # Test results
        self.results = []
    
    def setup(self):
        """Set up the test environment."""
        print("Setting up test environment...")
        
        # Create directories
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.test_files_dir, exist_ok=True)
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Create test files
        self._create_test_files()
        
        print("Test environment set up successfully.")
    
    def _create_test_files(self):
        """Create test files for the integration test."""
        # Create a Python file
        with open(os.path.join(self.test_files_dir, "project.py"), "w") as f:
            f.write("""
# Semantic OS Project
class SemanticOS:
    def __init__(self):
        self.name = "Semantic Operating System"
        self.version = "0.1.0"
    
    def start(self):
        print(f"Starting {self.name} v{self.version}")

if __name__ == "__main__":
    os = SemanticOS()
    os.start()
""")
        
        # Create a Markdown file
        with open(os.path.join(self.test_files_dir, "documentation.md"), "w") as f:
            f.write("""
# Semantic OS Documentation

## Overview
The Semantic Operating System (Semantic OS) enables natural language interactions
for managing files and executing tasks on a Linux-based system.

## Components
1. Content-Aware Storage (CAS)
2. Local Large Language Model (LLM)
3. Natural Language Interface
4. Modular Command Processing (MCP)
""")
        
        # Create a text file
        with open(os.path.join(self.test_files_dir, "notes.txt"), "w") as f:
            f.write("""
Semantic OS Development Notes

- Implement content-aware storage with Whoosh
- Integrate local LLM using Hugging Face Transformers
- Develop natural language terminal interface
- Create modular command processing framework
- Test agent-to-agent communication
""")
        
        # Create a configuration file
        with open(os.path.join(self.test_files_dir, "config.json"), "w") as f:
            f.write("""
{
    "name": "Semantic OS",
    "version": "0.1.0",
    "components": [
        {"name": "CAS", "enabled": true},
        {"name": "LLM", "enabled": true},
        {"name": "Interface", "enabled": true},
        {"name": "MCP", "enabled": true}
    ],
    "settings": {
        "debug": false,
        "log_level": "info",
        "storage_path": "/home/user/.semantic_os"
    }
}
""")
    
    def initialize_components(self):
        """Initialize all Semantic OS components."""
        print("Initializing Semantic OS components...")
        
        try:
            # Initialize CAS
            print("Initializing Content-Aware Storage...")
            self.cas = ContentAwareStorage(
                [self.test_files_dir],
                os.path.join(self.storage_dir, "cas")
            )
            self.cas.start()
            
            # Wait for indexing to complete
            time.sleep(2)
            
            # Initialize LLM
            print("Initializing Local LLM...")
            self.llm = LocalLLM(
                os.path.join(self.storage_dir, "llm"),
                model_name="microsoft/phi-2"
            )
            self.llm.initialize(quantize=True)
            
            # Initialize MCP
            print("Initializing Modular Command Processing...")
            self.mcp = ModularCommandProcessing(
                os.path.join(self.storage_dir, "mcp"),
                llm_service=self.llm,
                cas_service=self.cas
            )
            self.mcp.initialize_default_processors()
            
            print("All components initialized successfully.")
            return True
        except Exception as e:
            print(f"Error initializing components: {e}")
            return False
    
    def run_tests(self):
        """Run the integration tests."""
        print("\nRunning integration tests...")
        
        # Test 1: CAS Search
        self._run_test(
            "CAS Search",
            self._test_cas_search,
            "Testing basic search functionality"
        )
        
        # Test 2: LLM Query
        self._run_test(
            "LLM Query",
            self._test_llm_query,
            "Testing LLM query processing"
        )
        
        # Test 3: Command Processing
        self._run_test(
            "Command Processing",
            self._test_command_processing,
            "Testing command routing and processing"
        )
        
        # Test 4: Workflow Execution
        self._run_test(
            "Workflow Execution",
            self._test_workflow_execution,
            "Testing workflow creation and execution"
        )
        
        # Test 5: End-to-End Integration
        self._run_test(
            "End-to-End Integration",
            self._test_end_to_end,
            "Testing complete system integration"
        )
        
        # Print summary
        self._print_summary()
    
    def _run_test(self, name, test_func, description):
        """Run a single test and record the result."""
        print(f"\n=== Test: {name} ===")
        print(f"Description: {description}")
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            duration = end_time - start_time
            
            if result:
                status = "PASS"
                print(f"Result: PASS (completed in {duration:.2f}s)")
            else:
                status = "FAIL"
                print(f"Result: FAIL (completed in {duration:.2f}s)")
            
            self.results.append({
                "name": name,
                "description": description,
                "status": status,
                "duration": duration
            })
        except Exception as e:
            print(f"Error during test: {e}")
            self.results.append({
                "name": name,
                "description": description,
                "status": "ERROR",
                "error": str(e)
            })
    
    def _test_cas_search(self):
        """Test CAS search functionality."""
        if not self.cas:
            print("CAS not initialized")
            return False
        
        # Search for Python
        print("Searching for 'Python'...")
        python_results = self.cas.search("Python")
        print(f"Found {len(python_results)} results")
        
        # Search for Semantic
        print("Searching for 'Semantic'...")
        semantic_results = self.cas.search("Semantic")
        print(f"Found {len(semantic_results)} results")
        
        # Search for documentation
        print("Searching for 'documentation'...")
        doc_results = self.cas.search("documentation")
        print(f"Found {len(doc_results)} results")
        
        # Verify results
        return (len(python_results) > 0 and 
                len(semantic_results) > 0 and 
                len(doc_results) > 0)
    
    def _test_llm_query(self):
        """Test LLM query processing."""
        if not self.llm:
            print("LLM not initialized")
            return False
        
        # Process a simple query
        print("Processing query: 'What is a semantic operating system?'")
        response = self.llm.process_query("What is a semantic operating system?")
        print(f"Response length: {len(response)} characters")
        print(f"Response preview: {response[:100]}...")
        
        # Extract intent
        print("Extracting intent from: 'Find files about Python'")
        intent = self.llm.extract_intent("Find files about Python")
        print(f"Extracted intent: {intent}")
        
        # Verify results
        return (len(response) > 100 and 
                isinstance(intent, dict) and 
                'intent' in intent)
    
    def _test_command_processing(self):
        """Test command processing functionality."""
        if not self.mcp:
            print("MCP not initialized")
            return False
        
        # Process a search command
        print("Processing command: 'Find files containing semantic'")
        search_result = self.mcp.process_command("Find files containing semantic")
        print(f"Search result: {search_result}")
        
        # Process a system info command
        print("Processing command: 'Show system information'")
        system_result = self.mcp.process_command("Show system information")
        print(f"System info result: {system_result}")
        
        # Process a general query
        print("Processing command: 'What is content-aware storage?'")
        query_result = self.mcp.process_command("What is content-aware storage?")
        print(f"Query result: {query_result}")
        
        # Verify results
        return (isinstance(search_result, dict) and 
                search_result.get('status') == 'success' and
                isinstance(system_result, dict) and 
                system_result.get('status') == 'success' and
                isinstance(query_result, dict) and 
                query_result.get('status') == 'success')
    
    def _test_workflow_execution(self):
        """Test workflow execution functionality."""
        if not self.mcp:
            print("MCP not initialized")
            return False
        
        # Create a workflow
        print("Creating workflow...")
        workflow_id = self.mcp.create_workflow(
            name="Integration Test Workflow",
            description="Workflow for integration testing"
        )
        print(f"Created workflow: {workflow_id}")
        
        # Add steps
        print("Adding workflow steps...")
        
        # Step 1: Search for files
        step1_id = self.mcp.add_workflow_step(
            workflow_id=workflow_id,
            agent_id="search_processor",
            action="search_files",
            parameters={"query": "semantic"}
        )
        print(f"Added search step: {step1_id}")
        
        # Step 2: Process search results
        step2_id = self.mcp.add_workflow_step(
            workflow_id=workflow_id,
            agent_id="query_processor",
            action="analyze_results",
            parameters={"max_results": 3},
            dependencies=[step1_id]
        )
        print(f"Added analysis step: {step2_id}")
        
        # Start the workflow
        print("Starting workflow...")
        success = self.mcp.start_workflow(
            workflow_id=workflow_id,
            context={"test_id": "integration_test"}
        )
        print(f"Workflow started: {success}")
        
        # Get workflow information
        workflow_info = self.mcp.get_workflow(workflow_id)
        print(f"Workflow status: {workflow_info['status']}")
        
        # Verify results
        return (success and workflow_info is not None)
    
    def _test_end_to_end(self):
        """Test end-to-end integration."""
        if not (self.cas and self.llm and self.mcp):
            print("Components not initialized")
            return False
        
        # Step 1: Search for files using CAS
        print("Step 1: Searching for files containing 'documentation'...")
        search_results = self.cas.search("documentation")
        print(f"Found {len(search_results)} results")
        
        if not search_results:
            print("No search results found")
            return False
        
        # Step 2: Use LLM to analyze search results
        print("Step 2: Using LLM to analyze search results...")
        result_text = "\n".join([f"{r.get('filename')}: {r.get('snippet', '')}" for r in search_results[:2]])
        query = f"Analyze these search results about documentation:\n{result_text}"
        
        llm_response = self.llm.process_query(query)
        print(f"LLM analysis: {llm_response[:100]}...")
        
        # Step 3: Use MCP to create a workflow based on the analysis
        print("Step 3: Creating workflow based on analysis...")
        workflow_id = self.mcp.create_workflow(
            name="Documentation Analysis",
            description="Workflow created during end-to-end test"
        )
        
        # Add steps to the workflow
        step1_id = self.mcp.add_workflow_step(
            workflow_id=workflow_id,
            agent_id="search_processor",
            action="search_files",
            parameters={"query": "documentation"}
        )
        
        step2_id = self.mcp.add_workflow_step(
            workflow_id=workflow_id,
            agent_id="query_processor",
            action="summarize",
            parameters={"max_length": 200},
            dependencies=[step1_id]
        )
        
        # Start the workflow
        success = self.mcp.start_workflow(workflow_id)
        print(f"Workflow started: {success}")
        
        # Step 4: Process a command that combines multiple components
        print("Step 4: Processing integrated command...")
        command_result = self.mcp.process_command(
            "Find files about semantic OS and summarize their content"
        )
        print(f"Command result: {command_result}")
        
        # Verify all steps completed successfully
        return (len(search_results) > 0 and 
                len(llm_response) > 100 and 
                success and 
                isinstance(command_result, dict) and 
                command_result.get('status') == 'success')
    
    def _print_summary(self):
        """Print a summary of test results."""
        print("\n=== Integration Test Summary ===")
        
        pass_count = sum(1 for r in self.results if r['status'] == 'PASS')
        fail_count = sum(1 for r in self.results if r['status'] == 'FAIL')
        error_count = sum(1 for r in self.results if r['status'] == 'ERROR')
        
        print(f"Total tests: {len(self.results)}")
        print(f"Passed: {pass_count}")
        print(f"Failed: {fail_count}")
        print(f"Errors: {error_count}")
        
        print("\nTest details:")
        for i, result in enumerate(self.results, 1):
            status_str = result['status']
            if status_str == 'PASS':
                status_str = f"\033[92m{status_str}\033[0m"  # Green
            elif status_str == 'FAIL':
                status_str = f"\033[91m{status_str}\033[0m"  # Red
            else:
                status_str = f"\033[93m{status_str}\033[0m"  # Yellow
            
            print(f"{i}. {result['name']}: {status_str}")
            if 'duration' in result:
                print(f"   Duration: {result['duration']:.2f}s")
            if 'error' in result:
                print(f"   Error: {result['error']}")
    
    def cleanup(self):
        """Clean up the test environment."""
        print("\nCleaning up test environment...")
        
        # Shutdown components
        if self.cas:
            self.cas.stop()
        
        if self.llm:
            self.llm.shutdown()
        
        # Remove test directory
        try:
            shutil.rmtree(self.test_dir)
            print("Test directory removed successfully.")
        except Exception as e:
            print(f"Error removing test directory: {e}")


def main():
    """Main function to run the integration test."""
    integration_test = SemanticOSIntegrationTest()
    
    try:
        # Setup
        integration_test.setup()
        
        # Initialize components
        if not integration_test.initialize_components():
            print("Failed to initialize components. Exiting.")
            return 1
        
        # Run tests
        integration_test.run_tests()
        
        # Check if all tests passed
        pass_count = sum(1 for r in integration_test.results if r['status'] == 'PASS')
        total_count = len(integration_test.results)
        
        if pass_count == total_count:
            print("\nAll integration tests passed!")
            return 0
        else:
            print(f"\n{pass_count} out of {total_count} tests passed.")
            return 1
    except Exception as e:
        print(f"Error during integration test: {e}")
        return 1
    finally:
        # Cleanup
        integration_test.cleanup()


if __name__ == "__main__":
    sys.exit(main())
