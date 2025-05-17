"""
Prompt Engineer component for Local LLM Integration.

This component constructs effective prompts for the LLM based on user input and system state.
It formats prompts according to model-specific requirements and incorporates system context.
"""

from typing import Dict, List, Any, Optional, Union
import re


class PromptEngineer:
    """
    Constructs effective prompts for the LLM based on user input and system state.
    
    This class is responsible for:
    1. Formatting prompts according to model-specific requirements
    2. Incorporating system context and constraints
    3. Implementing techniques to improve response quality and relevance
    """
    
    def __init__(self, model_name: str = "microsoft/phi-2"):
        """
        Initialize the PromptEngineer.
        
        Args:
            model_name: Name of the model to format prompts for
        """
        self.model_name = model_name
        self.system_instructions = self._get_default_system_instructions()
        
    def _get_default_system_instructions(self) -> str:
        """
        Get default system instructions for the model.
        
        Returns:
            Default system instructions
        """
        return (
            "You are an AI assistant for a Semantic Operating System. "
            "Your role is to help users manage files and execute tasks using natural language. "
            "You can understand file content, context, and relationships between files. "
            "Respond concisely and accurately to user queries about files and system operations."
        )
    
    def set_system_instructions(self, instructions: str):
        """
        Set custom system instructions.
        
        Args:
            instructions: Custom system instructions
        """
        self.system_instructions = instructions
    
    def format_prompt(self, 
                      user_input: str, 
                      conversation_history: Optional[List[Dict[str, str]]] = None,
                      system_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a prompt for the model based on user input and context.
        
        Args:
            user_input: User input text
            conversation_history: Previous conversation turns
            system_context: Additional system context
            
        Returns:
            Formatted prompt string
        """
        # Use model-specific formatting
        if "phi" in self.model_name.lower():
            return self._format_phi_prompt(user_input, conversation_history, system_context)
        elif "llama" in self.model_name.lower():
            return self._format_llama_prompt(user_input, conversation_history, system_context)
        else:
            # Default formatting for other models
            return self._format_default_prompt(user_input, conversation_history, system_context)
    
    def _format_phi_prompt(self, 
                          user_input: str, 
                          conversation_history: Optional[List[Dict[str, str]]] = None,
                          system_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a prompt specifically for Phi models.
        
        Args:
            user_input: User input text
            conversation_history: Previous conversation turns
            system_context: Additional system context
            
        Returns:
            Formatted prompt string
        """
        # Start with system instructions
        instructions = system_context.get("instructions", self.system_instructions) if system_context else self.system_instructions
        prompt = f"<|system|>\n{instructions}\n<|end|>\n"
        
        # Add conversation history if provided
        if conversation_history:
            for message in conversation_history:
                role = message["role"]
                content = message["content"]
                
                if role == "system":
                    # Skip system messages in history as we've already added instructions
                    continue
                elif role == "user":
                    prompt += f"<|user|>\n{content}\n<|end|>\n"
                elif role == "assistant":
                    prompt += f"<|assistant|>\n{content}\n<|end|>\n"
        
        # Add current user input
        prompt += f"<|user|>\n{user_input}\n<|end|>\n"
        
        # Add assistant prefix to indicate where the model should start generating
        prompt += "<|assistant|>\n"
        
        return prompt
    
    def _format_llama_prompt(self, 
                           user_input: str, 
                           conversation_history: Optional[List[Dict[str, str]]] = None,
                           system_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a prompt specifically for LLaMA models.
        
        Args:
            user_input: User input text
            conversation_history: Previous conversation turns
            system_context: Additional system context
            
        Returns:
            Formatted prompt string
        """
        # Start with system instructions
        instructions = system_context.get("instructions", self.system_instructions) if system_context else self.system_instructions
        prompt = f"<s>[INST] <<SYS>>\n{instructions}\n<</SYS>>\n\n"
        
        # Add conversation history if provided
        if conversation_history:
            history_text = ""
            for i, message in enumerate(conversation_history):
                role = message["role"]
                content = message["content"]
                
                if role == "system":
                    # Skip system messages in history as we've already added instructions
                    continue
                elif role == "user":
                    if i > 0:  # Not the first message
                        history_text += f"[/INST]\n\n{previous_assistant_msg}\n\n[INST] {content} "
                    else:
                        history_text += f"{content} "
                    previous_user_msg = content
                elif role == "assistant":
                    previous_assistant_msg = content
            
            prompt += history_text
        
        # Add current user input
        if conversation_history and any(msg["role"] == "user" for msg in conversation_history):
            prompt += f"[/INST]\n\n{previous_assistant_msg}\n\n[INST] {user_input} [/INST]\n\n"
        else:
            prompt += f"{user_input} [/INST]\n\n"
        
        return prompt
    
    def _format_default_prompt(self, 
                             user_input: str, 
                             conversation_history: Optional[List[Dict[str, str]]] = None,
                             system_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a prompt using a generic format for most models.
        
        Args:
            user_input: User input text
            conversation_history: Previous conversation turns
            system_context: Additional system context
            
        Returns:
            Formatted prompt string
        """
        # Start with system instructions
        instructions = system_context.get("instructions", self.system_instructions) if system_context else self.system_instructions
        prompt = f"System: {instructions}\n\n"
        
        # Add conversation history if provided
        if conversation_history:
            for message in conversation_history:
                role = message["role"]
                content = message["content"]
                
                if role == "system":
                    # Skip system messages in history as we've already added instructions
                    continue
                elif role == "user":
                    prompt += f"User: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
        
        # Add current user input
        prompt += f"User: {user_input}\n"
        prompt += "Assistant: "
        
        return prompt
    
    def create_file_operation_prompt(self, 
                                    operation: str, 
                                    file_path: str, 
                                    additional_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a specialized prompt for file operations.
        
        Args:
            operation: Type of file operation (e.g., "create", "move", "delete")
            file_path: Path of the file to operate on
            additional_context: Additional context for the operation
            
        Returns:
            Specialized prompt for file operations
        """
        context = f"I need to {operation} the file at {file_path}."
        
        if additional_context:
            if "content" in additional_context:
                context += f" The file contains: {additional_context['content'][:100]}..."
            if "metadata" in additional_context:
                metadata = additional_context["metadata"]
                context += f" File metadata: {', '.join([f'{k}={v}' for k, v in metadata.items()][:5])}"
        
        return context
    
    def create_search_prompt(self, 
                           query: str, 
                           search_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a specialized prompt for search operations.
        
        Args:
            query: Search query
            search_context: Additional context for the search
            
        Returns:
            Specialized prompt for search operations
        """
        context = f"I want to find files related to: {query}."
        
        if search_context:
            if "file_types" in search_context:
                context += f" File types: {', '.join(search_context['file_types'])}."
            if "date_range" in search_context:
                context += f" Time period: {search_context['date_range']}."
            if "location" in search_context:
                context += f" Look in: {search_context['location']}."
        
        return context
    
    def extract_command_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Extract command intent from user input.
        
        Args:
            user_input: User input text
            
        Returns:
            Dictionary containing intent and parameters
        """
        # Simple rule-based intent extraction
        # In a real implementation, this would use the LLM for more sophisticated parsing
        
        # File operations
        if re.search(r"(create|make|new)\s+(file|document)", user_input, re.IGNORECASE):
            return {"intent": "create_file", "confidence": 0.8}
        elif re.search(r"(open|view|show|display)\s+file", user_input, re.IGNORECASE):
            return {"intent": "open_file", "confidence": 0.8}
        elif re.search(r"(delete|remove)\s+file", user_input, re.IGNORECASE):
            return {"intent": "delete_file", "confidence": 0.8}
        elif re.search(r"(move|copy)\s+file", user_input, re.IGNORECASE):
            return {"intent": "move_file", "confidence": 0.7}
        
        # Search operations
        elif re.search(r"(find|search|locate)\s+file", user_input, re.IGNORECASE):
            return {"intent": "search_files", "confidence": 0.9}
        elif re.search(r"(find|search)\s+for", user_input, re.IGNORECASE):
            return {"intent": "search_content", "confidence": 0.7}
        
        # System operations
        elif re.search(r"(system|os)\s+(status|info)", user_input, re.IGNORECASE):
            return {"intent": "system_info", "confidence": 0.8}
        
        # Default: general query
        else:
            return {"intent": "general_query", "confidence": 0.5}
