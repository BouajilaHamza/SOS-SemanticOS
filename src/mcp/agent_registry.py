"""
Agent Registry component for Modular Command Processing.

This component maintains a registry of available agents and their capabilities.
It provides dynamic registration and discovery of agents.
"""

from typing import Dict, List, Any, Optional, Set
import threading
import json
import time
from pathlib import Path


class AgentRegistry:
    """
    Maintains a registry of available agents and their capabilities.
    
    This class is responsible for:
    1. Providing dynamic registration and discovery of agents
    2. Managing agent metadata and capability descriptions
    3. Implementing versioning and dependency resolution
    """
    
    def __init__(self, registry_dir: str = None):
        """
        Initialize the AgentRegistry.
        
        Args:
            registry_dir: Directory to store registry data
        """
        self.agents = {}
        self.lock = threading.RLock()
        self.registry_dir = None
        
        if registry_dir:
            self.registry_dir = Path(registry_dir).expanduser().absolute()
            self.registry_dir.mkdir(parents=True, exist_ok=True)
            self._load_registry()
    
    def register_agent(self, agent_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Register an agent with the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            metadata: Dictionary of agent metadata
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            # Validate required metadata
            required_fields = ['name', 'version', 'capabilities']
            for field in required_fields:
                if field not in metadata:
                    print(f"Error registering agent: Missing required field '{field}'")
                    return False
            
            # Add registration timestamp
            metadata['registered_at'] = time.time()
            
            # Store agent metadata
            self.agents[agent_id] = metadata
            
            # Save registry if directory is specified
            if self.registry_dir:
                self._save_registry()
            
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
                
                # Save registry if directory is specified
                if self.registry_dir:
                    self._save_registry()
                
                return True
            return False
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific agent.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            Agent metadata or None if not found
        """
        with self.lock:
            return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Get a list of all registered agents.
        
        Returns:
            List of agent metadata dictionaries
        """
        with self.lock:
            return [
                {'id': agent_id, **metadata}
                for agent_id, metadata in self.agents.items()
            ]
    
    def find_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Find agents that provide a specific capability.
        
        Args:
            capability: Capability string to search for
            
        Returns:
            List of matching agent metadata dictionaries
        """
        with self.lock:
            matching_agents = []
            
            for agent_id, metadata in self.agents.items():
                capabilities = metadata.get('capabilities', [])
                
                if capability in capabilities:
                    matching_agents.append({'id': agent_id, **metadata})
            
            return matching_agents
    
    def find_agents_by_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find agents matching a query.
        
        Args:
            query: Dictionary of query criteria
            
        Returns:
            List of matching agent metadata dictionaries
        """
        with self.lock:
            matching_agents = []
            
            for agent_id, metadata in self.agents.items():
                match = True
                
                for key, value in query.items():
                    if key == 'capabilities':
                        # Check if agent has all required capabilities
                        agent_capabilities = set(metadata.get('capabilities', []))
                        required_capabilities = set(value if isinstance(value, list) else [value])
                        
                        if not required_capabilities.issubset(agent_capabilities):
                            match = False
                            break
                    elif key not in metadata or metadata[key] != value:
                        match = False
                        break
                
                if match:
                    matching_agents.append({'id': agent_id, **metadata})
            
            return matching_agents
    
    def update_agent_metadata(self, agent_id: str, metadata_updates: Dict[str, Any]) -> bool:
        """
        Update metadata for an agent.
        
        Args:
            agent_id: Unique identifier for the agent
            metadata_updates: Dictionary of metadata updates
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            # Update metadata
            self.agents[agent_id].update(metadata_updates)
            
            # Add update timestamp
            self.agents[agent_id]['updated_at'] = time.time()
            
            # Save registry if directory is specified
            if self.registry_dir:
                self._save_registry()
            
            return True
    
    def _save_registry(self) -> bool:
        """
        Save the registry to disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            registry_file = self.registry_dir / 'agent_registry.json'
            
            with open(registry_file, 'w') as f:
                json.dump(self.agents, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving registry: {e}")
            return False
    
    def _load_registry(self) -> bool:
        """
        Load the registry from disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            registry_file = self.registry_dir / 'agent_registry.json'
            
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    self.agents = json.load(f)
                
                return True
            return False
        except Exception as e:
            print(f"Error loading registry: {e}")
            return False
