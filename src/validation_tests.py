"""
Validation Test Suite for Semantic OS.

This script performs comprehensive validation tests for all Semantic OS components:
1. Content-Aware Storage (CAS)
2. Local LLM Integration
3. Natural Language Interface
4. Modular Command Processing (MCP) and Agent-to-Agent (A2A) Communication
5. End-to-end integration tests
"""

import os
import sys
import time
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from cas.cas_api import ContentAwareStorage
from llm.llm_api import LocalLLM
from interface.interface_api import NaturalLanguageInterface
from mcp.mcp_api import ModularCommandProcessing


class SemanticOSValidationTests(unittest.TestCase):
    """Test suite for validating Semantic OS components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        print("Setting up test environment...")
        
        # Create temporary directories
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_files_dir = os.path.join(cls.temp_dir, "test_files")
        cls.storage_dir = os.path.join(cls.temp_dir, "semantic_os")
        
        os.makedirs(cls.test_files_dir, exist_ok=True)
        os.makedirs(cls.storage_dir, exist_ok=True)
        
        # Create test files
        cls._create_test_files()
        
        # Initialize components
        cls._initialize_components()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        print("Cleaning up test environment...")
        
        # Shutdown components
        if hasattr(cls, 'cas') and cls.cas:
            cls.cas.stop()
        
        if hasattr(cls, 'llm') and cls.llm:
            cls.llm.shutdown()
        
        # Remove temporary directory
        shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def _create_test_files(cls):
        """Create test files for validation."""
        # Create a Python file
        with open(os.path.join(cls.test_files_dir, "example.py"), "w") as f:
            f.write("""
# Example Python file
def hello_world():
    print("Hello, Semantic OS!")

if __name__ == "__main__":
    hello_world()
""")
        
        # Create a Markdown file
        with open(os.path.join(cls.test_files_dir, "notes.md"), "w") as f:
            f.write("""
# Semantic OS Notes

## Features
- Content-Aware Storage
- Local LLM Integration
- Natural Language Interface
- Modular Command Processing

## TODO
- Complete validation
- Write documentation
""")
        
        # Create a text file
        with open(os.path.join(cls.test_files_dir, "data.txt"), "w") as f:
            f.write("""
