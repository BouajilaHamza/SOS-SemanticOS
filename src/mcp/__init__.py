"""
Modular Command Processing (MCP) module for Semantic OS.

This module provides a framework for extensible command processing and
agent-to-agent communication, enabling a plugin-based architecture.
"""

from .command_router import CommandRouter
from .agent_registry import AgentRegistry
from .message_bus import MessageBus
from .command_processor import CommandProcessor, BaseCommandProcessor
from .workflow_engine import WorkflowEngine
from .mcp_api import ModularCommandProcessing

__all__ = [
    'CommandRouter', 'AgentRegistry', 'MessageBus', 
    'CommandProcessor', 'BaseCommandProcessor', 
    'WorkflowEngine', 'ModularCommandProcessing'
]
