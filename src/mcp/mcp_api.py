"""
Modular Command Processing (MCP) API for Semantic OS.

This module provides a unified interface for the modular command processing framework.
It integrates the command router, agent registry, message bus, and workflow engine.
"""

from typing import Dict, List, Any, Optional, Callable, Union
import threading
from pathlib import Path

from .command_router import CommandRouter
from .agent_registry import AgentRegistry
from .message_bus import MessageBus, Message
from .command_processor import CommandProcessor, BaseCommandProcessor
from .workflow_engine import WorkflowEngine, WorkflowStatus, StepStatus


class ModularCommandProcessing:
    """
    Unified API for the Modular Command Processing framework.
    
    This class integrates the command router, agent registry, message bus,
    and workflow engine to provide a comprehensive interface for modular
    command processing and agent-to-agent communication.
    """
    
    def __init__(self, storage_dir: str, llm_service=None, cas_service=None):
        """
        Initialize the Modular Command Processing framework.
        
        Args:
            storage_dir: Directory to store MCP data
            llm_service: Reference to the LLM service
            cas_service: Reference to the Content-Aware Storage service
        """
        self.storage_dir = Path(storage_dir).expanduser().absolute()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.message_bus = MessageBus()
        self.agent_registry = AgentRegistry(str(self.storage_dir / "agents"))
        self.command_router = CommandRouter(llm_service)
        self.workflow_engine = WorkflowEngine(
            self.message_bus,
            str(self.storage_dir / "workflows")
        )
        
        # Store service references
        self.llm_service = llm_service
        self.cas_service = cas_service
        
        # Register as an agent
        self.agent_id = "mcp_core"
        self.register_agent(
            self.agent_id,
            {
                'name': 'MCP Core',
                'version': '0.1.0',
                'description': 'Core MCP agent for Semantic OS',
                'capabilities': ['command_routing', 'workflow_management']
            }
        )
        
        # Subscribe to messages
        self.message_bus.subscribe(self.agent_id, self._handle_message)
    
    def register_agent(self, agent_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Register an agent with the system.
        
        Args:
            agent_id: Unique identifier for the agent
            metadata: Dictionary of agent metadata
            
        Returns:
            True if successful, False otherwise
        """
        return self.agent_registry.register_agent(agent_id, metadata)
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the system.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            True if successful, False otherwise
        """
        return self.agent_registry.unregister_agent(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Get a list of all registered agents.
        
        Returns:
            List of agent metadata dictionaries
        """
        return self.agent_registry.list_agents()
    
    def find_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Find agents that provide a specific capability.
        
        Args:
            capability: Capability string to search for
            
        Returns:
            List of matching agent metadata dictionaries
        """
        return self.agent_registry.find_agents_by_capability(capability)
    
    def register_command_processor(self, intent: str, processor: Union[CommandProcessor, Callable], priority: int = 0) -> None:
        """
        Register a command processor for a specific intent.
        
        Args:
            intent: Intent string to match
            processor: Function or object to process commands with this intent
            priority: Priority level (higher numbers take precedence)
        """
        self.command_router.register_processor(intent, processor, priority)
    
    def register_fallback_processor(self, processor: Union[CommandProcessor, Callable]) -> None:
        """
        Register a fallback processor for when no intent matches.
        
        Args:
            processor: Function or object to process unmatched commands
        """
        self.command_router.register_fallback_processor(processor)
    
    def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Process a command using the command router.
        
        Args:
            command: Command text
            context: Additional context for command processing
            
        Returns:
            Processing result
        """
        return self.command_router.route_command(command, context)
    
    def send_message(self, sender: str, recipients: List[str], topic: str, content: Any) -> str:
        """
        Send a message to one or more agents.
        
        Args:
            sender: ID of the sending agent
            recipients: IDs of recipient agents
            topic: Message topic
            content: Message content
            
        Returns:
            Message ID
        """
        message = Message(
            sender=sender,
            recipients=recipients,
            topic=topic,
            content=content
        )
        
        return self.message_bus.publish(message)
    
    def subscribe_to_messages(self, agent_id: str, callback: Callable[[Message], None]) -> None:
        """
        Subscribe an agent to receive messages addressed to it.
        
        Args:
            agent_id: ID of the subscribing agent
            callback: Function to call when a message is received
        """
        self.message_bus.subscribe(agent_id, callback)
    
    def unsubscribe_from_messages(self, agent_id: str, callback: Optional[Callable[[Message], None]] = None) -> None:
        """
        Unsubscribe an agent from receiving messages.
        
        Args:
            agent_id: ID of the agent to unsubscribe
            callback: Specific callback to remove (None to remove all)
        """
        self.message_bus.unsubscribe(agent_id, callback)
    
    def subscribe_to_topic(self, topic: str, callback: Callable[[Message], None]) -> None:
        """
        Subscribe to a topic to receive all messages on that topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when a message is received
        """
        self.message_bus.subscribe_to_topic(topic, callback)
    
    def unsubscribe_from_topic(self, topic: str, callback: Optional[Callable[[Message], None]] = None) -> None:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            callback: Specific callback to remove (None to remove all)
        """
        self.message_bus.unsubscribe_from_topic(topic, callback)
    
    def create_workflow(self, name: str, description: str = "") -> str:
        """
        Create a new workflow.
        
        Args:
            name: Name of the workflow
            description: Description of the workflow
            
        Returns:
            Workflow ID
        """
        return self.workflow_engine.create_workflow(name, description)
    
    def add_workflow_step(self, workflow_id: str, agent_id: str, action: str,
                        parameters: Dict[str, Any] = None, dependencies: List[str] = None) -> str:
        """
        Add a step to a workflow.
        
        Args:
            workflow_id: ID of the workflow
            agent_id: ID of the agent responsible for this step
            action: Action to perform
            parameters: Parameters for the action
            dependencies: IDs of steps that must complete before this one
            
        Returns:
            Step ID
        """
        return self.workflow_engine.add_step(workflow_id, agent_id, action, parameters, dependencies)
    
    def start_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> bool:
        """
        Start a workflow.
        
        Args:
            workflow_id: ID of the workflow to start
            context: Initial context for the workflow
            
        Returns:
            True if successful, False otherwise
        """
        return self.workflow_engine.start_workflow(workflow_id, context)
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a workflow.
        
        Args:
            workflow_id: ID of the workflow to cancel
            
        Returns:
            True if successful, False otherwise
        """
        return self.workflow_engine.cancel_workflow(workflow_id)
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow information or None if not found
        """
        return self.workflow_engine.get_workflow(workflow_id)
    
    def list_workflows(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List workflows.
        
        Args:
            status: Filter by status string
            
        Returns:
            List of workflow information dictionaries
        """
        workflow_status = None
        if status:
            try:
                workflow_status = WorkflowStatus(status)
            except ValueError:
                pass
                
        return self.workflow_engine.list_workflows(workflow_status)
    
    def _handle_message(self, message: Message) -> None:
        """
        Handle a message addressed to the MCP core.
        
        Args:
            message: Message to handle
        """
        # This is a placeholder for handling core MCP messages
        # In a real implementation, this would handle various administrative messages
        pass
    
    def initialize_default_processors(self) -> None:
        """Initialize default command processors."""
        from .command_processor import FileOperationProcessor, SearchProcessor, GeneralQueryProcessor, SystemInfoProcessor
        
        # Create processors
        file_processor = FileOperationProcessor(self.cas_service)
        search_processor = SearchProcessor(self.cas_service)
        query_processor = GeneralQueryProcessor(self.llm_service)
        system_processor = SystemInfoProcessor(self.cas_service, self.llm_service)
        
        # Register processors
        for intent in ['create_file', 'open_file', 'delete_file', 'move_file']:
            self.register_command_processor(intent, file_processor.process)
        
        for intent in ['search_files', 'search_content']:
            self.register_command_processor(intent, search_processor.process)
        
        self.register_command_processor('system_info', system_processor.process)
        
        # Register fallback processor
        self.register_fallback_processor(query_processor.process)
        
        # Register agents for processors
        self.register_agent(
            'file_processor',
            {
                'name': 'File Operation Processor',
                'version': '0.1.0',
                'description': 'Handles file operations',
                'capabilities': ['create_file', 'open_file', 'delete_file', 'move_file']
            }
        )
        
        self.register_agent(
            'search_processor',
            {
                'name': 'Search Processor',
                'version': '0.1.0',
                'description': 'Handles search operations',
                'capabilities': ['search_files', 'search_content']
            }
        )
        
        self.register_agent(
            'query_processor',
            {
                'name': 'General Query Processor',
                'version': '0.1.0',
                'description': 'Handles general queries using the LLM',
                'capabilities': ['general_query']
            }
        )
        
        self.register_agent(
            'system_processor',
            {
                'name': 'System Information Processor',
                'version': '0.1.0',
                'description': 'Provides system information',
                'capabilities': ['system_info']
            }
        )