This is a sample text file for testing the Semantic OS.
It contains some keywords like Python, LLM, and semantic computing.
""")
    
    @classmethod
    def _initialize_components(cls):
        """Initialize Semantic OS components for testing."""
        try:
            # Initialize CAS
            print("Initializing Content-Aware Storage...")
            cls.cas = ContentAwareStorage(
                [cls.test_files_dir],
                os.path.join(cls.storage_dir, "cas")
            )
            cls.cas.start()
            
            # Initialize LLM
            print("Initializing Local LLM...")
            cls.llm = LocalLLM(
                os.path.join(cls.storage_dir, "llm"),
                model_name="microsoft/phi-2"
            )
            cls.llm.initialize(quantize=True)
            
            # Initialize MCP
            print("Initializing Modular Command Processing...")
            cls.mcp = ModularCommandProcessing(
                os.path.join(cls.storage_dir, "mcp"),
                llm_service=cls.llm,
                cas_service=cls.cas
            )
            cls.mcp.initialize_default_processors()
            
            print("Components initialized successfully.")
        except Exception as e:
            print(f"Error initializing components: {e}")
            raise
    
    def test_cas_indexing(self):
        """Test CAS file indexing functionality."""
        print("\nTesting CAS indexing...")
        
        # Wait for indexing to complete
        time.sleep(2)
        
        # Get statistics
        stats = self.cas.get_statistics()
        
        # Verify files were indexed
        self.assertGreater(stats['total_files'], 0, "No files were indexed")
        self.assertEqual(len(stats['monitored_directories']), 1, "Wrong number of monitored directories")
        self.assertIn(self.test_files_dir, stats['monitored_directories'], "Test directory not monitored")
        
        print(f"CAS indexed {stats['total_files']} files successfully.")
    
    def test_cas_search(self):
        """Test CAS search functionality."""
        print("\nTesting CAS search...")
        
        # Search for Python
        python_results = self.cas.search("Python")
        self.assertGreater(len(python_results), 0, "No results found for 'Python'")
        
        # Search for Semantic
        semantic_results = self.cas.search("Semantic")
        self.assertGreater(len(semantic_results), 0, "No results found for 'Semantic'")
        
        # Search for nonexistent term
        nonexistent_results = self.cas.search("nonexistentterm123456789")
        self.assertEqual(len(nonexistent_results), 0, "Results found for nonexistent term")
        
        print(f"CAS search returned {len(python_results)} results for 'Python' and {len(semantic_results)} results for 'Semantic'.")
    
    def test_llm_query_processing(self):
        """Test LLM query processing."""
        print("\nTesting LLM query processing...")
        
        # Process a simple query
        query = "What is semantic computing?"
        response = self.llm.process_query(query)
        
        # Verify response
        self.assertIsInstance(response, str, "Response is not a string")
        self.assertGreater(len(response), 50, "Response is too short")
        
        print(f"LLM processed query successfully. Response length: {len(response)} characters.")
    
    def test_llm_intent_extraction(self):
        """Test LLM intent extraction."""
        print("\nTesting LLM intent extraction...")
        
        # Extract intent from a file operation query
        file_query = "Create a new file called test.txt"
        file_intent = self.llm.extract_intent(file_query)
        
        # Extract intent from a search query
        search_query = "Find files related to Python"
        search_intent = self.llm.extract_intent(search_query)
        
        # Verify intents
        self.assertIsInstance(file_intent, dict, "File intent is not a dictionary")
        self.assertIsInstance(search_intent, dict, "Search intent is not a dictionary")
        
        print(f"LLM extracted intents successfully: {file_intent.get('intent')} and {search_intent.get('intent')}.")
    
    def test_mcp_command_routing(self):
        """Test MCP command routing."""
        print("\nTesting MCP command routing...")
        
        # Process a search command
        search_result = self.mcp.process_command("Find files about Python")
        
        # Process a system info command
        system_result = self.mcp.process_command("Show system information")
        
        # Verify results
        self.assertIsInstance(search_result, dict, "Search result is not a dictionary")
        self.assertIsInstance(system_result, dict, "System result is not a dictionary")
        
        self.assertEqual(search_result.get('status'), 'success', "Search command failed")
        self.assertEqual(system_result.get('status'), 'success', "System command failed")
        
        print("MCP command routing working correctly.")
    
    def test_mcp_agent_registry(self):
        """Test MCP agent registry."""
        print("\nTesting MCP agent registry...")
        
        # Register a test agent
        success = self.mcp.register_agent(
            "test_agent",
            {
                'name': 'Test Agent',
                'version': '0.1.0',
                'description': 'Agent for testing',
                'capabilities': ['test_capability']
            }
        )
        
        # List agents
        agents = self.mcp.list_agents()
        
        # Find agents by capability
        test_agents = self.mcp.find_agents_by_capability('test_capability')
        
        # Verify results
        self.assertTrue(success, "Agent registration failed")
        self.assertGreater(len(agents), 0, "No agents found")
        self.assertEqual(len(test_agents), 1, "Test agent not found by capability")
        
        print(f"MCP agent registry working correctly. Found {len(agents)} agents.")
    
    def test_mcp_messaging(self):
        """Test MCP messaging system."""
        print("\nTesting MCP messaging...")
        
        # Set up message handler
        self.received_message = None
        
        def message_handler(message):
            self.received_message = message
        
        # Subscribe to messages
        self.mcp.subscribe_to_messages("test_agent", message_handler)
        
        # Send a message
        message_id = self.mcp.send_message(
            sender="mcp_core",
            recipients=["test_agent"],
            topic="test",
            content={"text": "Test message"}
        )
        
        # Wait for message delivery
        time.sleep(0.5)
        
        # Verify message
        self.assertIsNotNone(self.received_message, "Message not received")
        self.assertEqual(self.received_message.sender, "mcp_core", "Wrong sender")
        self.assertEqual(self.received_message.topic, "test", "Wrong topic")
        
        print("MCP messaging working correctly.")
    
    def test_mcp_workflow(self):
        """Test MCP workflow engine."""
        print("\nTesting MCP workflow engine...")
        
        # Create a workflow
        workflow_id = self.mcp.create_workflow(
            name="Test Workflow",
            description="Workflow for testing"
        )
        
        # Add a step
        step_id = self.mcp.add_workflow_step(
            workflow_id=workflow_id,
            agent_id="search_processor",
            action="search_files",
            parameters={"query": "Python"}
        )
        
        # Get workflow
        workflow = self.mcp.get_workflow(workflow_id)
        
        # Verify workflow
        self.assertIsNotNone(workflow, "Workflow not found")
        self.assertEqual(workflow['name'], "Test Workflow", "Wrong workflow name")
        self.assertIn(step_id, workflow['steps'], "Step not found in workflow")
        
        print("MCP workflow engine working correctly.")
    
    def test_integration_search_to_llm(self):
        """Test integration between CAS search and LLM."""
        print("\nTesting CAS-LLM integration...")
        
        # Search for files
        search_results = self.cas.search("Python")
        
        # Use LLM to analyze results
        if search_results:
            result_text = "\n".join([f"{r.get('filename')}: {r.get('snippet', '')}" for r in search_results[:3]])
            query = f"Analyze these search results about Python:\n{result_text}"
            
            response = self.llm.process_query(query)
            
            # Verify response
            self.assertIsInstance(response, str, "Response is not a string")
            self.assertGreater(len(response), 50, "Response is too short")
            
            print("CAS-LLM integration working correctly.")
        else:
            self.skipTest("No search results to analyze")
    
    def test_integration_mcp_to_cas(self):
        """Test integration between MCP and CAS."""
        print("\nTesting MCP-CAS integration...")
        
        # Use MCP to process a search command
        result = self.mcp.process_command("Find files containing semantic")
        
        # Verify result
        self.assertIsInstance(result, dict, "Result is not a dictionary")
        self.assertEqual(result.get('status'), 'success', "Command failed")
        self.assertIn('results', result, "No results in response")
        
        print("MCP-CAS integration working correctly.")
    
    def test_integration_mcp_to_llm(self):
        """Test integration between MCP and LLM."""
        print("\nTesting MCP-LLM integration...")
        
        # Use MCP to process a general query
        result = self.mcp.process_command("Explain what a semantic operating system is")
        
        # Verify result
        self.assertIsInstance(result, dict, "Result is not a dictionary")
        self.assertEqual(result.get('status'), 'success', "Command failed")
        self.assertIn('message', result, "No message in response")
        self.assertGreater(len(result.get('message', '')), 50, "Response is too short")
        
        print("MCP-LLM integration working correctly.")


def run_tests():
    """Run the validation tests."""
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SemanticOSValidationTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
