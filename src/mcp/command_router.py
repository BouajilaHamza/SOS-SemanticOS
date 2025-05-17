"""
Command Router component for Modular Command Processing.

This component directs user requests to appropriate command processors based on intent.
It analyzes user intent and maps it to registered command processors.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
import re
import threading


class CommandRouter:
    """
    Directs user requests to appropriate command processors based on intent.
    
    This class is responsible for:
    1. Analyzing user intent using the LLM
    2. Mapping intents to registered command processors
    3. Handling ambiguity through clarification requests
    """
    
    def __init__(self, llm_service=None):
        """
        Initialize the CommandRouter.
        
        Args:
            llm_service: Reference to the LLM service for intent analysis
        """
        self.llm_service = llm_service
        self.intent_processors = {}
        self.fallback_processor = None
        self.lock = threading.RLock()
    
    def register_processor(self, intent: str, processor: Callable, priority: int = 0) -> None:
        """
        Register a command processor for a specific intent.
        
        Args:
            intent: Intent string to match
            processor: Function or object to process commands with this intent
            priority: Priority level (higher numbers take precedence)
        """
        with self.lock:
            if intent not in self.intent_processors:
                self.intent_processors[intent] = []
            
            # Add processor with priority
            self.intent_processors[intent].append({
                'processor': processor,
                'priority': priority
            })
            
            # Sort processors by priority (descending)
            self.intent_processors[intent].sort(key=lambda x: x['priority'], reverse=True)
    
    def register_fallback_processor(self, processor: Callable) -> None:
        """
        Register a fallback processor for when no intent matches.
        
        Args:
            processor: Function or object to process unmatched commands
        """
        with self.lock:
            self.fallback_processor = processor
    
    def route_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Route a command to the appropriate processor based on intent.
        
        Args:
            command: User command text
            context: Additional context for command processing
            
        Returns:
            Result from the command processor
        """
        if context is None:
            context = {}
        
        # Extract intent using LLM
        intent_data = self._extract_intent(command, context)
        intent = intent_data.get('intent', '')
        confidence = intent_data.get('confidence', 0.0)
        
        # Find matching processor
        processor = self._find_processor(intent, confidence)
        
        if processor:
            # Process command with the selected processor
            return processor(command, intent_data, context)
        elif self.fallback_processor:
            # Use fallback processor
            return self.fallback_processor(command, intent_data, context)
        else:
            # No processor found
            return {
                'status': 'error',
                'message': f"No processor found for intent '{intent}'"
            }
    
    def _extract_intent(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract intent from a command using the LLM.
        
        Args:
            command: User command text
            context: Additional context
            
        Returns:
            Dictionary containing intent and confidence
        """
        if self.llm_service:
            # Use LLM for intent extraction
            return self.llm_service.extract_intent(command)
        else:
            # Simple rule-based intent extraction as fallback
            return self._rule_based_intent(command)
    
    def _rule_based_intent(self, command: str) -> Dict[str, Any]:
        """
        Simple rule-based intent extraction as fallback.
        
        Args:
            command: User command text
            
        Returns:
            Dictionary containing intent and confidence
        """
        command_lower = command.lower()
        
        # File operations
        if re.search(r"(create|make|new)\s+(file|document)", command_lower):
            return {"intent": "create_file", "confidence": 0.8}
        elif re.search(r"(open|view|show|display)\s+file", command_lower):
            return {"intent": "open_file", "confidence": 0.8}
        elif re.search(r"(delete|remove)\s+file", command_lower):
            return {"intent": "delete_file", "confidence": 0.8}
        elif re.search(r"(move|copy)\s+file", command_lower):
            return {"intent": "move_file", "confidence": 0.7}
        
        # Search operations
        elif re.search(r"(find|search|locate)\s+file", command_lower):
            return {"intent": "search_files", "confidence": 0.9}
        elif re.search(r"(find|search)\s+for", command_lower):
            return {"intent": "search_content", "confidence": 0.7}
        
        # System operations
        elif re.search(r"(system|os)\s+(status|info)", command_lower):
            return {"intent": "system_info", "confidence": 0.8}
        
        # Default: general query
        else:
            return {"intent": "general_query", "confidence": 0.5}
    
    def _find_processor(self, intent: str, confidence: float) -> Optional[Callable]:
        """
        Find the appropriate processor for an intent.
        
        Args:
            intent: Intent string
            confidence: Confidence score for the intent
            
        Returns:
            Processor function or None if no suitable processor is found
        """
        with self.lock:
            # Check if we have processors for this intent
            if intent in self.intent_processors and self.intent_processors[intent]:
                # Get the highest priority processor
                return self.intent_processors[intent][0]['processor']
            
            # No processor found for this intent
            return None
    
    def list_registered_intents(self) -> List[str]:
        """
        Get a list of all registered intents.
        
        Returns:
            List of intent strings
        """
        with self.lock:
            return list(self.intent_processors.keys())
