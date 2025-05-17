"""
MCP Demo script for testing the Modular Command Processing framework.

This script demonstrates the basic usage of the MCP framework by:
1. Initializing the MCP with LLM and CAS services
2. Registering command processors and agents
3. Processing sample commands
4. Creating and executing a simple workflow
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.mcp_api import ModularCommandProcessing
from llm.llm_api import LocalLLM
from cas.cas_api import ContentAwareStorage


class MCPDemo:
    """Demo class to showcase the MCP framework with LLM and CAS integration."""
    
    def __init__(self):
        """Initialize the demo."""
        # Define directories
        self.home_dir = str(Path.home())
        self.storage_dir = os.path.join(self.home_dir, ".semantic_os")
        
        # Initialize components
        self.llm = None
        self.cas = None
        self.mcp = None
        
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
        
        # Initialize MCP
        print("Setting up modular command processing...")
        self.mcp = ModularCommandProcessing(
            os.path.join(self.storage_dir, "mcp"),
            llm_service=self.llm,
            cas_service=self.cas
        )
        
        # Initialize default processors
        self.mcp.initialize_default_processors()
        
        print("Semantic OS initialized successfully.")
    
    def demonstrate_command_processing(self):
        """Demonstrate command processing."""
        print("\n=== Command Processing Demo ===")
        
        # Process a file operation command
        print("\nProcessing file operation command:")
        result = self.mcp.process_command("Create a new file called notes.txt")
        print(f"Result: {result}")
        
        # Process a search command
        print("\nProcessing search command:")
        result = self.mcp.process_command("Find files related to python")
        print(f"Result: {result}")
        
        # Process a system info command
        print("\nProcessing system info command:")
        result = self.mcp.process_command("Show system information")
        print(f"Result: {result}")
        
        # Process a general query
        print("\nProcessing general query:")
        result = self.mcp.process_command("What is semantic computing?")
        print(f"Result: {result}")
    
    def demonstrate_agent_registry(self):
        """Demonstrate agent registry."""
        print("\n=== Agent Registry Demo ===")
        
        # Register a custom agent
        print("\nRegistering custom agent:")
        success = self.mcp.register_agent(
            "custom_agent",
            {
                'name': 'Custom Agent',
                'version': '0.1.0',
                'description': 'A custom agent for demonstration',
                'capabilities': ['custom_capability']
            }
        )
        print(f"Registration successful: {success}")
        
        # List all agents
        print("\nListing all agents:")
        agents = self.mcp.list_agents()
        for agent in agents:
            print(f"- {agent['name']} ({agent['id']}): {agent['description']}")
        
        # Find agents by capability
        print("\nFinding agents with search capability:")
        search_agents = self.mcp.find_agents_by_capability('search_files')
        for agent in search_agents:
            print(f"- {agent['name']} ({agent['id']})")
    
    def demonstrate_messaging(self):
        """Demonstrate agent-to-agent messaging."""
        print("\n=== Messaging Demo ===")
        
        # Set up message handler
        def message_handler(message):
            print(f"Received message: {message.topic} from {message.sender}")
            print(f"Content: {message.content}")
        
        # Subscribe to messages
        print("\nSubscribing to messages:")
        self.mcp.subscribe_to_messages("custom_agent", message_handler)
        print("Subscribed custom_agent to receive messages")
        
        # Send a message
        print("\nSending message:")
        message_id = self.mcp.send_message(
            sender="mcp_core",
            recipients=["custom_agent"],
            topic="greeting",
            content={"text": "Hello, agent!"}
        )
        print(f"Message sent with ID: {message_id}")
    
    def demonstrate_workflow(self):
        """Demonstrate workflow creation and execution."""
        print("\n=== Workflow Demo ===")
        
        # Create a workflow
        print("\nCreating workflow:")
        workflow_id = self.mcp.create_workflow(
            name="Demo Workflow",
            description="A simple workflow for demonstration"
        )
        print(f"Created workflow with ID: {workflow_id}")
        
        # Add steps to the workflow
        print("\nAdding workflow steps:")
        
        # Step 1: Search for files
        step1_id = self.mcp.add_workflow_step(
            workflow_id=workflow_id,
            agent_id="search_processor",
            action="search_files",
            parameters={"query": "python"}
        )
        print(f"Added search step with ID: {step1_id}")
        
        # Step 2: Process search results
        step2_id = self.mcp.add_workflow_step(
            workflow_id=workflow_id,
            agent_id="query_processor",
            action="analyze_results",
            parameters={"max_results": 5},
            dependencies=[step1_id]
        )
        print(f"Added analysis step with ID: {step2_id}")
        
        # Start the workflow
        print("\nStarting workflow:")
        success = self.mcp.start_workflow(
            workflow_id=workflow_id,
            context={"user_id": "demo_user"}
        )
        print(f"Workflow started: {success}")
        
        # Get workflow information
        print("\nWorkflow information:")
        workflow_info = self.mcp.get_workflow(workflow_id)
        if workflow_info:
            print(f"Name: {workflow_info['name']}")
            print(f"Status: {workflow_info['status']}")
            print(f"Steps: {len(workflow_info['steps'])}")
    
    def shutdown(self):
        """Shut down all components."""
        print("\nShutting down Semantic OS...")
        
        # Stop CAS
        if self.cas:
            self.cas.stop()
        
        # Unload LLM
        if self.llm:
            self.llm.shutdown()
        
        print("Semantic OS shut down successfully.")


def main():
    """Main function to run the demo."""
    demo = MCPDemo()
    
    try:
        demo.initialize()
        
        # Run demonstrations
        demo.demonstrate_command_processing()
        demo.demonstrate_agent_registry()
        demo.demonstrate_messaging()
        demo.demonstrate_workflow()
        
        print("\nMCP demonstration completed successfully.")
    except Exception as e:
        print(f"\nError during demonstration: {e}")
    finally:
        demo.shutdown()


if __name__ == "__main__":
    main()
